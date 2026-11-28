from build import *
LEG="蓝 = 用户空间应用，红 = 内核/系统级驱动，绿 = 用户态驱动或守护进程，橙 = 系统框架，灰 = 硬件与外部。"
cfgs=[]
# 07 Linux
d=mm('''    subgraph US["用户空间"]
        LIB["libusb / 应用"]
        HA["HID 应用"]
        VH["BlueZ HoG / 虚拟 HID 进程"]
        GD["gadget 守护进程"]
    end
    subgraph K["内核"]
        CORE["usbcore + usbfs"]
        HIDC["HID core"]
        COMP["composite + 函数驱动"]
        HCD["HCD: xhci / ehci / ohci"]
        UDC["UDC 驱动"]
    end
    HW1[("主机控制器")]
    HW2[("设备控制器")]
    LIB -->|"① /dev/bus/usb"| CORE
    HA -->|"② /dev/hidrawN"| HIDC
    VH -->|"③ /dev/uhid"| HIDC
    GD -->|"④ ConfigFS / FunctionFS"| COMP
    CORE -->|"⑤ usbhid"| HIDC
    CORE -->|"⑥ URB"| HCD
    HCD --> HW1
    COMP -->|"⑦ gadget API"| UDC
    UDC --> HW2
''',{'app':['LIB','HA','VH','GD'],'drv':['CORE','HIDC','COMP','HCD','UDC'],'hw':['HW1','HW2']})
cfgs.append(dict(src='01-linux.md',out='07-linux-usb-stack.md',title='架构文档：Linux USB 栈（主机、HID、Gadget 与虚拟 USB）',
 baseline='docs.kernel.org（页面标注 Linux 7.4.0-rc4）；torvalds/linux master',scope='docs.kernel.org/driver-api/usb, docs.kernel.org/usb, docs.kernel.org/hid, drivers/usb',
 overview='''Linux 用一个内核 USB 栈同时覆盖主机侧（usbcore + HCD）、HID 子系统和设备侧（gadget 框架）：新设备默认 autosuspend 延迟 **2 秒**，USB/IP 用 TCP **3240**，`/dev/uhid`、ConfigFS、dummy_hcd 都可在无硬件时造出“真实”设备。读者是熟悉 Windows WinUSB/KMDF/hidclass、要做虚拟 USB 与驱动研究的工程师。来源只用 kernel.org 文档与 torvalds/linux 源码，以及 libusb、systemd、BlueZ、Wireshark 官方站点。

**TL;DR**

- 主机侧：URB 经 usbcore 交给 HCD；用户态走 usbfs/libusb 或 hidraw。
- 虚拟 HID 用 uhid，虚拟设备用 ConfigFS + dummy_hcd，网络导出用 USB/IP。
- Raw Gadget 官方定位为调试与 fuzzing，生产用 FunctionFS。
- 协议报文与 ConfigFS/FunctionFS/Raw Gadget 的逐条定义见 [06-linux-virtual-usb.md](06-linux-virtual-usb.md)，本文只讲栈结构与取舍。

'''+LEG+'''

标记 **待核实** 的内容未能从官方来源确认，不要当作事实引用。''',
 diagram=d,caption='''
图中 ①–④ 是用户态入口，⑤–⑥ 是主机侧调用路径，⑦ 是设备侧；红色内核块都在同一内核镜像内。
''',
 rename={'架构分层':'架构分层：主机侧、HID 与设备侧三条路径'},
 sub=lambda t,b: b.replace('### 7.4 dummy_hcd','### 7.4 dummy_hcd') .replace('## 7. 设备侧','## 设备侧')))
