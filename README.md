# 中文词汇识记游戏——防空战（词汇可替换）

开发者：微信公众号“洞观中文”。

GitHub 仓库名：`chinese-vocab-air-defense`。Codex Skill 调用名：`$textbook-vocab-game`。

把教材或自编词汇表中的生词和发音放入四关闯关游戏。每次只需提供词汇表截图和配套录音，Codex 使用内置 HTML 模板生成新的单文件游戏；没有录音时，可使用本机系统中文语音。

适合国际学校、海外中文课堂、对外汉语教师。

## 它做什么

| 项目 | 说明 |
| --- | --- |
| 游戏形态 | 单文件 HTML，打字 / 朗读闯关，共 4 关 |
| 训练维度 | 听、识、读、写（电写） |
| 技能工作 | 提取生词，切分教材原声，注入游戏模板并按截图标题命名 |
| 修改范围 | 游戏逻辑一行不动，只替换 `WORDS` / `WORD_EN` / `WORD_AUDIO` 三张表 |

## 四关结构

| 关卡 | 屏幕呈现 | 学生产出 | 考察 |
| --- | --- | --- | --- |
| 1 | 汉字 + 拼音 | 打字 | 听辨、识字、写字（电写） |
| 2 | 仅汉字 | 打字 | 识字、拼音、打字（电写） |
| 3 | 汉字 + 拼音 | 读词 | 识字、拼音识读、说（发音） |
| 4 | 仅汉字 | 读词 | 识字、发音 |

详细设计见 [design.md](textbook-vocab-game/references/design.md)。电写指键盘输入，不是手写笔画训练。

## 在 Codex 中使用

将仓库内的 `textbook-vocab-game` 文件夹放入 Codex 个人技能目录（通常是 `~/.codex/skills/`）；自定义了 CODEX_HOME 时使用该目录下的 `skills/`。已有同名技能时先保留备份。重新打开 Codex，让它发现新技能。

上传本课词汇表截图和录音，输入：

> 使用 $textbook-vocab-game 更新本课词汇游戏。

没有录音时，注明“使用系统中文发音”。技能会根据截图标题命名输出，并内嵌全部发音。截图不清楚或录音缺词时，会指出具体需要补充的内容。

## 提取规则

只收独立生词和旁注，不收课文句子中的普通词。统一简体，去掉拼音、词性、英文和括注；跨图去重、最长优先，再按首次出现顺序排列。例如有“耳环”就不另列“环”，有“人民币”就不另列“人民”和“币”。

## 学生怎样玩

学生只需拿到生成的 HTML 文件，使用浏览器打开。发音已内嵌，无须另发 MP3 文件。键盘玩法和内嵌朗读可离线使用；语音识别关卡取决于浏览器支持、麦克风授权及网络条件。

## 独立模板和其他 AI

[chinese-vocab-air-defense.html](chinese-vocab-air-defense.html) 是可直接下载、用浏览器打开的独立游戏文件，不依赖 Codex 或 Python。相同模板也保存在 Skill 的 `assets/game-template.html` 中。

也可以把 HTML、词汇截图和录音交给其他具备音频处理能力的 AI，配合 [修改提示](textbook-vocab-game/references/other-ai-prompt.md) 使用。

## 文件与运行依赖

- [SKILL.md](textbook-vocab-game/SKILL.md)：完整执行流程。
- `agents/openai.yaml`：中文显示名称及调用提示。
- `assets/game-template.html`：用户提供的独立 HTML 模板。
- `scripts/cut_audio.py`：按核对后的时间裁剪录音，并检查静音及来源区间。
- `scripts/build_game.py`：只更新三张表，检查其余内容逐字不变。
- [audio-and-html.md](textbook-vocab-game/references/audio-and-html.md)：清单格式与运行方法。

生成过程需要 Python、FFmpeg，以及当前环境中可用的转写工具；无录音时需要本机可用的中文语音引擎。Skill 不包含大体积转写模型。其他 AI 工具是否能完成切音频，取决于其实际能力。

## 发布到 GitHub

创建名为 `chinese-vocab-air-defense` 的仓库，将本目录内的 README.md、.gitignore、chinese-vocab-air-defense.html 和 textbook-vocab-game 文件夹上传到仓库根目录。发布包不包含账号凭据或本地工作文件。
