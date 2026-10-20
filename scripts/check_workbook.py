"""Read-only validation for the 10-sheet story workbook. Python standard library only."""
import argparse
import collections
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
SCHEMA = Path(__file__).resolve().parents[1] / 'references' / 'schema.json'

def col_number(letters):
    result = 0
    for c in letters:
        result = result * 26 + ord(c) - 64
    return result

def read_workbook(path):
    """Return ordered sheets of row-number -> values; never evaluates cell formulas."""
    sheets = {}
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS):
                shared.append(''.join(t.text or '' for t in si.findall('.//s:t', NS)))
        relationships = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets = {r.attrib['Id']: r.attrib['Target'] for r in relationships}
        wb = ET.fromstring(z.read('xl/workbook.xml'))
        for sheet in wb.findall('s:sheets/s:sheet', NS):
            target = targets[sheet.attrib['{' + REL + '}id']]
            part = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl', target))
            if not part.startswith('xl/'):
                raise ValueError('Unexpected worksheet target: ' + target)
            rows = {}
            for row in ET.fromstring(z.read(part)).findall('s:sheetData/s:row', NS):
                values = {}
                for cell in row.findall('s:c', NS):
                    m = re.fullmatch(r'([A-Z]+)([0-9]+)', cell.attrib['r'])
                    if not m:
                        raise ValueError('Invalid cell address')
                    typ = cell.attrib.get('t', 'n')
                    v = cell.find('s:v', NS)
                    value = v.text if v is not None else None
                    if typ == 's' and value is not None:
                        value = shared[int(value)]
                    elif typ == 'inlineStr':
                        value = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
                    values[col_number(m[1])] = value
                if values:
                    rows[int(row.attrib['r'])] = [values.get(n) for n in range(1, max(values) + 1)]
            sheets[sheet.attrib['name']] = rows
    return sheets