# 08 ARM
d=mm('''    CONN["usb-c-connector<br/>CC / VBUS"]
    MUX["Type-C mux / retimer"]
    TCPM["TCPM 或 UCSI<br/>typec class"]
    RS["USB Role Switch"]
    DRD["双角色控制器<br/>DWC3 / DWC2 / ChipIdea / Cadence / MUSB"]
    PHY["USB2 / USB3 PHY"]
    XH["xhci-plat / ehci / musb host"]
    UDC["UDC → gadget / composite"]
    CONN -->|"① CC 检测"| TCPM
    TCPM -->|"② 角色通知"| RS
    RS -->|"③ 切换数据角色"| DRD
    DRD -->|"④ host"| XH
    DRD -->|"⑤ device"| UDC
    PHY --> DRD
    CONN -.->|"SBU / SS 线"| MUX
''',{'drv':['TCPM','RS','DRD','XH','UDC'],'hw':['CONN','MUX','PHY']})
cfgs.append(dict(src='02-arm-embedded.md',out='08-arm-embedded-usb.md',title='架构文档：ARM / 嵌入式 USB（SoC 控制器、设备树、双角色与 MCU 栈）',
 baseline='torvalds/linux master（Kconfig 与 DT binding）；TinyUSB README',scope='drivers/usb/{dwc2,dwc3,chipidea,musb,cdns3,typec,roles}, Documentation/devicetree/bindings/usb, hathach/tinyusb',
 overview='''ARM 在 USB 层没有独立 OS 栈：Linux/Android 跑在 ARM SoC 上时，差异集中在 **5 类控制器 IP**（DWC2、DWC3、ChipIdea、MUSB、Cadence）、设备树描述（`dr_mode` 未指定时默认 `otg`）、双角色切换和 Type-C 管理；MCU 上则是 TinyUSB 等裸机/RTOS 协议栈。

**TL;DR**

- 控制器 IP 决定驱动：dwc2/dwc3/ci_hdrc/musb-hdrc/cdns3；主机侧 USB3 类走 xhci-plat。
- 角色链路：连接器 → TCPM 或 UCSI → Role Switch → 双角色控制器。
- 同一 IP 在 Linux 与 TinyUSB 都有驱动，寄存器模型一致，是从固件迁到内核驱动研究的入口。
- Synopsys、Cadence、Mentor 的 Databook 需 NDA，本文不引用，寄存器细节以 Linux 驱动与 binding 为准。
- 虚拟 USB 与 gadget 的做法见 [07-linux-usb-stack.md](07-linux-usb-stack.md) 与 [06-linux-virtual-usb.md](06-linux-virtual-usb.md)。

'''+LEG,
 diagram=d,caption='''
① 到 ③ 是 Type-C 角色协商链，④ 与 ⑤ 是控制器按角色选择的两条路；虚线是数据线复用，不走角色链。
''',
 rename={'SoC USB 子系统的组成':'SoC 里的角色链路：连接器到控制器'}))
# 09 macOS
d=mm('''    subgraph APP["用户空间：App 与 DriverKit dext"]
        A1["IOHIDManager / IOUSBHost"]
        D1["USBDriverKit dext"]
        A2["CoreHID（macOS 15+）"]
        D2["HIDDriverKit dext"]
        A3["CoreBluetooth"]
    end
    subgraph XNU["XNU 内核"]
        K3["HID 事件系统"]
        K1["IOKit / IORegistry"]
        K2["IOUSBHostFamily"]
    end
    HW[("xHCI / Apple silicon 控制器")]
    A1 -->|"① IOKit 用户态接口"| K1
    A2 -->|"② HID 客户端"| K3
    D1 -->|"③ provider"| K1
    D2 -->|"④ 事件分发"| K3
    K1 --> K2
    K2 --> HW
''',{'app':['A1','A2','A3'],'svc':['D1','D2'],'drv':['K1','K2','K3'],'hw':['HW']})
cfgs.append(dict(src='03-macos.md',out='09-macos-usb.md',title='架构文档：macOS USB 栈（IOKit、DriverKit 系统扩展与 HID 路径）',
 baseline='developer.apple.com 文档 JSON 与 support.apple.com（2026-11-28 抓取）',scope='IOUSBHost, DriverKit, USBDriverKit, HIDDriverKit, SystemExtensions, CoreHID, IOHIDManager',
 overview='''macOS 自 Big Sur 起不再支持 **IOUSBFamily 与 IOHIDFamily 的全部 KPI**，第三方 USB/HID 驱动改为用户态 DriverKit 扩展（dext），分发要走 entitlement 申请、Developer ID 签名与公证。读者是 Windows 驱动背景、想做 macOS 虚拟 HID 或自定义 USB 驱动的工程师。来源只用 developer.apple.com 与 support.apple.com，Apple 未公开的内核实现标 **待核实**。

**TL;DR**

- 免驱动访问：IOUSBHost 框架（macOS 10.15+）与 IOHIDManager；CoreHID 需 macOS 15+。
- 写驱动：USBDriverKit / HIDDriverKit，需向 Apple 申请 DriverKit entitlement。
- 虚拟 HID：CoreHID `HIDVirtualDevice` 或 HIDDriverKit，都要对应 entitlement。
- 没有面向第三方的 USB 设备（gadget）模式 API（否定性结论，**待核实**）。

'''+LEG,
 diagram=d,caption='''
① 与 ② 是不写驱动的路径，③ 与 ④ 是 dext 路径；dext 虽在用户态，仍通过 IOKit 服务平面与内核对话。
''',
 rename={'架构分层':'架构分层：App、dext 与内核三层'}))
