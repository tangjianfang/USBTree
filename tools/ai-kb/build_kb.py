#!/usr/bin/env python3
"""从 USBTree 生成面向 AI 检索的 Markdown 知识库：每主题一个文件 + index.md + llms-full.md。

在仓库根目录运行：python3 tools/ai-kb/build_kb.py
原地覆盖 ai-kb/ 下的生成文件，保留手写的 ai-kb/README.md。
usbtree_commit 取最近一次改动所抽取原文的短哈希（工作区有未提交改动时加 -dirty）。提交本目录不会让该字段空转。
"""
import os, re, posixpath, datetime, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topics import TOPICS
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REPO = ROOT
OUT = os.path.join(ROOT, "ai-kb")
GH = "https://github.com/tangjianfang/USBTree/blob/main/"
os.makedirs(OUT, exist_ok=True)
for name in os.listdir(OUT):
    if name.endswith(".md") and name != "README.md":
        os.remove(os.path.join(OUT, name))

def source_commit(paths):
    """最近一次改动被抽取原文的提交。提交 ai-kb 自身不会让这个字段空转。"""
    log = subprocess.run(
        ["git", "-C", REPO, "log", "-1", "--format=%h", "--", *paths],
        capture_output=True, text=True, check=True)
    commit = log.stdout.strip() or subprocess.run(
        ["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", REPO, "status", "--porcelain", "--", *paths],
        capture_output=True, text=True, check=True).stdout.strip()
    return commit + ("-dirty" if dirty else "")

commit = source_commit(sorted({s for t in TOPICS for s in t["sources"]}))
src2kb = {s: t["id"] for t in TOPICS for s in t["sources"]}
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200d]")
NAV = re.compile(r"知识树位置|上一叶|下一叶|返回|父节点|前置|相邻叶子|规范缓存索引|下一篇|上一篇")

def fix_link(m, cur):
    text, href = m.group(1), m.group(2)
    if href.startswith(("http", "#", "mailto:")): return m.group(0)
    path, _, frag = href.partition("#")
    tgt = posixpath.normpath(posixpath.join(posixpath.dirname(cur), path))
    if tgt in src2kb: return f"[{text}]({src2kb[tgt]}.md)"
    return f"[{text}]({GH}{tgt})"

def clean(rel):
    s = open(os.path.join(REPO, rel), encoding="utf-8").read()
    s = re.sub(r"^---\n.*?\n---\n", "", s, flags=re.S)
    s = re.sub(r"^# .*\n", "", s, count=1, flags=re.M)
    out, skip, in_code, code_lang = [], False, False, ""
    lines = s.split("\n"); i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            if not in_code:
                in_code, code_lang = True, l[3:].strip()
                if code_lang == "mermaid" and i + 1 < len(lines) and lines[i+1].strip().startswith("mindmap"):
                    j = i + 1
                    while not lines[j].startswith("```"): j += 1
                    i = j + 1; in_code = False; continue
            else: in_code = False
            if not skip: out.append(l)
            i += 1; continue
        if not in_code:
            if re.match(r"^##\s+(相关节点|相关阅读|延伸阅读)", l): skip = True; i += 1; continue
            if re.match(r"^##\s", l): skip = False
            if skip: i += 1; continue
            if l.startswith(">") and NAV.search(l): i += 1; continue
            l = EMOJI.sub("", l)
            l = re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", lambda m: fix_link(m, rel), l)
            l = re.sub(r"^(#{2,5})(\s)", lambda m: "#" * min(len(m.group(1)) + 1, 6) + m.group(2), l)
        elif skip: i += 1; continue
        out.append(l); i += 1
    txt = "\n".join(out)
    txt = re.sub(r"\n{3,}", "\n\n", txt).strip()
    return txt

def yaml_list(xs): return "[" + ", ".join('"' + x.replace('"', '\\"') + '"' for x in xs) + "]"

