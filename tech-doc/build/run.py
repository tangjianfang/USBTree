from cfgs import *
import os, re
_HERE=os.path.dirname(os.path.abspath(__file__))
for c in cfgs: build(c)
P=os.environ.get('TECH_DOC_OUT') or os.path.dirname(_HERE)
if not P.endswith(os.sep):
    P+=os.sep
def sub(f,pairs):
    s=open(P+f).read()
    for a,b in pairs:
        assert a in s,(f,a)
        s=s.replace(a,b)
    open(P+f,'w').write(s)
sub('08-arm-embedded-usb.md',[("（见 `07-linux-usb-stack.md` §7.4）","（见 [07-linux-usb-stack.md](07-linux-usb-stack.md) 的“dummy_hcd”小节）"),
 ("（见 `07-linux-usb-stack.md` §3）","（见 [07-linux-usb-stack.md](07-linux-usb-stack.md) 的“HID 子系统”节）"),
 ("方法见 `07-linux-usb-stack.md` §7","方法见 [07-linux-usb-stack.md](07-linux-usb-stack.md) 的“设备侧”节")])
sub('11-android-usb.md',[("（见 `07-linux-usb-stack.md` §7）","（见 [07-linux-usb-stack.md](07-linux-usb-stack.md) 的“设备侧”节）")])
sub('07-linux-usb-stack.md',[
 ("## USB/IP（网络虚拟 USB）\n\n","## USB/IP（网络虚拟 USB）\n\n报文格式、命令码与 UNLINK 语义见 [06-linux-virtual-usb.md](06-linux-virtual-usb.md)；那篇的“待确认项”称内核文档页未写端口号，本文的 3240 来自内核源码树的 `tools/usb/usbip/README`。\n\n"),
 ("## 设备侧：Gadget 框架（虚拟 USB 研究的核心）\n\n","## 设备侧：Gadget 框架（虚拟 USB 研究的核心）\n\nConfigFS 属性、FunctionFS 挂载流程与 Raw Gadget ioctl 的逐条定义见 [06-linux-virtual-usb.md](06-linux-virtual-usb.md)；本节只讲选型与组合。\n\n")])

# ---- post-process
def chunk_lists(s):
    out=[];lines=s.split('\n');i=0;cur=None
    res=[];sec=''
    # find sections 参考来源/待确认项, split bullets into groups of 8 with H3
    parts=re.split(r'(?m)^(## .*)$',s)
    new=[parts[0]]
    for j in range(1,len(parts),2):
        h,b=parts[j],parts[j+1]
        if h.startswith('## 参考来源') or h.startswith('## 待确认项'):
            items=[l for l in b.split('\n') if l.startswith('- ')]
            if len(items)>9:
                nb='\n'
                for k in range(0,len(items),8):
                    g=items[k:k+8]
                    lab=(f'来源组 {k//8+1}' if h.startswith('## 参考来源') else f'待确认组 {k//8+1}')
                    nb+=f'\n### {lab}\n\n'+'\n'.join(g)+'\n'
                b=nb+'\n'
        new+= [h,b]
    return ''.join(new)
for f,_ in [(c['out'],0) for c in cfgs]:
    s=open(P+f).read()
    s=chunk_lists(s)
    if f.startswith(('09','11','12')):
        s=s.replace('flowchart TB\n    %% level: L1\n','flowchart TB\n    %% level: L1\n    %% size: large\n',1)
    s=s.replace('"Usbhub3 / Ucx01000 / Usbxhci / hidclass"','"Usbhub3 / Ucx01000<br/>Usbxhci / hidclass"')
    s=s.replace('["usb-c-connector<br/>CC / VBUS"]','["usb-c-connector<br/>CC / VBUS"]')
    s=s.replace('macOS 自 Big Sur 起不再支持 **IOUSBFamily 与 IOHIDFamily 的全部 KPI**','macOS 11（Big Sur）起不再支持 **IOUSBFamily 与 IOHIDFamily 的全部 KPI**')
    open(P+f,'w').write(s)

# ---- split semicolon-heavy table rows
def split_rows(s):
    out=[]
    for l in s.split('\n'):
        if l.startswith('| ') and l.count('；')>=2 and l.count('|')>=5:
            cells=[c.strip() for c in l.strip().strip('|').split('|')]
            # find the cell with most ；
            k=max(range(len(cells)),key=lambda i:cells[i].count('；'))
            if cells[k].count('；')>=2:
                segs=cells[k].split('；')
                for n,seg in enumerate(segs):
                    nc=list(cells)
                    nc[k]=seg
                    if n>0:
                        nc[0]=cells[0]+'.'+str(n+1) if cells[0].isdigit() else cells[0]
                    out.append('| '+' | '.join(nc)+' |')
                continue
        out.append(l)
    return '\n'.join(out)
for c in cfgs:
    s=open(P+c['out']).read()
    s=split_rows(s)
    s=s.replace("DWC3 / DWC2 / ChipIdea / Cadence / MUSB</span>","DWC3 / DWC2 / ChipIdea<br/>Cadence / MUSB</span>").replace('DWC3 / DWC2 / ChipIdea / Cadence / MUSB"]','DWC3 / DWC2 / ChipIdea<br/>Cadence / MUSB"]')
    open(P+c['out'],'w').write(s)