# 10 iOS
d=mm('''    ACC1["MFi 配件"]
    ACC2["标准 USB-C 配件"]
    ACC3["自定义 USB 设备<br/>仅 M 系列 iPad"]
    ACC4["BLE 设备"]
    EA["ExternalAccessory"]
    SYS["系统内建类驱动"]
    GC["GameController"]
    DK["USBDriverKit dext"]
    APP["宿主 App<br/>communicates-with-drivers"]
    CB["CoreBluetooth"]
    ACC1 -->|"① 协议字符串"| EA
    ACC2 -->|"② 系统驱动"| SYS
    SYS --> GC
    ACC3 -->|"③ DriverKit"| DK
    DK -->|"user client"| APP
    ACC4 -->|"④ GATT"| CB
''',{'hw':['ACC1','ACC2','ACC3','ACC4'],'app':['EA','GC','APP','CB'],'drv':['SYS'],'svc':['DK']})
cfgs.append(dict(src='04-ios-ipados.md',out='10-ios-ipados-usb.md',title='架构文档：iOS / iPadOS USB（MFi、iPad DriverKit 与配件安全）',
 baseline='developer.apple.com、support.apple.com、mfi.apple.com（2026-11-28 抓取）',scope='ExternalAccessory, DriverKit(iPadOS), USBDriverKit, GameController, CoreBluetooth, 有线配件设置',
 overview='''iOS 是最封闭的 USB 平台：第三方 App 没有通用 USB 主机 API，只有 **4 条通道**——MFi/ExternalAccessory、系统内建标准类驱动、M 系列 iPad 的 DriverKit、蓝牙。iPhone 15 起为 USB-C，Pro 机型配 USB 3 线可达 10 Gbit/s。“某 API 不存在”这类否定性结论无法由单页官方文档证实，一律标 **待核实**。

**TL;DR**

- 私有协议配件：MFi 计划 + ExternalAccessory，由配件厂商决定哪些 App 能通信。
- 自定义 USB 设备：只有 M 系列 iPad 能用 USBDriverKit，驱动随 App 分发。
- 没有 HIDDriverKit，CoreHID 仅 macOS，iOS 上无公开原始 HID 报告 API（**待核实**）。
- 安全：锁定超 1 小时后不允许新数据连接，已知配件记忆 30 天。

'''+LEG,
 diagram=d,caption='''
① 到 ④ 对应四条通道；绿色 dext 只在 M 系列 iPad 上存在，其余机型只能走 ①②④。
''',
 rename={'访问路径总览':'访问路径：四条通道，只有 iPad 能写驱动'}))
# 11 Android
d=mm('''    subgraph APP["App"]
        H["USB Host API<br/>UsbManager"]
        AC["Accessory API<br/>UsbAccessory"]
        BT["android.bluetooth<br/>BLE / BluetoothHidDevice"]
    end
    subgraph FW["system_server"]
        US["UsbService<br/>UsbHostManager / UsbDeviceManager"]
        IN["InputFlinger<br/>EventHub → InputReader"]
        MTP["MtpService"]
    end
    subgraph HAL["HAL"]
        UH["USB HAL<br/>端口状态与角色"]
        GH["Gadget HAL<br/>setCurrentUsbFunctions"]
    end
    subgraph KN["Linux 内核（GKI + vendor 模块）"]
        UC["usbcore + xHCI / DWC3"]
        HK["HID core → input / evdev"]
        G["ConfigFS + FunctionFS + UDC"]
        TC["typec class / TCPM"]
    end
    H -->|"① Binder"| US
    AC --> US
    US -->|"② 主机侧"| UC
    US -->|"③ 设备侧"| G
    GH -->|"④ ConfigFS"| G
    MTP --> G
    UH --> TC
    HK --> IN
''',{'app':['H','AC','BT'],'own':['US','IN','MTP'],'svc':['UH','GH'],'drv':['UC','HK','G','TC']})
cfgs.append(dict(src='05-android.md',out='11-android-usb.md',title='架构文档：Android USB（Host API、AOA、Gadget HAL 与 HID）',
 baseline='developer.android.com、source.android.com（含 Android 15 CDD）、android.googlesource.com（2026-11-28 抓取）',scope='android.hardware.usb, AOA/AOAv2, USB HAL, Gadget HAL, MTP/PTP, 输入链路',
 overview='''Android 在 Linux 内核 USB 栈（见 [07-linux-usb-stack.md](07-linux-usb-stack.md)）之上加了框架层：Host API 要 Android **3.1（API 12）** 以上，外设模式经 AOA（VID `0x18D1`，PID `0x2D00`–`0x2D05`），Android 15 CDD 要求带外设口的手持设备必须实现 AOA。读者是要在手机上做 USB 外设通信、或把手机当虚拟 USB 设备的工程师。

**TL;DR**

- 主机模式：`UsbManager` + 每设备用户授权，不装驱动。
- 外设模式：AOA 握手（请求 51 / 52 / 53），AOAv2 还能由配件注入 HID。
- 设备侧由 Gadget HAL 通过 ConfigFS 组装，MTP/PTP 用 FunctionFS。
- HID 输入走 内核 HID → evdev → EventHub → InputReader；蓝牙 HID 设备角色用 `BluetoothHidDevice`（API 28+）。

'''+LEG,
 diagram=d,caption='''
① 到 ④ 是 App 与 HAL 进入内核的四条入口；主机侧与设备侧在内核里分属不同子系统，不要混为一条链。
''',
 rename={'架构分层':'架构分层：App、system_server、HAL 与内核'}))