def check(sheets, schema, state=None, max_characters=None):
    errors, warnings = [], []
    if max_characters is not None and (isinstance(max_characters, bool) or not isinstance(max_characters, int) or max_characters < 0):
        raise ValueError('字符上限须为非负整数')
    by_sheet = {}
    max_units = 0
    for name, rows in sheets.items():
        count = 0
        for n, row in rows.items():
            for column, value in enumerate(row, 1):
                if value is None:
                    continue
                text = str(value)
                count += len(text)
                units = len(text.encode('utf-16-le')) // 2
                max_units = max(max_units, units)
                if units > 32767:
                    errors.append(f'{name}第{n}行第{column}列：单元格超过32767个UTF-16代码单元')
        by_sheet[name] = count
    total = sum(by_sheet.values())
    if max_characters is not None and total > max_characters:
        errors.append(f'全表字符数{total}超过上限{max_characters}')
    expected = [s['name'] for s in schema['sheets']]
    if list(sheets) != expected:
        errors.append('工作表名称或顺序不符：应为 ' + '、'.join(expected))
    for spec in schema['sheets']:
        rows = sheets.get(spec['name'], {})
        headers = rows.get(spec['header_row'], [])
        if headers[:len(spec['headers'])] != spec['headers'] or any(v not in (None, '') for v in headers[len(spec['headers']):]):
            errors.append(spec['name'] + '：表头不匹配')
    for n, field in enumerate(schema['basic_fields'], start=2):
        row = sheets.get('基本信息', {}).get(n, [])
        if not row or row[0] != field:
            errors.append('基本信息!A' + str(n) + '：应为' + field)
    opening = sheets.get('固定开局选项', {}).get(1, [])
    if not opening or opening[0] != '固定开局描述':
        errors.append('固定开局选项!A1：应为固定开局描述')

    def records(name, start=2, size=0):
        for n, row in sheets.get(name, {}).items():
            if n >= start and any(v not in (None, '') for v in row):
                yield n, row + [None] * max(0, size - len(row))

    keys = set()
    for n, r in records('实体与属性', size=8):
        key = (r[0], r[1], r[4], r[5])
        if any(x in (None, '') for x in key):
            errors.append(f'实体与属性第{n}行：实体或属性键缺失')
        elif key in keys:
            errors.append(f'实体与属性第{n}行：重复实体属性键 {key}')
        keys.add(key)
        if r[7] is None or not str(r[7]).strip():
            errors.append(f'实体与属性第{n}行：属性规则为空')
        for idx in (2, 3):
            if r[idx] not in ('是', '否'):
                errors.append(f'实体与属性第{n}行：是否玩家/是否隐藏应为是或否')
    for name, column in [('词条库', 2), ('持续状态', 3)]:
        for n, r in records(name, size=column + 1):
            if r[column] not in ('是', '否'):
                errors.append(f'{name}第{n}行：可见性应为是或否')

    mechanisms = {}
    for n, r in records('随机机制', size=6):
        if not r[0] or r[0] in mechanisms:
            errors.append(f'随机机制第{n}行：名称为空或重复')
        mechanisms[r[0]] = r
        try:
            qty, sides = int(r[3]), int(r[4])
            if qty < 1 or sides < 1 or float(r[3]) != qty or float(r[4]) != sides:
                raise ValueError()
            float(r[5])
        except (ValueError, TypeError):
            errors.append(f'随机机制第{n}行：骰子数量/面数须为正整数，修正值须为数字')
    intervals = collections.defaultdict(list)
    for n, r in records('随机项结果区间', size=4):
        if r[0] not in mechanisms:
            errors.append(f'随机项结果区间第{n}行：找不到机制 {r[0]}')
        try:
            low, high = float(r[1]), float(r[2])
            if low > high:
                raise ValueError()
            intervals[r[0]].append((low, high, n))
        except (ValueError, TypeError):
            errors.append(f'随机项结果区间第{n}行：边界非法')
    for name, ranges in intervals.items():
        ranges.sort()
        max_high = None
        for low, high, n in ranges:
            if max_high is not None and low <= max_high:
                errors.append(f'随机项结果区间第{n}行：{name}的含边界区间重叠')
            max_high = high if max_high is None else max(max_high, high)
    for name in mechanisms:
        if name not in intervals:
            warnings.append(f'随机机制{name}没有结果区间：核对是否有其他明确判定规则')
    event_names = [r[0] for _, r in records('一次性剧情点', size=3)]
    for name, count in collections.Counter(event_names).items():
        if count > 1:
            errors.append(f'一次性剧情点标题重复：{name}')
    # Dates are deliberately not compared with start time: past dates may signal conditional triggering.
    for n, r in records('词条库', size=5):
        if not r[0] or r[1] in (None, ''):
            warnings.append(f'词条库第{n}行：标题或描述为空')
        try:
            order = int(r[3])
            if order < 0 or float(r[3]) != order:
                raise ValueError()
        except (ValueError, TypeError):
            errors.append(f'词条库第{n}行：显示顺序须为非负整数')
    if state is not None:
        for q in state.get('questions', []):
            if q.get('required', True) and q.get('status') in ('pending', 'deferred'):
                errors.append('定稿仍有必要待答问题：' + str(q.get('id', '?')))
    return {'errors': errors, 'warnings': warnings,
            'characters': {'total': total, 'by_sheet': by_sheet,
                           'limit': max_characters, 'max_cell_utf16_units': max_units,
                           'basis': '全部非空单元格储存值的Unicode字符数，含空白、表头及数字；不按Excel显示格式展开'},
            'sheet_count': len(sheets),
            'scope': '仅结构与基础字段检查；不证明世界观一致性、完整性或平台可运行性'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook')
    parser.add_argument('--state')
    parser.add_argument('--max-characters', type=int, help='全表字符数上限，含边界')
    parser.add_argument('--sheet')
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int, default=10)
    args = parser.parse_args()
    try:
        sheets = read_workbook(args.workbook)
        schema = json.loads(SCHEMA.read_text(encoding='utf8'))
        state = json.loads(Path(args.state).read_text(encoding='utf8')) if args.state else None
        result = check(sheets, schema, state, args.max_characters)
        if args.sheet:
            if args.sheet not in sheets:
                raise ValueError('工作表不存在：' + args.sheet)
            result['rows'] = {n: r for n, r in sheets[args.sheet].items() if args.start <= n <= args.end}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result['errors'] else 0
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(json.dumps({'errors': [str(exc)]}, ensure_ascii=False))
        return 2

if __name__ == '__main__':
    sys.exit(main())
