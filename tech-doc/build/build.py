import re,sys,os
# 仓库内路径：本文件在 tech-doc/build/。源笔记不入库，用 USB_OS_KB 指向
# 含 01-linux.md … 06-cross-platform-comparison.md 的目录（默认同目录 os-kb/）。
# 输出默认写到 tech-doc/（与 00–06 同级），可用 TECH_DOC_OUT 覆盖。
_HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.environ.get('USB_OS_KB') or os.path.join(_HERE,'os-kb')
OUT=os.environ.get('TECH_DOC_OUT') or os.path.dirname(_HERE)
CLS={'app':'classDef renderer fill:#dbeafe,stroke:#2563eb,color:#1e3a8a',
     'drv':'classDef driver fill:#fee2e2,stroke:#dc2626,color:#7f1d1d',
     'hw':'classDef outside fill:#f3f4f6,stroke:#6b7280,color:#374151',
     'own':'classDef main fill:#ffedd5,stroke:#ea580c,color:#7c2d12',
     'svc':'classDef service fill:#dcfce7,stroke:#16a34a,color:#14532d',
     'dec':'classDef decision fill:#ffffff,stroke:#334155,color:#0f172a,stroke-width:1.5px'}
NAME={'app':'renderer','drv':'driver','hw':'outside','own':'main','svc':'service'}
def mm(body,classes):
    # classes: dict cls-> list of node ids
    s="```mermaid\nflowchart TB\n    %% level: L1\n"+body.strip('\n')+"\n"
    used=set(classes)
    for k in classes: s+="    "+CLS[k]+"\n"
    for k,ids in classes.items(): s+="    class "+",".join(ids)+" "+NAME[k]+"\n"
    return s+"```\n"
REN=[('01-linux.md','07-linux-usb-stack.md'),('02-arm-embedded.md','08-arm-embedded-usb.md'),('03-macos.md','09-macos-usb.md'),
     ('04-ios-ipados.md','10-ios-ipados-usb.md'),('05-android.md','11-android-usb.md'),('06-cross-platform-comparison.md','12-cross-platform-comparison.md')]
def load(f):
    s=open(f'{SRC}/{f}').read()
    s=s.split('---\n',2)[2]
    for a,b in REN: s=s.replace(a,b)
    return s
def sections(s):
    parts=re.split(r'(?m)^## ',s); head=parts[0]; secs=[]
    for p in parts[1:]:
        t,_,b=p.partition('\n'); secs.append((t.strip(),b))
    return head,secs
def pend(text):
    items=[]
    for l in text.split('\n'):
        if '待核实' in l and not l.startswith('>') and not l.startswith('```'):
            l=re.sub(r'\s+',' ',l.strip(' |-*'))
            i=l.find('待核实'); a=max(0,i-70); 
            seg=l[a:i+60]
            items.append(seg)
    return items
def build(cfg):
    s=load(cfg['src']); head,secs=sections(s)
    out=[f"# {cfg['title']}\n",
         f"> 类型：arch ｜ 模式：Reverse ｜ 代码基线：`{cfg['baseline']}` ｜ 最后核对：2026-11-28 ｜ 范围：`{cfg['scope']}` ｜ lang: zh\n",
         "## Overview\n",cfg['overview'].strip()+"\n"]
    allbody=''
    for t,b in secs:
        if t.startswith('参考来源'):
            continue
        t2=re.sub(r'^\d+\.\s*','',t)
        t2=cfg.get('rename',{}).get(t2,t2)
        b=cfg.get('sub',lambda x,y:y)(t2,b)
        # replace mermaid
        if '```mermaid' in b:
            b=re.sub(r'```mermaid.*?```\n',lambda m:cfg['diagram']+(cfg.get('caption','')),b,flags=re.S)
        allbody+=b
        out.append(f"## {t2}\n\n{b.strip()}\n")
    refs=[b for t,b in secs if t.startswith('参考来源')][0]
    out.append("## 参考来源\n\n"+refs.strip()+"\n")
    full='\n'.join(out)
    items=pend(full)
    out.append("## 待确认项\n\n"+'\n'.join(f"- [ ] …{x}…" for x in items)+"\n")
    open(f"{OUT}/{cfg['out']}",'w').write('\n'.join(out))