titles = {t["id"]: t["title"] for t in TOPICS}; titles["index"] = "知识库索引"
files = []
for t in TOPICS:
    fm = ["---", f'id: {t["id"]}', f'title: "{t["title"]}"', f'topic: {t["topic"]}', f'level: {t["level"]}',
          f'keywords: {yaml_list(t["keywords"])}', "sources:"] + [f'  - path: "{s}"\n    url: "{GH}{s}"' for s in t["sources"]] + \
         [f'spec_refs: {yaml_list(t["specs"])}', f'related: {yaml_list(t["related"])}',
          f'usbtree_commit: {commit}', f'generated: {datetime.date.today().isoformat()}', "---"]
    body = [f'# {t["title"]}', "",
            f'> 层级 {t["level"]} · 主题 `{t["topic"]}` · 相关：' + "、".join(f'[{titles.get(r, r)}]({r}.md)' for r in t["related"]), ""]
    if t["facts"].strip():
        body += ["## 核心事实 Key Facts", "", "> 由维护者整理并与规范核对；与下方 USBTree 原文冲突时以本节为准。", "", t["facts"].strip(), ""]
    for s in t["sources"]:
        body += [f"## 原文：{s.rsplit('/',1)[-1][:-3]}", "", f"> Source: [{s}]({GH}{s})", "", clean(s), ""]
    txt = "\n".join(fm) + "\n\n" + "\n".join(body).rstrip() + "\n"
    open(os.path.join(OUT, t["id"] + ".md"), "w", encoding="utf-8").write(txt)
    files.append((t, txt))

TERMS = [("主机","Host"),("设备 / 功能","Device / Function"),("集线器","Hub"),("端点","Endpoint (EP)"),("管道","Pipe"),("接口","Interface"),("备用设置","Alternate Setting"),
("配置","Configuration"),("描述符","Descriptor"),("枚举","Enumeration"),("事务","Transaction"),("传输","Transfer"),("控制/批量/中断/同步传输","Control / Bulk / Interrupt / Isochronous"),
("帧 / 微帧","Frame (1 ms) / Microframe (125 µs)"),("数据翻转","Data Toggle"),("握手","Handshake"),("零长度包","Zero-Length Packet (ZLP)"),("复合设备","Composite Device"),
("接口关联描述符","Interface Association Descriptor (IAD)"),("事务转换器","Transaction Translator (TT)"),("挂起 / 恢复 / 远程唤醒","Suspend / Resume / Remote Wakeup"),
("报告描述符","Report Descriptor"),("顶层集合","Top-Level Collection (TLC)"),("供电方 / 受电方","Source / Sink"),("数据下行/上行端口","DFP / UFP"),("双角色端口","Dual-Role Port (DRP)"),
("功率数据对象","Power Data Object (PDO)"),("请求数据对象","Request Data Object (RDO)"),("替代模式","Alternate Mode"),("电子标签线缆","Electronically Marked Cable (E-marker)"),
("链路训练状态机","LTSSM"),("连接管理器","Connection Manager (CM)"),("隧道","Tunnel"),("主机控制器接口","xHCI / EHCI / OHCI / UHCI")]

idx = ["---", 'title: "USB 知识库索引（AI 参考）"', "topic: index", "level: 入门", 'keywords: ["USB","index","knowledge base","USBTree"]',
       f'source_repo: "https://github.com/tangjianfang/USBTree"', f"usbtree_commit: {commit}", f"generated: {datetime.date.today().isoformat()}", "---", "",
       "# USB 知识库索引（AI 参考）", "",
       "用途：供 AI 代理检索 USB（及相关 Type-C/PD、USB4、BLE-HID）技术事实。每个文件 = 一个主题；frontmatter 含 level、keywords、sources（USBTree 原文路径与 URL）、spec_refs、related。",
       "每个文件结构：`核心事实 Key Facts`（手工整理、已核对，含对 USBTree 原文的勘误）→ `原文：…`（USBTree 原文清洗版：去导航/emoji，链接改写为 KB 内链或 GitHub URL，保留表格、代码、Mermaid）。",
       "冲突处理优先级：官方规范 > 本库 Key Facts > USBTree 原文。`llms-full.md` 为全部文件按顺序拼接的单文件版本。", "",
       "## 文件列表", "", "| 文件 | 标题 | 层级 | 主题 | 关键词 |", "|---|---|---|---|---|"]
