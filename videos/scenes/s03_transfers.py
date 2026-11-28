"""03 · 四种传输类型与（微）帧调度（USB 2.0 §5.4–§5.8、§9.6.6）"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from manim import *  # noqa: F401,F403
from usbstyle import *  # noqa: F401,F403

CTRL, BULK, INTR, ISO = TEAL, BLUE, AMBER, PURPLE


class Transfers(USBScene):
    TITLE = "四种传输类型与帧调度"
    SLUG = "03-transfers"

    def card(self, name, color, lines):
        head = T(name, size=26, color=color, weight="BOLD")
        body = VGroup(*[T(l, size=18, color=FG) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        g = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        box = RoundedRectangle(corner_radius=0.14, width=3.05, height=3.1, stroke_color=color, stroke_width=2,
                               fill_color=color, fill_opacity=0.08)
        if g.width > 2.75:
            g.scale_to_fit_width(2.75)
        g.move_to(box).align_to(box, UP).shift(DOWN * 0.25)
        return VGroup(box, g)

    def frame_row(self, y, label, segs, total_w=11.0, x0=-4.6, h=0.5):
        """一行（微）帧：segs = [(名称, 占比, 颜色)]，左侧带标签与 SOF。"""
        lab = T(label, size=18, color=MUTED).move_to([x0 - 1.15, y, 0])
        outline = Rectangle(width=total_w, height=h, stroke_color=HAIR, stroke_width=1.5).move_to([x0 + total_w / 2, y, 0])
        blocks = VGroup()
        x = x0
        for name, frac, color in segs:
            w = total_w * frac
            r = Rectangle(width=w, height=h, stroke_width=0, fill_color=color, fill_opacity=0.55).move_to([x + w / 2, y, 0])
            t = T(name, size=16, color=FG)
            if t.width > w - 0.08:
                t.scale_to_fit_width(max(w - 0.08, 0.05))
            t.move_to(r)
            blocks.add(VGroup(r, t))
            x += w
        return lab, outline, blocks

    def construct(self):
        self.intro("四种传输类型与帧调度", "控制 · 批量 · 中断 · 同步：谁先上车，谁能保证带宽")

        # ── 1 四种类型 ──
        self.chapter("四种传输类型", 1)
        cards = VGroup(
            self.card("控制 Control", CTRL, ["枚举、配置、命令", "SETUP + 数据 + 状态", "出错可重试", "每个设备都有端点 0"]),
            self.card("批量 Bulk", BULK, ["U 盘、打印机", "数据保证送达", "只用剩余带宽", "不保证时延"]),
            self.card("中断 Interrupt", INTR, ["键盘、鼠标、手柄", "按 bInterval 轮询", "延迟有上界", "出错下次轮询重试"]),
            self.card("同步 Isochronous", ISO, ["音频、视频流", "每（微）帧预留带宽", "没有握手", "出错不重传"]),
        ).arrange(RIGHT, buff=0.3).move_to([0, 0.35, 0])
        self.say("USB 定义了四种传输类型，各自对应不同的数据特点")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.2), run_time=2.0)
        self.say("控制传输管配置命令，批量保证送达但不保证时延")
        self.play(Indicate(cards[0][0], color=CTRL, scale_factor=1.03), Indicate(cards[1][0], color=BULK, scale_factor=1.03), run_time=1.2)
        self.say("中断传输保证轮询周期，同步传输保证带宽但出错不重传")
        self.play(Indicate(cards[2][0], color=INTR, scale_factor=1.03), Indicate(cards[3][0], color=ISO, scale_factor=1.03), run_time=1.2)
        self.wait(0.8)
        self.clear_stage()

        # ── 2 最大包长 ──
        self.chapter("最大包长（字节）", 2)
        hdr = ["", "低速", "全速", "高速"]
        data = [("控制", "8", "8/16/32/64", "64"), ("批量", "—", "8/16/32/64", "512"),
                ("中断", "≤ 8", "≤ 64", "≤ 1024 ×3"), ("同步", "—", "≤ 1023", "≤ 1024 ×3")]
        colors = [CTRL, BULK, INTR, ISO]
        cells = VGroup()
        for j, h in enumerate(hdr):
            cells.add(T(h, size=22, color=MUTED))
        for i, row in enumerate(data):
            cells.add(T(row[0], size=22, color=colors[i], weight="BOLD"))
            for v in row[1:]:
                cells.add(M(v, size=22, color=FG))
        tbl = cells.arrange_in_grid(rows=5, cols=4, buff=(1.0, 0.36), col_alignments="lccc").move_to([0, 0.3, 0])
        lines = VGroup(*[Line([tbl.get_left()[0] - 0.3, y, 0], [tbl.get_right()[0] + 0.3, y, 0], color=HAIR, stroke_width=1)
                         for y in [(cells[3].get_bottom()[1] + cells[7].get_top()[1]) / 2]])
        self.say("最大包长随速度而变：高速批量固定 512 字节")
        self.play(FadeIn(tbl[:4]), Create(lines), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(VGroup(*tbl[4 + 4 * i: 8 + 4 * i]), shift=RIGHT * 0.2) for i in range(4)], lag_ratio=0.25), run_time=2.0)
        self.say("高速中断与同步端点每微帧最多 3 笔事务，即 3072 字节")
        self.play(Indicate(tbl[15], color=INTR), Indicate(tbl[19], color=ISO), run_time=1.2)
        note = T("出处：§5.5.3 · §5.6.3 · §5.7.3 · §5.8.3", size=18, color=MUTED).next_to(tbl, DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(0.8)
        self.clear_stage()

        # ── 3 全速帧 ──
        self.chapter("全速：1 ms 一帧", 3)
        self.say("全速总线每 1 ms 一帧，帧首是主机发出的 SOF 包")
        rows = []
        y0 = 1.6
        plan = [
            [("SOF", 0.03, MUTED), ("同步", 0.30, ISO), ("中断", 0.12, INTR), ("控制", 0.10, CTRL), ("批量（剩余时间）", 0.45, BULK)],
            [("SOF", 0.03, MUTED), ("同步", 0.30, ISO), ("控制", 0.06, CTRL), ("批量（剩余时间）", 0.61, BULK)],
            [("SOF", 0.03, MUTED), ("同步", 0.30, ISO), ("中断", 0.12, INTR), ("批量（剩余时间）", 0.55, BULK)],
        ]
        for i, segs in enumerate(plan):
            lab, outline, blocks = self.frame_row(y0 - i * 0.95, f"第 {i + 1} 帧", segs)
            rows.append((lab, outline, blocks))
        for lab, outline, blocks in rows:
            self.play(FadeIn(lab), Create(outline), run_time=0.3)
            self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in blocks], lag_ratio=0.25), run_time=1.0)
        self.say("同步传输每帧都占位；中断端点 bInterval=2，就每隔一帧出现一次")
        brace = BraceBetweenPoints(rows[0][2][2].get_bottom() + DOWN * 0.02, rows[0][2][2].get_bottom() + DOWN * 0.02 + RIGHT * 0.001)
        tags = VGroup(*[SurroundingRectangle(rows[i][2][2], color=INTR, buff=0.04) for i in (0, 2)])
        self.play(Create(tags), run_time=0.6)
        rule = VGroup(
            T("周期性（同步 + 中断）≤ 每帧 90%", size=22, color=AMBER),
            T("控制传输优先使用剩余时间，批量拿最后的空闲", size=22, color=FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0, -1.75, 0])
        self.say("规范要求：全速周期性传输最多占每帧 90%，其余留给控制和批量")
        self.play(FadeIn(rule, shift=UP * 0.15), run_time=0.8)
        self.wait(1.4)
        self.clear_stage()

        # ── 4 高速微帧 ──
        self.chapter("高速：125 µs 微帧", 4)
        self.say("高速把 1 ms 再切成 8 个 125 µs 的微帧")
        slots = VGroup(*[Rectangle(width=1.35, height=0.75, stroke_color=HAIR, stroke_width=1.5) for _ in range(8)]).arrange(RIGHT, buff=0).move_to([0, 1.3, 0])
        nums = VGroup(*[M(f"µF{i}", size=16, color=MUTED).next_to(slots[i], UP, buff=0.08) for i in range(8)])
        span = DoubleArrow(slots.get_corner(DL) + DOWN * 0.25, slots.get_corner(DR) + DOWN * 0.25, buff=0, color=MUTED, stroke_width=2, tip_length=0.15)
        span_t = T("1 ms = 8 × 125 µs", size=18, color=MUTED).next_to(span, DOWN, buff=0.08)
        self.play(Create(slots), FadeIn(nums), run_time=1.0)
        self.play(GrowFromCenter(span), FadeIn(span_t), run_time=0.6)
        formula = M("周期 = 2^(bInterval-1) × 125 µs", size=26, color=TEAL).move_to([0, -0.5, 0])
        self.say("高速中断/同步端点的周期是 2 的 (bInterval−1) 次方个微帧")
        self.play(Write(formula), run_time=1.0)
        ex = T("例：bInterval = 4 → 2³ = 8 个微帧 = 1 ms", size=22, color=FG).next_to(formula, DOWN, buff=0.3)
        self.play(FadeIn(ex), run_time=0.5)
        hits = VGroup(Rectangle(width=1.35, height=0.75, stroke_width=0, fill_color=INTR, fill_opacity=0.6).move_to(slots[0]))
        self.play(FadeIn(hits), run_time=0.4)
        self.say("bInterval=1 则每个微帧都轮询；高速周期性传输最多占微帧的 80%")
        every = VGroup(*[Rectangle(width=1.35 * 0.8, height=0.3, stroke_width=0, fill_color=ISO, fill_opacity=0.6)
                         .move_to(slots[i]).align_to(slots[i], LEFT).align_to(slots[i], DOWN) for i in range(8)])
        self.play(LaggedStart(*[GrowFromEdge(e, LEFT) for e in every], lag_ratio=0.1), run_time=1.2)
        lim = T("紫色条 = 80% 上限示意", size=18, color=MUTED).next_to(ex, DOWN, buff=0.3)
        self.play(FadeIn(lim))
        self.wait(1.4)
        self.clear_stage()

        # ── 5 小结 ──
        self.chapter("小结", 5)
        pts = VGroup(
            T("控制：配置命令，人人都有端点 0", size=26, color=CTRL),
            T("批量：保证送达，用剩余带宽，不保证时延", size=26, color=BULK),
            T("中断：按 bInterval 轮询，延迟有上界", size=26, color=INTR),
            T("同步：预留带宽，无握手、不重传", size=26, color=ISO),
            T("周期性上限：全速 90% / 帧，高速 80% / 微帧", size=26, color=FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.36).move_to([0, 0.25, 0])
        self.say("选传输类型，就是在“保证送达”“保证时延”“保证带宽”之间取舍")
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in pts], lag_ratio=0.25), run_time=2.4)
        self.wait(1.5)

        self.outro([
            "USB 2.0 §5.4–§5.8（四种传输类型；§5.5.3/§5.6.3/§5.7.3/§5.8.3 最大包长）",
            "USB 2.0 §5.5.4（控制传输保留：全速 10% / 高速 20%）",
            "USB 2.0 §5.6.4、§5.7.4（周期性 ≤ 90% 帧 / ≤ 80% 微帧；高速每微帧最多 3072 字节）",
            "USB 2.0 §8.4.3.1（1 ms 帧与 125 µs 微帧）、§9.6.6 表 9-13（bInterval）",
        ], page="usbtree.gumuhub.com/10-树干-USB核心/06-四种传输类型/")
