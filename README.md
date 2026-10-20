# Omnimundia：story-workbook

**一个专门给 [Omnimundia](https://omnimundia.cn/) 网站制作、整理和修订剧本 Excel 的 AI Skill。**

适用于支持 `SKILL.md` 的 AI 助手。它帮助你把原创设定或现有剧本整理成网站所用的十工作表格式，处理开局、角色属性、隐藏信息、剧情点、词条和篇幅等问题。

**Excel 模板请自行到 [Omnimundia 网站](https://omnimundia.cn/) 导出。本仓库不提供 Excel 模板或示例工作簿。**

## 安装

1. 点击本仓库 **Code → Download ZIP**，或克隆仓库。
2. 将解压后的仓库根目录重命名为 `story-workbook`，确保 `SKILL.md` 直接位于该目录内。
3. 放入 AI 助手支持的技能目录。在 Codex 中通常为 `$CODEX_HOME/skills/story-workbook`；未自定义 CODEX_HOME 时为 `~/.codex/skills/story-workbook`。
4. 重新加载技能或重启助手。已有同名技能时先备份、比较版本再替换。

其他助手请按其技能安装方式操作；本仓库不包含自动安装器。

## 怎么用

先到 Omnimundia 导出最新 Excel 模板，随后把模板和设定交给助手，例如：

> 使用 $story-workbook，按我从 Omnimundia 导出的模板制作剧本。以下是我的设定……
> 沿用已确认的要求，只问影响交付的必要问题；完成后交付 Excel，并说明做过哪些检查。

也可以要求：

- 检查现有剧本的属性、剧情点和词条是否互相矛盾。
- 调整开局和角色替换，保持已有世界规则。
- 修正可见信息中的剧透，区分固定知识与变化状态。
- 在指定字符数内压缩剧本，保留必要因果和玩法。

Skill 的制作规则会按任务读取，不需要你逐一阅读全部参考文档。

## 附带内容

- [SKILL.md](SKILL.md)：技能入口与制作流程。
- `references/`：十表结构、访谈、信息归属、叙事和验收方法。
- `agents/openai.yaml`：技能显示名称及调用提示。
- `scripts/check_workbook.py`：可选的 Excel 结构校验脚本，Python 3.10+，仅用标准库。
- [原创 JSON 示例](examples/rain-lantern.json)：供理解写法，不是网站导入模板。

需要单独校验自己的 Excel 时，在仓库根目录运行：

```sh
python scripts/check_workbook.py path/to/your-story.xlsx
```

可添加 `--max-characters 50000` 指定全表字符上限；数字仅为示例，非网站默认上限。
开发者回归检查：`python -m unittest discover -s scripts -p "test_*.py" -v`。

## 使用范围

本 Skill 面向 Omnimundia 网站，未声明网站官方背书。网站模板和功能可能变化，请以你实际导出的最新模板为准；附带 schema 只是本版本校验规则，出现差异时先核对，不要强改网站模板去迎合脚本。
结构校验不证明剧情正确、隐藏信息不泄漏或网站实际运行成功。导入、保存回读和试玩需在网站内另行验证。本版本尚未完成网站实测，详见 [验证说明](docs/VALIDATION.md)。

离线使用 Skill 不需要配置 Omnimundia API Key；上传和试玩按网站正常登录流程操作。Skill 不会自动启动游玩。

## 许可

当前分享源文件，暂未指定开源许可证。除平台条款允许的行为外，不据此授予额外的使用、修改或分发许可；后续由维护者明确授权范围。来源说明见 [分享说明](docs/SHARING.md)。
