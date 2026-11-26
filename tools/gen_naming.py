#!/usr/bin/env python3
"""gen_naming.py —— 从 graph/naming.yaml 单一事实源重写 90-附录/02-速查表大全.md 的命名区块。
区块以 <!-- NAMING:BEGIN --> ... <!-- NAMING:END --> 标记；构造性幂等（重复运行输出不变）。
用法: python3 tools/gen_naming.py            # 写回速查表
      python3 tools/gen_naming.py --stdout   # 只打印结果，不改工作区（validate 用）
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


def render(text: str) -> str:
    block = visible_block()
    begin = text.find("<!-- NAMING:BEGIN -->")
    endmark = "<!-- NAMING:END -->"
    if begin == -1:
        return text.rstrip() + "\n\n" + block + "\n"
    end = text.find(endmark, begin) + len(endmark)
    return text[:begin] + block + text[end:]


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true", help="打印重写后的全文，不改文件")
    args = ap.parse_args(argv)
    target = root / "90-附录" / "02-速查表大全.md"
    s = render(target.read_text(encoding="utf-8"))
    if args.stdout:
        sys.stdout.write(s)
        return
    target.write_text(s, encoding="utf-8", newline="\n")
    print(f"命名区块已重写: {target}")


if __name__ == "__main__":
    main(sys.argv[1:])
