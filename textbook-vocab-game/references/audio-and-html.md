# 发音与三表注入

先发现当前环境的转写工具、Python、FFmpeg 和系统中文语音。复用已有工具；确需下载时遵守当前权限，不依赖创建 Skill 时的机器绝对路径。

## 词汇清单

UTF-8 JSON，代理根据本次截图和录音建立；每词一项，顺序为提取顺序：

```json
{"words": [{"word": "耳环", "pinyin": "ěr huán", "english": "earrings", "audio": "01_耳环.mp3", "start": 20.08, "end": 21.33}]}
```

示例时间只表示格式，不能用于新录音。`start/end` 为最终裁剪起止秒数。无录音而生成系统发音时可省略时间字段，audio 仍指向真实 MP3。

## 原声定位与裁剪

先由可用转写工具取得词/段时间戳，再结合源录音及波形校准边界；独立词优先，勿包含序号。通常留 80–150 毫秒边界余量，词间紧密时按实际情况裁剪。注意合适/适合及长短词的区别，不用音节拼接造词。

```sh
python3 <skill>/scripts/cut_audio.py --manifest work/lesson.json --source <recording> --out-dir work/clips --ffmpeg <ffmpeg>
```

脚本仅使用 Python 标准库及 FFmpeg，可从 PATH 或 imageio_ffmpeg 查找。使用输入侧 seek 并重置滤镜时间戳，避免先给全录音淡出再裁剪而得到无声 MP3。解码检查非静音，并与原区间比较；这不能代替对词语身份的核对。多个录音可分别建立子清单，将切片收集到同一目录。

## 无录音：系统中文语音

明确没有录音时，优先使用操作系统可用的中文语音，例如 macOS 的 `say`，先查询实际可用声音，选择中文语音而不猜名称；逐词导出到 work/ 的 AIFF/WAV，再用 FFmpeg 转为 MP3。其他操作系统可用本地安装的中文语音引擎。把这些 MP3 放进清单指定的文件名，注明“系统合成发音”。没有可用中文声音就说明并请补录音，不擅自改游戏或调用外部收费服务。

对生成的系统音频也执行 `check_clip` 非静音检查（从 cut_audio.py 导入），避免导出空文件。不要以此声称是教材原声。

## 生成

```sh
python3 <skill>/scripts/build_game.py --manifest work/lesson.json --clips-dir work/clips --output outputs/词汇防空战_第3课_买礼物_生词1.html
```

默认使用相对 Skill 目录的 assets/game-template.html。用户明确提供新模板时加 `--template <html>`。脚本接受本模板的 JSON 数据表，不执行上传文件内的任意脚本；模板三表不是合法 JSON 时停止并说明结构不兼容，不重写游戏。

脚本内嵌所有音频、核对最长优先及重复词，并保证三表以外逐字一致。仅命名输出文件，不修改内部标题、词数静态占位、拼音映射、TTS_WORDS 或示例词。运行时词库数量由原模板逻辑决定。如原模板在特殊新词上存在语音匹配限制，应如实说明，不扩大修改范围。
