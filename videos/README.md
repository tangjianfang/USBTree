# videos/ · USBTree 代码视频

用 [Manim Community Edition](https://www.manim.community/)（Python）把核心知识点写成动画。每个视频都是一份可读、可改、可复现的源码：画面里的数值、时序和字节都按官方规范原文核对，片尾列出章节号；只有主机实现差异（例如“先读 64 字节”）会在字幕里注明“非规范要求”。

在线观看：<https://usbtree.gumuhub.com/videos/>（也嵌在对应的知识树正文里）。

| # | 视频 | 场景源码 | 旁白 / 字幕稿 | 嵌入页面 |
|---|---|---|---|---|
| 01 | USB 枚举全过程 | [scenes/s01_enumeration.py](scenes/s01_enumeration.py) | [scripts/01-enumeration.md](scripts/01-enumeration.md) | [08-枚举流程与标准请求](../10-树干-USB核心/08-枚举流程与标准请求.md) |
| 02 | 包、事务与数据切换 | [scenes/s02_packets.py](scenes/s02_packets.py) | [scripts/02-packets.md](scripts/02-packets.md) | [05-包格式与事务](../10-树干-USB核心/05-包格式与事务.md) |
| 03 | 四种传输类型与帧调度 | [scenes/s03_transfers.py](scenes/s03_transfers.py) | [scripts/03-transfers.md](scripts/03-transfers.md) | [06-四种传输类型](../10-树干-USB核心/06-四种传输类型.md)、[13-总线带宽与调度计算](../10-树干-USB核心/13-总线带宽与调度计算.md) |
| 04 | HID 报告描述符解析 | [scenes/s04_hid_report.py](scenes/s04_hid_report.py) | [scripts/04-hid-report.md](scripts/04-hid-report.md) | [02-报告描述符与Item编码](../20-枝干-设备类协议/HID-人机接口设备/02-报告描述符与Item编码.md)、[06-鼠标详解](../20-枝干-设备类协议/HID-人机接口设备/06-鼠标详解.md) |
| 05 | Type-C CC 检测与 PD 协商 | [scenes/s05_typec_pd.py](scenes/s05_typec_pd.py) | [scripts/05-typec-pd.md](scripts/05-typec-pd.md) | [04-USBPD协议](../30-枝干-接口与供电/04-USBPD协议.md)、[02-USBType-C详解](../30-枝干-接口与供电/02-USBType-C详解.md) |
| 06 | NRZI 编码与位填充 | [scenes/s06_nrzi.py](scenes/s06_nrzi.py) | [scripts/06-nrzi.md](scripts/06-nrzi.md) | [04-信号编码与比特流](../10-树干-USB核心/04-信号编码与比特流.md) |

## 目录

```
videos/
├── videos.yaml        视频清单：id、场景类、封面时间、嵌入页面、摘要、规范出处（render.sh 与站点共用）
├── usbstyle.py        共享样式：配色（与站点深色主题一致）、字体、字幕条、章节标签、片头片尾、时序图 / 状态条组件
├── scenes/            每个主题一个场景文件
├── scripts/           每个视频的旁白 / 字幕稿与规范核对表
├── render.sh          渲染 + 压缩 + 封面 + 字幕 → site/public/videos/
├── cues2vtt.py        场景运行时记录的字幕时间轴 → WebVTT；汇总 manifest.json
├── requirements.txt
└── out/               中间产物（gitignore）
```

成品放在 `site/public/videos/<id>.{mp4,png,thumb.jpg,vtt}` 与 `manifest.json`，**随仓库提交**，站点构建时原样发布，CI 不需要渲染。

## 渲染

```bash
# Debian / Ubuntu
sudo apt-get install -y ffmpeg fonts-noto-cjk libcairo2-dev libpango1.0-dev pkg-config
python3 -m venv .venv && . .venv/bin/activate
pip install -r videos/requirements.txt

videos/render.sh                         # 全部（1920×1080 · 30 fps · H.264 CRF 30）
videos/render.sh 05-typec-pd             # 只渲染一个
QUALITY=draft videos/render.sh 02-packets  # 480p 草稿，输出到 videos/out/，不覆盖站点文件
WEBM=1 videos/render.sh                  # 额外生成 VP9 WebM（默认不生成，站点只用 MP4）
```

- 不需要 LaTeX：文字全部用 `Text` / `MarkupText`（Pango）渲染。中文字体 Noto Sans CJK SC；等宽字体 JetBrains Mono，缺失时 Pango 会自动回退。
- 每个视频目标 2–5 MB（上限 8 MB）。超了就调高 `CRF`（如 `CRF=32 videos/render.sh …`）。
- 字幕：`USBScene.say()` 在切换底部字幕时记录时间，渲染结束写出 `out/<id>.cues.json`，`render.sh` 再转成 WebVTT。画面里已经烧录了字幕，所以站点的 `<track>` 默认关闭，只供读屏和搜索用。
- 发布：渲染后正常提交 `site/public/videos/` 的改动，站点按 [site/README.md](../site/README.md) 构建 / 部署即可。

## 新增一个视频

1. 在 `scenes/` 新建 `sNN_xxx.py`，继承 `usbstyle.USBScene`，设好 `TITLE` / `SLUG`；用 `intro()`、`chapter()`、`say()`、`outro([...出处])` 组织画面。
2. 在 `videos.yaml` 加一条：`pages` 写要嵌入的知识树正文（仓库相对路径），`specs` 写规范章节。
3. `QUALITY=draft videos/render.sh <id>` 看草稿，用 ffmpeg 抽帧检查重叠、裁切、缺字（豆腐块）；没问题再正式渲染。
4. 在 `scripts/` 写旁白稿和“规范核对表”，每个数字都要能对到规范原文的章节 / 表号；查不到的标 **待核实**。

## 许可

视频与脚本遵循本仓库的 MIT 许可证（见 [LICENSE](../LICENSE)）。
