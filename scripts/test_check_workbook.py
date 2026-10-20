"""Regression tests with an original teaching fixture; stdlib only."""
import copy
import io
import json
import unittest
import zipfile
from pathlib import Path
from check_workbook import SCHEMA, check, read_workbook

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DATA = json.loads(SCHEMA.read_text(encoding="utf-8"))


def fixture():
    raw = json.loads((ROOT / "examples/rain-lantern.json").read_text(encoding="utf-8"))
    rows = {s["name"]: {i: row for i, row in enumerate(raw[s["name"]], 1)}
            for s in SCHEMA_DATA["sheets"]}
    rows["随机机制"][2] = ["试验骰", "测试数据，不是示例玩法", "测试时", "1", "6", "0"]
    rows["随机项结果区间"][2] = ["试验骰", "1", "3", "甲"]
    rows["随机项结果区间"][3] = ["试验骰", "4", "6", "乙"]
    return rows


class WorkbookChecks(unittest.TestCase):
    def setUp(self):
        self.x = fixture()

    def errors(self):
        return check(self.x, SCHEMA_DATA)["errors"]

    def test_valid_fixture(self):
        self.assertEqual(self.errors(), [])

    def test_original_example(self):
        raw = json.loads((ROOT / "examples/rain-lantern.json").read_text(encoding="utf-8"))
        rows = {s["name"]:dict(enumerate(raw[s["name"]], 1)) for s in SCHEMA_DATA["sheets"]}
        self.assertEqual(check(rows, SCHEMA_DATA)["errors"], [])

    def test_xlsx_reader_in_memory(self):
        # A one-sheet XML fixture tests parsing, not a distributable website template.
        data = io.BytesIO()
        ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        with zipfile.ZipFile(data, "w") as z:
            z.writestr("xl/workbook.xml", f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets><sheet name="测试" sheetId="1" r:id="rId1"/></sheets></workbook>')
            z.writestr("xl/_rels/workbook.xml.rels", '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
            z.writestr("xl/sharedStrings.xml", f'<sst xmlns="{ns}"><si><t>共享文本</t></si></sst>')
            z.writestr("xl/worksheets/sheet1.xml", f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>内联文本</t></is></c><c r="B1" t="s"><v>0</v></c><c r="C1"><v>42</v></c></row></sheetData></worksheet>')
        data.seek(0)
        self.assertEqual(read_workbook(data), {"测试":{1:["内联文本","共享文本","42"]}})

    def test_past_date_allowed(self):
        self.x["一次性剧情点"][2][2] = "001-01-01 00:00:00"
        self.assertEqual(self.errors(), [])

    def test_duplicate_entity(self):
        self.x["实体与属性"][99] = list(self.x["实体与属性"][2])
        self.assertTrue(any("重复实体属性键" in e for e in self.errors()))

    def test_overlapping_intervals(self):
        self.x["随机项结果区间"][3][1] = "3"
        self.assertTrue(any("区间重叠" in e for e in self.errors()))

    def test_unknown_mechanism(self):
        self.x["随机项结果区间"][2][0] = "不存在"
        self.assertTrue(any("找不到机制" in e for e in self.errors()))

    def test_headers(self):
        self.x["词条库"][1][0] = "错误"
        self.assertTrue(any("表头不匹配" in e for e in self.errors()))

    def test_visibility(self):
        self.x["实体与属性"][2][2] = "也许"
        self.assertTrue(any("是否玩家" in e for e in self.errors()))

    def test_required_question(self):
        self.assertTrue(check(self.x, SCHEMA_DATA, {"questions":[{"id":"q1","status":"pending"}]})["errors"])

    def test_optional_question(self):
        self.assertFalse(check(self.x, SCHEMA_DATA, {"questions":[{"id":"q1","required":False,"status":"deferred"}]})["errors"])

    def test_blank_rule(self):
        for value in (None, "", " \n\t"):
            with self.subTest(value=value):
                self.x["实体与属性"][2][7] = value
                self.assertTrue(any("属性规则为空" in e for e in self.errors()))

    def test_character_boundary(self):
        size = check(self.x, SCHEMA_DATA)["characters"]["total"]
        self.assertFalse(check(self.x, SCHEMA_DATA, max_characters=size)["errors"])
        self.assertTrue(check(self.x, SCHEMA_DATA, max_characters=size-1)["errors"])

    def test_character_basis(self):
        old = check(self.x, SCHEMA_DATA)["characters"]["total"]
        self.x["基本信息"][1000] = ["甲 \n", "123"]
        self.assertEqual(check(self.x, SCHEMA_DATA)["characters"]["total"]-old, 6)

    def test_utf16_limit(self):
        self.x["基本信息"][1000] = ["😀"*16384]
        self.assertTrue(any("32767" in e for e in self.errors()))
        self.x["基本信息"][1000] = ["甲"*32767]
        self.assertFalse(any("32767" in e for e in self.errors()))

    def test_negative_limit(self):
        with self.assertRaises(ValueError):
            check(self.x, SCHEMA_DATA, max_characters=-1)

    def test_sheet_order(self):
        self.x = dict(reversed(list(self.x.items())))
        self.assertTrue(any("工作表名称或顺序" in e for e in self.errors()))

    def test_missing_basic_field(self):
        self.x["基本信息"][2][0] = "错误"
        self.assertTrue(any("基本信息!A2" in e for e in self.errors()))

    def test_duplicate_event(self):
        self.x["一次性剧情点"][3] = list(self.x["一次性剧情点"][2])
        self.assertTrue(any("剧情点标题重复" in e for e in self.errors()))

    def test_no_mutation(self):
        before = copy.deepcopy(self.x)
        check(self.x, SCHEMA_DATA)
        self.assertEqual(self.x, before)


if __name__ == "__main__":
    unittest.main()