for t, _ in files:
    idx.append(f'| [{t["id"]}.md]({t["id"]}.md) | {t["title"]} | {t["level"]} | `{t["topic"]}` | {", ".join(t["keywords"][:8])} |')
idx += ["", "## 按问题找文件", "", "| 问题类型 | 先看 |", "|---|---|",
 "| 字段偏移/长度、描述符类型码 | 06-descriptors, 11-hid-core |", "| Setup 包、标准/类/厂商请求码 | 07-enumeration-requests, 11-hid-core, 14-cdc, 15-msc, 16-uvc |",
 "| PID、事务、toggle、帧 | 04-packets-transactions |", "| bInterval、回报率、带宽 | 05-transfer-types-bandwidth, 12-hid-devices |",
 "| 枚举失败、代码 43、dmesg 错误 | 50-debug-troubleshooting, 07-enumeration-requests |", "| Windows HID/WinUSB/KMDF API | 41-windows-driver, 11-hid-core |",
 "| PD 消息、PDO、EPR | 22-usb-pd |", "| Type-C 电阻、CC 时序 | 20-connectors-typec |", "| USB3 LTSSM、包格式 | 30-usb3-superspeed |", "| USB4 隧道 | 31-usb4 |",
 "| 固件 TinyUSB | 43-device-firmware |", "| BLE HOGP 与 USB HID 对应 | 60-usb-wireless-intersection |", "| 数值/时序速查 | 90-quick-reference |",
 "", "## 术语统一（中文 ↔ English）", "", "| 中文 | English |", "|---|---|"] + [f"| {a} | {b} |" for a, b in TERMS] + \
 ["", "## 已知 USBTree 原文勘误（已在对应 Key Facts 中更正）", "",
  "- `30-枝干-接口与供电/08-USBPD消息全表.md` 开篇仍写「PD 规范本体未缓存（门控下载）」，同页文末以及 `80-参考资料/README.md`、`skills/usb-spec-lookup/SKILL.md` 已登记 `usb-core/USB-PD-3.2-V1.2.zip`。→ 22-usb-pd",
  "- `90-附录/03-时序参数全表.md` §4 来源说明仍写「未缓存 USB PD 规范原文」，同表 tFirstSourceCap 行又写「PD 3.2 V1.2 已缓存」。→ 90-quick-reference", ""]
idx_txt = "\n".join(idx)
open(os.path.join(OUT, "index.md"), "w", encoding="utf-8").write(idx_txt)

full = ["# USB 知识库全文（llms-full）", "", f"> 由 kb/ 下 {len(files)+1} 个文件拼接；源：tangjianfang/USBTree@{commit}。每个主题以 `<!-- file: xxx.md -->` 分隔。", ""]
full += ["<!-- file: index.md -->", re.sub(r"^---\n.*?\n---\n", "", idx_txt, flags=re.S)]
for t, txt in files:
    full += ["", "---", "", f'<!-- file: {t["id"]}.md -->', txt.replace("](", "](") ]
open(os.path.join(OUT, "llms-full.md"), "w", encoding="utf-8").write("\n".join(full) + "\n")
print(len(files) + 2, "files written to", os.path.relpath(OUT, ROOT), "at", commit)

link_re = re.compile(r"\]\(([^)#\s][^)\s]*)\)")
missing = []
for name in sorted(os.listdir(OUT)):
    if not name.endswith(".md") or name == "llms-full.md":
        continue
    text = open(os.path.join(OUT, name), encoding="utf-8").read()
    for m in link_re.finditer(text):
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        path = href.split("#", 1)[0]
        if path and not os.path.exists(os.path.normpath(os.path.join(OUT, path))):
            missing.append(f"{name} -> {href}")
if missing:
    print(f"kb relative links missing: {len(missing)}")
    for item in missing[:40]:
        print(" ", item)
    sys.exit(1)