# 12 comparison
d=mm('''    subgraph LNX["Linux / Android / ARM"]
        LA["libusb / hidraw / Host API"]
        LK["内核 usbcore + HID core"]
        LG["ConfigFS / FunctionFS / Raw Gadget"]
        LU["UDC 驱动"]
    end
    subgraph MAC["macOS / M 系列 iPad"]
        MA["IOUSBHost / IOHIDManager / CoreHID"]
        MD["DriverKit dext"]
        MK["XNU IOKit"]
    end
    subgraph IOS["iPhone / 其他 iPad"]
        IA["ExternalAccessory / GameController"]
        IS["系统内建驱动"]
    end
    subgraph WIN["Windows 参照"]
        WA["WinUSB / HidD_*"]
        WD["KMDF / UMDF 2 / VHF / UDE"]
        WK["Usbhub3 / Ucx01000 / Usbxhci / hidclass"]
    end
    %% 不可见连线：让四个平台分组纵向排列，避免横向过宽
    LNX ~~~ MAC
    MAC ~~~ IOS
    IOS ~~~ WIN
    LA --> LK
    LG --> LU
    MA --> MK
    MD --> MK
    IA --> IS
    WA --> WK
    WD --> WK
''',{'app':['LA','MA','IA','WA'],'drv':['LK','LU','MK','IS','WK'],'svc':['MD','WD'],'own':['LG']})
cfgs.append(dict(src='06-cross-platform-comparison.md',out='12-cross-platform-comparison.md',title='架构文档：跨平台 USB 栈异同（Linux、ARM、macOS、iOS、Android 与 Windows）',
 baseline='07–11 号文档与 learn.microsoft.com（2026-11-28 核对）',scope='07-linux-usb-stack.md, 08-arm-embedded-usb.md, 09-macos-usb.md, 10-ios-ipados-usb.md, 11-android-usb.md',
 overview='''在 **5 个平台 + Windows 参照** 的对比中，只有 Linux 系（含 Android 与 ARM 板）把 USB **设备侧**完整开放给开发者；Apple 平台第三方驱动强制用户态（DriverKit）；Android 的特色是 AOA。本文只做归纳，每格事实回链到 07–11 号文档的引用标签（`[Lx]` `[Ax]` `[Mx]` `[Ix]` `[Dx]`）与 learn.microsoft.com 的 `[Wx]`。各平台文档中标 **待核实** 的点，这里保持 **待核实**。

**TL;DR**

- Linux 与 Android 共用同一内核 USB 栈；ARM 的差异在控制器 IP、设备树与角色管理。
- 虚拟 USB 研究首选 Linux：dummy_hcd + ConfigFS / Raw Gadget；USB/IP 细节见 [06-linux-virtual-usb.md](06-linux-virtual-usb.md)。
- 虚拟 HID：Linux uhid、macOS CoreHID、Windows VHF、Android AOAv2；iOS 无公开 API。
- Apple 的门槛是授权（entitlement、公证、MFi），不是技术。

'''+LEG,
 diagram=d,caption='''
图只展示各平台“应用 → 驱动层”的分层差异，不含设备侧细节；设备模式与虚拟 USB 的差异在下面的大表里。
''',
 rename={'2. 架构总览图':'架构总览图'}))
