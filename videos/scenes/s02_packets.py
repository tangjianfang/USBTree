"""02 · 包与事务、DATA0/DATA1 切换（USB 2.0 §8.3–§8.6）"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from manim import *  # noqa: F401,F403
from usbstyle import *  # noqa: F401,F403


class Packets(USBScene):
    TITLE = "包、事务与数据切换"
    SLUG = "02-packets"

    def construct(self):
        self.intro("包、事务与数据切换", "令牌 · 数据 · 握手，以及 DATA0/DATA1 如何防重复")

        # ── 1 PID ──
        self.chapter("PID：每个包的第一个字节", 1)
        self.say("每个包都以 SYNC 开头，紧跟 8 位 PID，最后以 EOP 结束")
        frame = field_row([("SYNC", 8), ("PID", 8), ("包内容（按类型而定）", 40), ("EOP", "SE0")], unit=0.18, height=0.7)
        frame.move_to([0, 1.7, 0])
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in frame], lag_ratio=0.2), run_time=1.4)
        bits = VGroup(*[chip(b, TEAL if i < 4 else PURPLE, size=22, mono=True) for i, b in enumerate("1001" + "0110")]).arrange(RIGHT, buff=0.08)
        bits.move_to([0, 0.05, 0])
        lab1 = T("PID<3:0> 类型（低位先发）", size=19, color=TEAL).next_to(bits[:4], UP, buff=0.18)
        lab2 = T("校验：前 4 位取反", size=19, color=PURPLE).next_to(bits[4:], DOWN, buff=0.18)
        hex_ = M("IN = 1001b → 字节 0x69", size=26, color=FG).next_to(lab2, DOWN, buff=0.3).set_x(0)
        self.say("PID 低 4 位是类型，高 4 位是它的反码；对不上就整个包丢弃")
        self.play(FadeIn(bits, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(lab1), FadeIn(lab2), Write(hex_), run_time=1.0)
        table = VGroup(
            chip("OUT 0001", BLUE, size=19, mono=True), chip("IN 1001", BLUE, size=19, mono=True),
            chip("SOF 0101", BLUE, size=19, mono=True), chip("SETUP 1101", BLUE, size=19, mono=True),
            chip("DATA0 0011", AMBER, size=19, mono=True), chip("DATA1 1011", AMBER, size=19, mono=True),
            chip("ACK 0010", GREEN, size=19, mono=True), chip("NAK 1010", RED, size=19, mono=True),
            chip("STALL 1110", RED, size=19, mono=True), chip("NYET 0110", PURPLE, size=19, mono=True),
        ).arrange_in_grid(rows=2, cols=5, buff=(0.25, 0.2)).move_to([0, -2.1, 0])
        self.say("常用 PID：令牌 OUT/IN/SOF/SETUP，数据 DATA0/DATA1，握手 ACK/NAK/STALL/NYET")
        self.play(LaggedStart(*[FadeIn(c, scale=0.9) for c in table], lag_ratio=0.08), run_time=1.6)
        self.wait(1.0)
        self.clear_stage()

        # ── 2 三类包 ──
        self.chapter("三类包", 2)
        tok = field_row([("PID", 8), ("ADDR", 7), ("ENDP", 4), ("CRC5", 5)], unit=0.26)
        dat = field_row([("PID", 8), ("数据 0–1024 字节", 48), ("CRC16", 16)], unit=0.1, colors=[TEAL, AMBER, PURPLE])
        hsk = field_row([("PID", 8)], unit=0.26, colors=[GREEN])
        names = [T("令牌包 Token", size=24, color=BLUE), T("数据包 Data", size=24, color=AMBER), T("握手包 Handshake", size=24, color=GREEN)]
        rows = VGroup()
        for n, r in zip(names, [tok, dat, hsk]):
            n.set_width(min(n.width, 3.0))
            rows.add(VGroup(n, r).arrange(RIGHT, buff=0.5))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6).move_to([0, 0.35, 0])
        self.say("令牌包：PID + 7 位地址 + 4 位端点号 + CRC5，由主机发出")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), run_time=0.8)
        self.say("数据包：PID + 载荷 + CRC16；握手包只有一个 PID")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2), run_time=0.8)
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2), run_time=0.8)
        note = T("一笔事务 = 令牌 → 数据 → 握手（同步传输没有握手）", size=24, color=TEAL).move_to([0, -2.3, 0])
        self.say("三类包组成一笔事务，总线上一切都由主机发令牌开始")
        self.play(FadeIn(note, shift=UP * 0.15))
        self.wait(1.0)
        self.clear_stage()

        # ── 3 三种事务 ──
        self.chapter("IN / OUT / SETUP 事务", 3)
        seq = Seq(self, left_x=-5.4, right_x=0.2, first_y=1.3, step=0.6)
        seq.show()
        side = panel(5.6, 4.2).move_to([4.15, -0.4, 0])
        self.play(FadeIn(side))

        def side_text(lines, old=None):
            g = VGroup(*[T(s, size=20, color=c) for s, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            if g.width > 5.1:
                g.scale_to_fit_width(5.1)
            g.move_to(side).align_to(side, UP).shift(DOWN * 0.3)
            if old is not None:
                self.play(FadeOut(old, run_time=0.3))
            self.play(FadeIn(g, shift=UP * 0.1), run_time=0.45)
            return g

        self.say("IN 事务：主机发 IN，设备回数据，主机回 ACK")
        seq.msg("IN  地址 5 · 端点 1", True, BLUE)
        seq.msg("DATA1  载荷", False, AMBER)
        seq.msg("ACK", True, GREEN)
        st = side_text([("IN 事务的三种结局", TEAL), ("有数据 → DATAx，主机 ACK", FG), ("暂无数据 → NAK，主机稍后重试", FG), ("端点停止 → STALL", FG), ("§8.4.6.1 · §8.5.2", MUTED)])
        self.say("设备没数据就回 NAK，主机下次再问；端点出错则回 STALL")
        seq.msg("IN", True, BLUE)
        seq.msg("NAK", False, RED)
        self.say("OUT 事务方向相反：主机发数据，设备用 ACK / NAK / STALL 应答")
        seq.msg("OUT", True, BLUE)
        seq.msg("DATA0  载荷", True, AMBER)
        seq.msg("ACK", False, GREEN)
        st = side_text([("SETUP 事务很特别", TEAL), ("数据固定 DATA0、8 字节", FG), ("设备必须接收并回 ACK", FG), ("不允许回 NAK 或 STALL", RED), ("同时把双方切换位置成一致", FG), ("§8.4.6.4 · §8.6.1", MUTED)], st)
        self.say("SETUP 事务：设备必须接收并 ACK，不允许 NAK 或 STALL")
        seq.msg("SETUP", True, BLUE)
        seq.msg("DATA0  8 字节请求", True, AMBER)
        seq.msg("ACK", False, GREEN)
        self.wait(1.0)
        self.clear_stage()

        # ── 4 数据切换 ──
        self.chapter("DATA0/DATA1 数据切换", 4)
        self.say("收发双方各存一个序列位，数据包的 PID 携带发送方的序列位")
        seq = Seq(self, left_x=-4.2, right_x=2.2, first_y=1.25, step=0.62, left_label="发送方（主机 OUT）", right_label="接收方（设备）")
        seq.show()
        tx = M("Tx=0", size=24, color=BLUE).next_to(seq.hl, LEFT, buff=0.3)
        rx = M("Rx=0", size=24, color=AMBER).next_to(seq.hr, RIGHT, buff=0.3)
        self.play(FadeIn(tx), FadeIn(rx))

        def setb(m, txt, color):
            new = M(txt, size=24, color=color).move_to(m)
            self.play(Transform(m, new), Indicate(m, color=TEAL, scale_factor=1.25), run_time=0.6)

        self.say("正常：DATA0 被接收，接收方翻转；发送方收到 ACK 后才翻转")
        seq.msg("DATA0", True, AMBER)
        setb(rx, "Rx=1", AMBER)
        seq.msg("ACK", False, GREEN)
        setb(tx, "Tx=1", BLUE)
        self.say("下一包用 DATA1，同样成功，双方回到 0")
        seq.msg("DATA1", True, AMBER)
        setb(rx, "Rx=0", AMBER)
        self.say("但如果 ACK 在线上损坏，发送方以为失败，不翻转")
        seq.msg("ACK（损坏）", False, RED)
        cross = Cross(seq.msgs[-1], stroke_color=RED, stroke_width=4).scale(0.5)
        self.play(Create(cross), run_time=0.4)
        self.say("发送方重发 DATA1；接收方发现 PID 与自己的序列位不符，判定为重复包")
        seq.msg("DATA1（重发）", True, AMBER)
        dup = T("重复 → 丢弃数据，仍回 ACK", size=20, color=TEAL).next_to(seq.msgs[-1], RIGHT, buff=0.6)
        self.play(FadeIn(dup, shift=LEFT * 0.2))
        seq.msg("ACK", False, GREEN)
        setb(tx, "Tx=0", BLUE)
        self.say("丢弃数据但照样回 ACK，双方重新同步，数据不重不漏")
        self.wait(1.0)
        self.clear_stage()

        # ── 5 小结 ──
        self.chapter("小结", 5)
        pts = VGroup(
            T("PID = 4 位类型 + 4 位反码，错了整包丢弃", size=26),
            T("事务 = 令牌 → 数据 → 握手，全部由主机发起", size=26),
            T("SETUP 必须 ACK；DATA0/DATA1 切换防止重复与丢包", size=26),
            T("同步传输只有令牌 + 数据：没有握手，也不重传", size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, 0.3, 0])
        self.say("记住这四点，抓包时就能一眼读懂每一笔事务")
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in pts], lag_ratio=0.3), run_time=2.4)
        self.wait(2.0)

        self.outro([
            "USB 2.0 §8.3.1 图 8-1、表 8-1（PID 格式与编码）",
            "USB 2.0 §8.4.1–§8.4.6（令牌、数据、握手包与握手应答；§8.4.6.4 SETUP 不得 NAK/STALL）",
            "USB 2.0 §8.5.2–§8.5.5（批量/控制/中断/同步事务）",
            "USB 2.0 §8.6.1–§8.6.4（数据切换同步与重试，图 8-44～8-47）",
        ], page="usbtree.gumuhub.com/10-树干-USB核心/05-包格式与事务/")
