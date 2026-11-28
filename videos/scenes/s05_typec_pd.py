"""05 · Type-C CC 检测与 PD 契约协商（Type-C R2.5 §4.5、§4.11；PD R3.3 §5.5、§6.4–§6.5、§7.31）"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from manim import *  # noqa: F401,F403
from usbstyle import *  # noqa: F401,F403

SRC, SNK = TEAL, AMBER


def resistor(label, color, vertical=True):
    zz = VMobject(color=color, stroke_width=3)
    pts = [[0, 0.45, 0], [0, 0.3, 0]]
    for i in range(6):
        pts.append([0.12 if i % 2 == 0 else -0.12, 0.3 - (i + 0.5) * 0.1, 0])
    pts += [[0, -0.3, 0], [0, -0.45, 0]]
    zz.set_points_as_corners(pts)
    t = T(label, size=18, color=color).next_to(zz, RIGHT, buff=0.12)
    g = VGroup(zz, t)
    if not vertical:
        g.rotate(-PI / 2)
    return g


class TypeCPD(USBScene):
    TITLE = "Type-C CC 检测与 PD 协商"
    SLUG = "05-typec-pd"

    def construct(self):
        self.intro("Type-C CC 检测与 PD 协商", "一根 CC 线：先靠电阻分压认出彼此，再用 BMC 谈好电压")

        # ── 1 Rp / Rd ──
        self.chapter("CC 线上的 Rp 与 Rd", 1)
        sbox = panel(3.4, 3.6, SRC).move_to([-4.6, 0.2, 0])
        kbox = panel(3.4, 3.6, SNK).move_to([2.2, 0.2, 0])
        st = T("Source（供电方）", size=22, color=SRC).next_to(sbox, UP, buff=0.1)
        kt = T("Sink（受电方）", size=22, color=SNK).next_to(kbox, UP, buff=0.1)
        self.say("Source 在 CC 上接上拉电阻 Rp，Sink 接 5.1 kΩ 下拉电阻 Rd")
        self.play(FadeIn(sbox), FadeIn(kbox), FadeIn(st), FadeIn(kt))
        rp = resistor("Rp", SRC).move_to([-4.2, 0.9, 0])
        v5 = T("5 V", size=18, color=SRC).next_to(rp, UP, buff=0.05)
        rd = resistor("Rd 5.1 kΩ", SNK).move_to([2.0, -0.3, 0])
        gnd = VGroup(*[Line(LEFT * w, RIGHT * w, color=SNK, stroke_width=3).shift(DOWN * 0.08 * i) for i, w in enumerate([0.25, 0.16, 0.07])]).next_to(rd, DOWN, buff=0.02).align_to(rd[0], LEFT).shift(LEFT * 0.13)
        wire = Line([-4.2, 0.45, 0], [2.0, 0.45, 0], color=FG, stroke_width=3)
        wire2 = Line([2.0, 0.45, 0], rd[0].get_top(), color=FG, stroke_width=3)
        cc = T("CC", size=22, color=FG, weight="BOLD").next_to(wire, UP, buff=0.08)
        self.play(Create(rp), FadeIn(v5), Create(rd), Create(gnd), run_time=0.8)
        self.play(Create(wire), Create(wire2), FadeIn(cc), run_time=0.8)
        node = Dot([2.0, 0.45, 0], color=TEAL)
        vm = T("Sink 测得 vRd", size=20, color=TEAL).next_to(node, UP + RIGHT, buff=0.1)
        self.play(FadeIn(node), FadeIn(vm))

        # 电压表
        axis = NumberLine(x_range=[0, 2.2, 0.5], length=4.2, include_numbers=False, color=MUTED).rotate(PI / 2).move_to([5.7, 0.2, 0])
        bands = [(0.277, 0.612, "默认 USB", MUTED), (0.746, 1.164, "1.5 A", BLUE), (1.369, 2.042, "3.0 A", GREEN)]
        bandg = VGroup()
        for lo, hi, lab, c in bands:
            r = Rectangle(width=0.32, height=axis.n2p(hi)[1] - axis.n2p(lo)[1], stroke_width=0, fill_color=c, fill_opacity=0.5)
            r.move_to([axis.get_x(), (axis.n2p(hi)[1] + axis.n2p(lo)[1]) / 2, 0])
            t = T(lab, size=16, color=c).next_to(r, LEFT, buff=0.1)
            bandg.add(VGroup(r, t))
        ax_t = T("vRd (V)", size=16, color=MUTED).next_to(axis, UP, buff=0.1)
        nums = VGroup(*[M(f"{v}", size=14, color=MUTED).next_to(axis.n2p(v), RIGHT, buff=0.12) for v in (0, 1, 2)])
        self.say("Rp 的阻值告诉 Sink 能取多大电流：分压落在哪个区间，就是哪档")
        self.play(Create(axis), FadeIn(ax_t), FadeIn(nums), LaggedStart(*[FadeIn(b) for b in bandg], lag_ratio=0.2), run_time=1.2)
        marker = Triangle(color=TEAL, fill_opacity=1).scale(0.1).rotate(-PI / 2)
        for k, (rv, lab) in enumerate([(56, "56 kΩ → 默认"), (22, "22 kΩ → 1.5 A"), (10, "10 kΩ → 3.0 A")]):
            v = 5 * 5.1 / (rv + 5.1)
            pos = axis.n2p(v) + RIGHT * 0.32
            new_rp = T(f"Rp {lab}", size=18, color=SRC).move_to(rp[1]).align_to(rp[1], LEFT)
            vv = M(f"{v:.2f} V", size=16, color=TEAL).next_to(pos, RIGHT, buff=0.15)
            if k == 0:
                marker.move_to(pos)
                self.play(Transform(rp[1], new_rp), FadeIn(marker), FadeIn(vv), run_time=0.6)
                self.vv = vv
            else:
                self.play(Transform(rp[1], new_rp), marker.animate.move_to(pos), Transform(self.vv, vv), run_time=0.8)
            self.wait(0.5)
        note = T("上拉到 5 V 时 Rp：56 k / 22 k / 10 kΩ（Type-C R2.5 表 4-27）", size=18, color=MUTED).move_to([-1.2, -2.35, 0])
        self.play(FadeIn(note))
        self.say("另一根 CC 悬空，因此还能顺便判断插头是正插还是反插")
        self.wait(0.6)
        self.say("CC 状态稳定 tCCDebounce（100～200 ms）后，Source 才打开 VBUS 输出 5 V")
        self.wait(0.8)
        self.clear_stage()

        # ── 2 PD 协商 ──
        self.chapter("PD 显式契约协商", 2)
        self.say("VBUS 有了 5 V，双方开始在 CC 上用 BMC 编码（约 300 kbps）交换 PD 消息")
        seq = Seq(self, left_x=-5.6, right_x=0.0, first_y=1.35, step=0.56, left_label="Source", right_label="Sink",
                  left_color=SRC, right_color=SNK)
        seq.show()
        # VBUS 图
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 22, 5], x_length=5.0, y_length=2.6, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 1.5}).move_to([4.2, -0.9, 0])
        ylab = T("VBUS", size=16, color=MUTED).next_to(ax.y_axis, UP, buff=0.05)
        ticks = VGroup(*[M(f"{v}V", size=13, color=MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.08) for v in (5, 9, 20)])
        vline = VMobject(color=TEAL, stroke_width=3).set_points_as_corners([ax.c2p(0, 5), ax.c2p(4, 5)])
        self.play(Create(ax), FadeIn(ylab), FadeIn(ticks), Create(vline), run_time=0.8)

        # PDO 面板
        pdo_p = panel(5.0, 1.75).move_to([4.2, 1.55, 0])
        pdo_t = T("Source_Capabilities（示例 PDO）", size=17, color=SRC).move_to(pdo_p).align_to(pdo_p, UP).shift(DOWN * 0.15)
        pdos = VGroup(*[chip(s, SRC, size=17, mono=True) for s in ["#1 5V 3A", "#2 9V 3A", "#3 15V 3A", "#4 20V 3A"]]).arrange_in_grid(rows=2, cols=2, buff=(0.2, 0.12))
        pdos.next_to(pdo_t, DOWN, buff=0.15)
        seq.msg("Source_Capabilities  · 数据 00001b", True, SRC)
        self.play(FadeIn(pdo_p), FadeIn(pdo_t), LaggedStart(*[FadeIn(p) for p in pdos], lag_ratio=0.15), run_time=1.0)
        seq.msg("GoodCRC", False, MUTED, run_time=0.45)
        self.say("每条消息对方都要回 GoodCRC；Source 每 100～200 ms 重发能力，直到收到 GoodCRC")
        self.wait(0.4)
        self.say("Sink 从列表里挑一档，用 Request 请求：这里选 #2，9 V / 3 A")
        seq.msg("Request（对象 #2）  · 数据 00010b", False, SNK)
        self.play(Indicate(pdos[1], color=SNK, scale_factor=1.1), pdos[1][0].animate.set_stroke(SNK).set_fill(SNK, opacity=0.3), run_time=0.8)
        seq.msg("GoodCRC", True, MUTED, run_time=0.45)
        self.say("Sink 发出 Request 后最多等 tSenderResponse（27～50 ms），Source 回 Accept")
        seq.msg("Accept  · 控制 00011b", True, GREEN)
        seq.msg("GoodCRC", False, MUTED, run_time=0.45)
        self.say("随后 Source 把电压从 5 V 调到 9 V")
        ramp = VMobject(color=TEAL, stroke_width=3).set_points_as_corners([ax.c2p(4, 5), ax.c2p(4.6, 5), ax.c2p(6.2, 9), ax.c2p(10, 9)])
        self.play(Create(ramp), run_time=1.4)
        self.say("调好后发 PS_RDY；Sink 等 PS_RDY 的上限是 tPSTransition（450～550 ms）")
        seq.msg("PS_RDY  · 控制 00110b", True, GREEN)
        seq.msg("GoodCRC", False, MUTED, run_time=0.45)
        tag = chip("显式契约：9 V / 3 A = 27 W", GREEN, size=20).next_to(ax, UP, buff=0.12)
        tag.move_to([4.2, 0.62, 0])
        self.play(FadeOut(VGroup(pdo_p, pdo_t, pdos)), FadeIn(tag, scale=0.9))
        self.say("收到 PS_RDY，显式契约建立，Sink 可以按 9 V / 3 A 取电")
        self.wait(1.0)
        self.clear_stage()

        # ── 3 小结 ──
        self.chapter("小结", 3)
        pts = VGroup(
            T("Rp（Source）/ Rd 5.1 kΩ（Sink）：分压决定默认 / 1.5 A / 3.0 A", size=24),
            T("tCCDebounce 100～200 ms 后才输出 VBUS 5 V", size=24),
            T("Source_Capabilities → Request → Accept → PS_RDY，每条都回 GoodCRC", size=24),
            T("tSenderResponse 27～50 ms · tPSTransition 450～550 ms（SPR）", size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to([0, 0.3, 0])
        self.say("先电阻、后消息：这就是 Type-C 充电器“认出”设备并升压的全过程")
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in pts], lag_ratio=0.3), run_time=2.2)
        self.wait(1.6)

        self.outro([
            "USB Type-C R2.5 表 4-27（Rp）、表 4-28（Rd）、表 4-34（tCCDebounce）、表 4-36（vRd 区间）",
            "USB PD R3.3 §5.5.1（BMC fBitRate 270～330 kbps）",
            "USB PD R3.3 表 6.4 / 表 6.5（控制 / 数据消息类型编码）",
            "USB PD R3.3 §7.31 表 7.10（tTypeCSendSourceCap、tSenderResponse、tPSTransition）",
        ], page="usbtree.gumuhub.com/30-枝干-接口与供电/04-USBPD协议/")
