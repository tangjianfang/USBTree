"""06 · 线上的比特：NRZI 编码与位填充（USB 2.0 §7.1.8–§7.1.10、§7.1.13.2）"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from manim import *  # noqa: F401,F403
from usbstyle import *  # noqa: F401,F403

W = 0.52   # 每位宽度
HI, LO = 0.42, -0.42


class Wave:
    """逐位绘制 NRZI 波形；level=+1 表示 J，-1 表示 K，0 表示 SE0。"""

    def __init__(self, scene, x0, y, level=1):
        self.s, self.x, self.y, self.level = scene, x0, y, level
        self.parts = VGroup()

    def yv(self, lv):
        return self.y + (HI if lv == 1 else LO if lv == -1 else 0)

    def step(self, new_level, color=TEAL, run_time=0.18, label=None):
        segs = VGroup()
        if new_level != self.level:
            segs.add(Line([self.x, self.yv(self.level), 0], [self.x, self.yv(new_level), 0], color=color, stroke_width=3))
        segs.add(Line([self.x, self.yv(new_level), 0], [self.x + W, self.yv(new_level), 0], color=color, stroke_width=3))
        self.level = new_level
        self.x += W
        self.parts.add(segs)
        if run_time:
            self.s.play(Create(segs), run_time=run_time)
        return segs

    def nrzi(self, bit, color=TEAL, run_time=0.18):
        return self.step(self.level if bit == 1 else -self.level, color, run_time)


def bit_cells(bits, x0, y, color=FG, size=22, colors=None):
    g = VGroup()
    for i, b in enumerate(bits):
        c = colors[i] if colors else color
        g.add(M(str(b), size=size, color=c).move_to([x0 + W * (i + 0.5), y, 0]))
    return g


class NRZI(USBScene):
    TITLE = "NRZI 编码与位填充"
    SLUG = "06-nrzi"

    def construct(self):
        self.intro("NRZI 编码与位填充", "USB 线上没有时钟线：接收方如何从数据里恢复时钟")

        # ── 1 NRZI 规则 ──
        self.chapter("NRZI：0 翻转，1 保持", 1)
        rule = VGroup(chip("数据 0 → 电平翻转", TEAL, size=24), chip("数据 1 → 电平不变", BLUE, size=24)).arrange(RIGHT, buff=0.6).move_to([0, 2.3, 0])
        self.say("USB 用 NRZI 编码：数据 0 让线路电平翻转，数据 1 保持不变")
        self.play(FadeIn(rule, shift=DOWN * 0.2))
        x0 = -6.2
        ylab = VGroup(T("J", size=22, color=MUTED).move_to([x0 - 0.35, 0.2 + HI, 0]), T("K", size=22, color=MUTED).move_to([x0 - 0.35, 0.2 + LO, 0]))
        grid = VGroup(*[DashedLine([x0, 0.2 + v, 0], [6.4, 0.2 + v, 0], color=HAIR, stroke_width=1, dash_length=0.08) for v in (HI, LO)])
        self.play(FadeIn(ylab), Create(grid), run_time=0.5)
        wave = Wave(self, x0, 0.2, level=1)
        idle = VGroup(*[wave.step(1, MUTED, run_time=0) for _ in range(2)])
        idle_t = T("空闲 = J", size=18, color=MUTED).next_to(idle, UP, buff=0.12)
        self.play(Create(idle), FadeIn(idle_t), run_time=0.5)

        # SYNC
        self.say("每个全速包以 SYNC 开头：00000001，线上就是 KJKJKJKK")
        sync = [0, 0, 0, 0, 0, 0, 0, 1]
        sx = wave.x
        cells = bit_cells(sync, sx, 1.35, color=AMBER)
        stag = T("SYNC", size=20, color=AMBER).next_to(cells, UP, buff=0.12)
        self.play(FadeIn(cells), FadeIn(stag), run_time=0.4)
        syms = VGroup()
        for b in sync:
            wave.nrzi(b, AMBER, 0.22)
            syms.add(T("J" if wave.level == 1 else "K", size=16, color=MUTED).move_to([wave.x - W / 2, -0.75, 0]))
        self.play(FadeIn(syms), run_time=0.4)
        self.say("连续的 0 制造密集跳变，接收方据此锁定时钟")
        self.wait(0.4)

        # PID ACK
        self.say("接着是 PID：ACK = 0xD2，低位先发 → 0 1 0 0 1 0 1 1")
        pid = [0, 1, 0, 0, 1, 0, 1, 1]
        px = wave.x
        cells2 = bit_cells(pid, px, 1.35, color=GREEN)
        ptag = T("PID = ACK", size=20, color=GREEN).next_to(cells2, UP, buff=0.12)
        self.play(FadeIn(cells2), FadeIn(ptag), run_time=0.4)
        for b in pid:
            wave.nrzi(b, GREEN, 0.22)
            syms.add(T("J" if wave.level == 1 else "K", size=16, color=MUTED).move_to([wave.x - W / 2, -0.75, 0]))
        self.play(FadeIn(syms[8:]), run_time=0.4)

        # EOP
        self.say("包尾 EOP：两位时间的 SE0（D+、D− 都拉低），再回到 J")
        e1 = wave.step(0, RED, 0.25)
        e2 = wave.step(0, RED, 0.25)
        e3 = wave.step(1, MUTED, 0.25)
        etag = T("EOP：SE0 ×2 位 + J", size=18, color=RED).next_to(VGroup(e1, e2, e3), DOWN, buff=0.75)
        self.play(FadeIn(etag))
        self.wait(1.0)
        self.clear_stage()

        # ── 2 位填充 ──
        self.chapter("位填充：连续 6 个 1 后插 0", 2)
        self.say("问题来了：一长串 1 没有任何跳变，接收方的时钟会漂移")
        raw = [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1]
        x0 = -6.0
        lab_raw = T("原始数据", size=20, color=MUTED).move_to([x0 - 0.0, 2.25, 0]).align_to([x0, 0, 0], LEFT)
        rc = bit_cells(raw, x0, 1.8, color=FG)
        self.play(FadeIn(lab_raw), FadeIn(rc))
        run = SurroundingRectangle(rc[2:10], color=RED, buff=0.06)
        run_t = T("8 个连续的 1", size=18, color=RED).next_to(run, UP, buff=0.12)
        self.play(Create(run), FadeIn(run_t))
        self.say("规则：发送方每遇到 6 个连续的 1，就强行插入一个 0")
        stuffed = raw[:8] + [0] + raw[8:]
        cols = [FG] * 8 + [RED] + [FG] * (len(raw) - 8)
        lab_st = T("填充后", size=20, color=MUTED).move_to([x0, 0.95, 0]).align_to([x0, 0, 0], LEFT)
        sc = bit_cells(stuffed, x0, 0.5, colors=cols)
        self.play(FadeIn(lab_st), TransformFromCopy(rc, VGroup(*sc[:8], *sc[9:])), run_time=0.9)
        ins = sc[8]
        arrow = Arrow(ins.get_bottom() + DOWN * 0.7, ins.get_bottom() + DOWN * 0.05, buff=0, color=RED, stroke_width=3, tip_length=0.15)
        ins_t = T("插入的 0", size=18, color=RED).next_to(arrow, DOWN, buff=0.05)
        self.play(FadeIn(ins, scale=1.6), GrowArrow(arrow), FadeIn(ins_t), FadeOut(run), FadeOut(run_t))
        # 波形
        wave = Wave(self, x0, -1.6, level=1)
        grid2 = VGroup(*[DashedLine([x0, -1.6 + v, 0], [x0 + W * len(stuffed), -1.6 + v, 0], color=HAIR, stroke_width=1, dash_length=0.08) for v in (HI, LO)])
        self.play(Create(grid2), run_time=0.3)
        self.say("插入的 0 在 NRZI 里就是一次翻转：保证至少每 7 个位时间有一次跳变")
        for i, b in enumerate(stuffed):
            wave.nrzi(b, RED if i == 8 else TEAL, 0.16)
        self.say("接收方解码后看到 6 个 1 加一个 0，就把这个 0 删掉")
        self.wait(0.6)
        rules = VGroup(
            T("从 SYNC 末尾的 1 开始计数", size=20, color=FG),
            T("全速 / 低速：连续 7 个 1 = 位填充错误，", size=20, color=FG),
            T("　　　　　　该包被丢弃", size=20, color=FG),
            T("高速 EOP：01111111 不做填充，", size=20, color=AMBER),
            T("　　　　　故意制造填充错误来标记包尾", size=20, color=AMBER),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        if rules.width > 5.4:
            rules.scale_to_fit_width(5.4)
        rules.move_to([3.85, -1.2, 0])
        bg = panel(rules.width + 0.4, rules.height + 0.35).move_to(rules)
        self.say("全速 / 低速收到 7 个连续的 1 就是错误；高速反而用这个“错误”标记包尾")
        self.play(FadeIn(bg), FadeIn(rules, shift=UP * 0.1), run_time=0.8)
        self.wait(1.4)
        self.clear_stage()

        # ── 3 小结 ──
        self.chapter("小结", 3)
        pts = VGroup(
            T("NRZI：0 翻转、1 保持，空闲为 J", size=26),
            T("SYNC：全速 / 低速 8 个符号 KJKJKJKK，高速 32 个", size=26),
            T("位填充：连续 6 个 1 后插 0，至少每 7 位一次跳变", size=26),
            T("EOP：全速 / 低速 = SE0 约 2 位 + J；高速 = 故意的填充错误", size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, 0.3, 0])
        self.say("示波器上看到的每一个跳变，都能用这四条规则解释")
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in pts], lag_ratio=0.3), run_time=2.2)
        self.wait(1.6)

        self.outro([
            "USB 2.0 §7.1.8 图 7-31（NRZI 编码）",
            "USB 2.0 §7.1.9、§7.1.9.1–§7.1.9.2（位填充：6 个 1 后插 0；7 个 1 为错误）",
            "USB 2.0 §7.1.10 图 7-35（SYNC：3 对 KJ + 2 个 K；高速 15 对 KJ + 2 个 K）",
            "USB 2.0 §7.1.13.2（EOP 宽度：全速 SE0 160～175 ns；高速 EOP 01111111）",
            "USB 2.0 §8.3.1 表 8-1（ACK PID = 0010b → 字节 0xD2）",
        ], page="usbtree.gumuhub.com/10-树干-USB核心/04-信号编码与比特流/")
