#!/usr/bin/env python3
"""gen_naming.py —— 从 graph/naming.yaml 单一事实源重写 90-附录/02-速查表大全.md 的命名区块。
区块以 <!-- NAMING:BEGIN --> ... <!-- NAMING:END --> 标记；构造性幂等（重复运行输出不变）。
用法: python tools/gen_naming.py  （在仓库根目录执行）
"""
import pathlib, sys
try:
    import yaml
except ImportError:
    sys.exit("需要 pyyaml: pip install pyyaml")

root = pathlib.Path(__file__).resolve().parent.parent
data = yaml.safe_load((root / "graph" / "naming.yaml").read_text(encoding="utf-8"))


def speed(n):
    mb = n["speed_mbit"]
    return f"{mb} Mbps" if mb < 1000 else f"{mb // 1000} Gbps"


def visible_block():
    lines = ["| 现行标识（USB-IF） | 规范名 | 旧称（已弃用传播名） | 标称速率 |", "|---|---|---|---|"]
    lines += [f"| {n['marketing']} | {n['spec']} | {'、'.join(n['legacy'])} | {speed(n)} |"
              for n in data["naming"]]
    return "<!-- NAMING:BEGIN -->\n" + "\n".join(lines) + "\n<!-- NAMING:END -->"


target = root / "90-附录" / "02-速查表大全.md"
s = target.read_text(encoding="utf-8")
block = visible_block()
begin = s.find("<!-- NAMING:BEGIN -->")
endmark = "<!-- NAMING:END -->"
if begin == -1:
    s = s.rstrip() + "\n\n" + block + "\n"
else:
    end = s.find(endmark, begin) + len(endmark)
    s = s[:begin] + block + s[end:]
target.write_text(s, encoding="utf-8", newline="\n")
print(f"命名区块已重写: {target}")
