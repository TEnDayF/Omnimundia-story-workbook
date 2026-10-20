# Omnimundia：story-workbook

**面向 [Omnimundia](https://omnimundia.cn/) 创作者的 AI 剧本制作 Skill：把世界观、角色与玩法设定，整理成供平台 AI 推演的互动文字冒险剧本。**

Omnimundia 是一个 **AI 互动阅读平台**，以“世界树”为核心，由剧本驱动 AI 推演故事。玩家每回合可以选择选项，也可以自由输入自己的想法；通过保存和读取世界线，从已有存档继续探索新的走向。数值、关系和行动结果会影响后续故事。平台定位与玩法见官网的[关于 Omnimundia](https://omnimundia.cn/about)。

在这样的玩法下，创作者需要给 AI 提供可持续推演的世界：世界如何运转、角色知道什么、行动如何改变状态，以及事件何时发生。`story-workbook` 用于辅助这一制作过程：让支持 Skill 的 AI 助手按需追问设定、组织信息、检查矛盾，并依据用户从网站导出的 Excel 模板填写或修订剧本，为玩家的自由决策和不同世界线留下空间。

## 它能帮你做什么

- **从设定开始制作剧本**：梳理世界规则、主控身份和开局，只询问影响交付的关键缺口。
- **让行动产生后果**：组织角色属性、物品、关系、事件条件及分支承接，给 AI 推演提供依据。
- **管理玩家知道的信息**：区分公开状态、待解锁词条与后台规则，检查提前泄露真相的问题。
- **修改已有剧本**：调整开局、角色替换、文风和篇幅，同时核对引用与前后因果。
- **检查制作结果**：附带十表结构校验脚本，并区分文本检查、文件检查和网站实际试玩。

## 使用流程

**从 Omnimundia 导出模板 → 把模板与设定交给 AI 助手 → 调用 Skill 制作或修订 → 检查结果 → 回到网站导入并试玩。**

**Excel 模板请自行到 [Omnimundia](https://omnimundia.cn/) 导出。本仓库不提供 Excel 模板或示例工作簿。**

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

## 许可与署名

Copyright © 2026 TEnDayF。

除另有标注的第三方内容外，本仓库由维护者有权授权的内容，包括 Skill、参考文档、示例及附带脚本，采用 **[CC BY-NC-SA 4.0（署名—非商业性使用—相同方式共享）](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)**。完整条款见 [LICENSE](LICENSE)。

分享本 Skill 或其改编版本时，请署名 **TEnDayF**，保留来源与许可证链接，标明修改，并遵守非商业及相同方式共享条件。这是带非商业限制的共享许可，不宣称是开源软件许可证。

建议署名方式：

> Omnimundia：story-workbook — TEnDayF；来源：https://github.com/TEnDayF/Omnimundia-story-workbook ；CC BY-NC-SA 4.0。若有修改，请补充修改说明。

**使用本 Skill 创作的剧本不因使用本 Skill 而受本仓库许可证约束，也无需向 TEnDayF 或本 Skill 署名。** 用户自行决定其剧本的发布、署名和许可方式。直接复制或改编仓库内受保护的示例、文档或代码，相关复制／改编部分仍适用对应许可；其他素材与网站的权利不由本仓库授予。

## 反馈与维护

接受 Issue 和 Pull Request，是否合并由维护者 **TEnDayF** 决定；不承诺处理所有建议。
本项目按需维护，不保证响应时间或固定更新频率。贡献说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。

本 Skill 面向 [Omnimundia](https://omnimundia.cn/)，未声明网站官方背书。来源与授权范围见 [分享说明](docs/SHARING.md)。
