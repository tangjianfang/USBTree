"""04 · HID 报告描述符解析：启动鼠标（HID 1.11 §6.2.2、附录 B.2、附录 E.10）"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from manim import *  # noqa: F401,F403
from usbstyle import *  # noqa: F401,F403

KIND_COLOR = {"Main": TEAL, "Global": BLUE, "Local": AMBER}

# HID 1.11 附录 E.10 Report Descriptor (Mouse)，按原文顺序
ITEMS = [
    ("05 01", "Usage Page (Generic Desktop)", "Global"),
    ("09 02", "Usage (Mouse)", "Local"),
    ("A1 01", "Collection (Application)", "Main"),
    ("09 01", "  Usage (Pointer)", "Local"),
    ("A1 00", "  Collection (Physical)", "Main"),
    ("05 09", "    Usage Page (Buttons)", "Global"),
    ("19 01", "    Usage Minimum (1)", "Local"),
    ("29 03", "    Usage Maximum (3)", "Local"),
    ("15 00", "    Logical Minimum (0)", "Global"),
    ("25 01", "    Logical Maximum (1)", "Global"),
    ("95 03", "    Report Count (3)", "Global"),
    ("75 01", "    Report Size (1)", "Global"),
    ("81 02", "    Input (Data,Var,Abs)", "Main"),
    ("95 01", "    Report Count (1)", "Global"),
    ("75 05", "    Report Size (5)", "Global"),
    ("81 01", "    Input (Constant)", "Main"),
    ("05 01", "    Usage Page (Generic Desktop)", "Global"),
    ("09 30", "    Usage (X)", "Local"),
    ("09 31", "    Usage (Y)", "Local"),
    ("15 81", "    Logical Minimum (-127)", "Global"),
    ("25 7F", "    Logical Maximum (127)", "Global"),
    ("75 08", "    Report Size (8)", "Global"),
    ("95 02", "    Report Count (2)", "Global"),
    ("81 06", "    Input (Data,Var,Rel)", "Main"),
    ("C0", "  End Collection", "Main"),
    ("C0", "End Collection", "Main"),
]


class HidReport(USBScene):
    TITLE = "HID 报告描述符解析"
    SLUG = "04-hid-report"

    def construct(self):
        self.intro("HID 报告描述符解析", "以规范附录里的启动鼠标为例：50 个字节如何变成 3 字节报告")

        # ── 1 字节流 ──
        self.chapter("50 个字节", 1)
        allhex = " ".join(h for h, _, _ in ITEMS).split()
        grid = VGroup(*[M(b, size=24, color=FG) for b in allhex]).arrange_in_grid(rows=4, cols=13, buff=(0.32, 0.3)).move_to([0, 0.6, 0])
        self.say("这是 HID 1.11 附录 E.10 给出的鼠标报告描述符，一共 50 个字节")
        self.play(LaggedStart(*[FadeIn(b) for b in grid], lag_ratio=0.02), run_time=1.6)
        cnt = T(f"{len(allhex)} 字节 · 26 个 Item", size=22, color=MUTED).next_to(grid, DOWN, buff=0.4)
        self.play(FadeIn(cnt))
        self.wait(0.6)

        # ── 2 前缀字节 ──
        self.chapter("短 Item 的前缀字节", 2)
        self.say("每个短 Item 的第一个字节是前缀：bTag 4 位、bType 2 位、bSize 2 位")
        first = grid[0].copy()
        self.play(FadeOut(grid[1:]), FadeOut(cnt), first.animate.move_to([-4.8, 1.6, 0]).scale(1.6), FadeOut(grid[0]))
        bits = VGroup(*[chip(b, c, size=26, mono=True) for b, c in zip("00000101", [PURPLE] * 4 + [BLUE] * 2 + [GREEN] * 2)]).arrange(RIGHT, buff=0.08).move_to([0.6, 1.6, 0])
        arr = Arrow(first.get_right(), bits.get_left(), buff=0.2, color=MUTED, stroke_width=2.5)
        self.play(GrowArrow(arr), FadeIn(bits, shift=RIGHT * 0.2))
        l1 = T("bTag = 0000", size=20, color=PURPLE).next_to(bits[:4], DOWN, buff=0.2)
        l2 = T("bType = 01", size=20, color=BLUE).next_to(bits[4:6], DOWN, buff=0.2)
        l3 = T("bSize = 01", size=20, color=GREEN).next_to(bits[6:], DOWN, buff=0.2)
        l2.shift(DOWN * 0.42)
        self.play(FadeIn(l1), FadeIn(l2), FadeIn(l3))
        expl = VGroup(
            T("bType：0 = Main　1 = Global　2 = Local", size=22, color=FG),
            T("bSize：0/1/2/3 → 后跟 0/1/2/4 字节数据", size=22, color=FG),
            T("0x05 = Global 类、Tag 0 → Usage Page，数据 0x01 = Generic Desktop", size=22, color=TEAL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([0, -1.3, 0])
        self.say("bType 区分 Main、Global、Local 三类；bSize 说明后面跟几个数据字节")
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.1) for e in expl], lag_ratio=0.3), run_time=1.6)
        self.wait(1.2)
        self.clear_stage()

        # ── 3 逐条解析 ──
        self.chapter("逐条解析", 3)
        self.say("解析器自上而下读 Item：Global 更新全局状态，Local 只对下一个 Main 有效")
        left = panel(6.6, 5.2).move_to([-3.45, -0.15, 0])
        right = panel(6.0, 2.75).move_to([3.55, 1.08, 0])
        self.play(FadeIn(left), FadeIn(right))
        legend = VGroup(*[chip(k, c, size=16) for k, c in KIND_COLOR.items()]).arrange(RIGHT, buff=0.15).next_to(left, UP, buff=0.08).align_to(left, RIGHT)
        self.play(FadeIn(legend))

        # 状态表
        keys = ["Usage Page", "Logical Min/Max", "Report Size", "Report Count", "Usage（Local）"]
        st_k = VGroup(*[T(k, size=18, color=MUTED) for k in keys]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        st_k.move_to(right).align_to(right, LEFT).shift(RIGHT * 0.3)
        st_title = T("解析器状态", size=20, color=TEAL, weight="BOLD").next_to(right, UP, buff=0.08).align_to(right, LEFT)
        vals = {k: M("—", size=18, color=FG).next_to(st_k[i], RIGHT, buff=0.4).set_x(right.get_x() + 1.2, LEFT) for i, k in enumerate(keys)}
        for i, k in enumerate(keys):
            vals[k].align_to(right.get_center() + RIGHT * 0.3, LEFT)
        self.play(FadeIn(st_title), FadeIn(st_k), *[FadeIn(v) for v in vals.values()])

        # 报告位图（3 字节）
        cell_w = 0.42
        cells = VGroup(*[Square(cell_w, stroke_color=HAIR, stroke_width=1.5) for _ in range(24)]).arrange(RIGHT, buff=0)
        cells.move_to([3.55, -1.55, 0]).scale_to_fit_width(5.9)
        bylab = VGroup(*[T(f"字节 {i}", size=15, color=MUTED).next_to(cells[i * 8: i * 8 + 8], UP, buff=0.06) for i in range(3)])
        rep_t = T("输入报告位图（每字节低位在左）", size=18, color=TEAL).next_to(cells, DOWN, buff=0.15)
        self.play(Create(cells), FadeIn(bylab), FadeIn(rep_t), run_time=0.8)

        def setv(k, s):
            nv = M(s, size=18, color=FG).move_to(vals[k]).align_to(vals[k], LEFT)
            self.play(Transform(vals[k], nv), run_time=0.25)

        def fill(start, n, color, label):
            r = Rectangle(width=cells[0].width * n, height=cells[0].height, stroke_width=0, fill_color=color, fill_opacity=0.6)
            r.align_to(cells[start], LEFT).set_y(cells.get_y())
            t = T(label, size=14, color=FG)
            if t.width > r.width - 0.04:
                t.scale_to_fit_width(r.width - 0.04)
            t.move_to(r)
            self.play(FadeIn(VGroup(r, t), scale=0.9), run_time=0.5)

        chunks = [(0, 5), (5, 13), (13, 16), (16, 24), (24, 26)]
        lines = None
        for ci, (a, b) in enumerate(chunks):
            rows = VGroup()
            for h, txt, kind in ITEMS[a:b]:
                hx = M(h.ljust(5), size=18, color=KIND_COLOR[kind])
                tx = M(txt, size=18, color=FG)
                rows.add(VGroup(hx, tx).arrange(RIGHT, buff=0.35))
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            if rows.width > 6.2:
                rows.scale_to_fit_width(6.2)
            rows.move_to(left).align_to(left, UP).align_to(left, LEFT).shift(DOWN * 0.3 + RIGHT * 0.25)
            if ci == 0:
                self.say("先声明用途：Generic Desktop 页里的 Mouse，再开 Application 和 Physical 两层集合")
            elif ci == 1:
                self.say("三个按键：每个 1 位、取值 0/1，Report Count 3 × Report Size 1")
            elif ci == 2:
                self.say("再补 5 个常量位，把按键凑成完整的 1 个字节")
            elif ci == 3:
                self.say("X、Y 各 8 位，取值 −127～127，Input 标记为相对量")
            else:
                self.say("两个 End Collection 收尾，描述符结束")
            if lines is not None:
                self.play(FadeOut(lines), run_time=0.3)
            self.play(FadeIn(rows), run_time=0.4)
            lines = rows
            for i, (h, txt, kind) in enumerate(ITEMS[a:b]):
                hl = SurroundingRectangle(rows[i], color=KIND_COLOR[kind], buff=0.05, stroke_width=2)
                self.play(Create(hl), run_time=0.22)
                t = txt.strip()
                if t.startswith("Usage Page"):
                    setv("Usage Page", t[len("Usage Page ("):-1])
                elif t.startswith("Usage Min"):
                    setv("Usage（Local）", "Button 1…")
                elif t.startswith("Usage Max"):
                    setv("Usage（Local）", "Button 1…3")
                elif t.startswith("Usage ("):
                    cur = vals["Usage（Local）"].text if hasattr(vals["Usage（Local）"], "text") else ""
                    v = t[len("Usage ("):-1]
                    setv("Usage（Local）", "X, Y" if v == "Y" else v)
                elif t.startswith("Logical Min"):
                    self._lmin = t[len("Logical Minimum ("):-1]
                elif t.startswith("Logical Max"):
                    setv("Logical Min/Max", f"{self._lmin} … {t[len('Logical Maximum ('):-1]}")
                elif t.startswith("Report Size"):
                    setv("Report Size", t[len("Report Size ("):-1])
                elif t.startswith("Report Count"):
                    setv("Report Count", t[len("Report Count ("):-1])
                elif t.startswith("Input"):
                    if h == "81 02":
                        for k in range(3):
                            fill(k, 1, AMBER, f"B{k + 1}")
                    elif h == "81 01":
                        fill(3, 5, HAIR, "常量填充")
                    else:
                        fill(8, 8, BLUE, "X（相对）")
                        fill(16, 8, PURPLE, "Y（相对）")
                if kind == "Main":
                    setv("Usage（Local）", "—（已清空）")
                self.play(FadeOut(hl), run_time=0.15)
        self.wait(0.6)
        self.say("每个 Main Item 之后 Local 状态清空，Global 状态一直保留到被改写")
        self.wait(0.8)
        self.clear_stage()

        # ── 4 实际报告 ──
        self.chapter("读一条真实报告", 4)
        rep = VGroup(*[chip(b, c, size=36, mono=True) for b, c in [("01", AMBER), ("05", BLUE), ("FB", PURPLE)]]).arrange(RIGHT, buff=0.4).move_to([-3.2, 1.0, 0])
        self.say("设备发来 3 个字节：01 05 FB")
        self.play(FadeIn(rep, shift=DOWN * 0.2))
        dec = VGroup(
            T("字节 0 = 0000 0001 → 按键 1 按下", size=24, color=AMBER),
            T("字节 1 = 0x05 → X 向右移动 5", size=24, color=BLUE),
            T("字节 2 = 0xFB → 补码 −5 → Y 向上移动 5", size=24, color=PURPLE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([-2.4, -1.0, 0])
        self.play(LaggedStart(*[FadeIn(d, shift=RIGHT * 0.2) for d in dec], lag_ratio=0.4), run_time=1.8)
        # 指针动画
        area = panel(3.6, 3.0).move_to([4.6, 0.0, 0])
        ptr = Polygon([0, 0, 0], [0, -0.42, 0], [0.11, -0.31, 0], [0.2, -0.5, 0], [0.27, -0.46, 0], [0.18, -0.28, 0], [0.32, -0.28, 0], color=FG, fill_color=FG, fill_opacity=1, stroke_width=1).move_to(area.get_center())
        self.play(FadeIn(area), FadeIn(ptr))
        self.say("HUT 规定 Y 值随“由远及近”增大（屏幕上向下），所以 −5 是向上")
        trace = TracedPath(ptr.get_center, stroke_color=TEAL, stroke_width=3)
        self.add(trace)
        self.play(ptr.animate.shift(RIGHT * 0.5 + UP * 0.5), run_time=1.2)
        click = Circle(radius=0.25, color=AMBER).move_to(ptr)
        self.play(Create(click), click.animate.scale(1.6).set_opacity(0), run_time=0.6)
        self.wait(0.8)
        self.clear_stage()

        # ── 5 小结 ──
        self.chapter("小结", 5)
        pts = VGroup(
            T("前缀字节 = bTag(4) · bType(2) · bSize(2)", size=26),
            T("Global 是持续状态，Local 只管下一个 Main", size=26),
            T("每个 Input 按 Report Size × Report Count 生成字段", size=26),
            T("字段按出现顺序从低位开始依次排进报告", size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, 0.3, 0])
        self.say("掌握这四条，就能手工读懂任何 HID 报告描述符")
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in pts], lag_ratio=0.3), run_time=2.2)
        self.wait(1.6)

        self.outro([
            "HID 1.11 §6.2.2.2（短 Item：bSize / bType / bTag）",
            "HID 1.11 §6.2.2.4–§6.2.2.8（Main / Global / Local Item 与 Input 标志位）",
            "HID 1.11 附录 B.2（启动鼠标报告格式）、附录 E.10（鼠标报告描述符字节）",
            "HID Usage Tables 1.7 §4.2（X 由左到右增大、Y 由远及近增大）",
        ], page="usbtree.gumuhub.com/20-枝干-设备类协议/HID-人机接口设备/02-报告描述符与Item编码/")
