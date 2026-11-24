import os
OUT=os.environ.get("FIG_OUT",os.path.join(os.path.dirname(os.path.abspath(__file__)),"output"))
os.makedirs(OUT,exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({"font.family":"sans-serif","font.sans-serif":["Arial","Liberation Sans","DejaVu Sans"],"font.size":8,"pdf.fonttype":42,"ps.fonttype":42})
MM=1/25.4; W,H=130,158
fig=plt.figure(figsize=(W*MM,H*MM)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(10,178); ax.axis("off")
INK="#000000"; DARK="#000000"; GREY="#000000"; RAIL="#0072B2"
T_BLUE,T_ORANGE,T_GREEN="#DCEBF7","#FBE3D2","#DCF0E4"
LS=1.32  # line pitch factor (mm per pt approx)
contained=[]
def box(x,y,w,h,lines,fc="white",lw=0.6):
    patch=FancyBboxPatch((x,y),w,h,boxstyle="square,pad=0",fc=fc,ec=INK,lw=lw)
    ax.add_patch(patch)
    yy=y+h-3.0
    for txt,kw in lines:
        size=kw.get("size",8); ind=kw.get("indent",0)
        text=ax.text(x+2.4+ind,yy,txt,ha="left",va="top",fontsize=size,color=kw.get("color",DARK),weight=kw.get("weight","normal"))
        contained.append((patch,text))
        yy-=size*0.44+kw.get("gap",0)
def arrow(p,q):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle="-|>",mutation_scale=7,lw=0.8,color=INK,shrinkA=0,shrinkB=0))
B={"weight":"bold","size":8}; N={"size":8}; S={"size":8,"color":GREY,"indent":2.2}
mx,mw=11,63; rx,rw=78,51.5; mc=mx+mw/2
# header
ax.add_patch(FancyBboxPatch((mx,170),rx+rw-mx,7,boxstyle="square,pad=0",fc=RAIL,ec=INK,lw=0.6))
ax.text((mx+rx+rw)/2,173.5,"Identification of studies via databases",ha="center",va="center",fontsize=8.5,weight="bold",color="white")
# rows (y,h)
id_y,id_h=141,26
box(mx,id_y,mw,id_h,fc=T_BLUE,lines=[("Records identified from databases",B),("(n = 24,925)",B),
    ("Scopus 11,333 · Web of Science 6,286",S),("IEEE Xplore 1,862 · ACM DL 5,444†",S),
    ("By branch: S1 313 · S2 14,082",S),("targeted S3 10,530",dict(S,indent=12.2))])
box(rx,id_y,rw,id_h,fc=T_ORANGE,lines=[("Before screening",B),
    ("Duplicate or overlapping branch",S),("records (n = 9,197)",dict(S,indent=4.5)),
    ("Marked ineligible by automation",S),("tools‡ (n = 14,436)",dict(S,indent=4.5)),
    ("Other reasons (n = 0)",S)])
arrow((mx+mw,id_y+id_h/2),(rx,id_y+id_h/2))
sc_y,sc_h=115,21
box(mx,sc_y,mw,sc_h,fc=T_BLUE,lines=[("Records screened by authors",B),("(n = 1,292)",B),("S1/S2 family 919 · targeted S3 373",S),("title, abstract, and keywords",S)])
box(rx,sc_y+2,rw,sc_h-4,fc=T_ORANGE,lines=[("Records excluded by authors",B),("(n = 988)",S)])
arrow((mx+mw,sc_y+sc_h/2),(rx,sc_y+sc_h/2))
arrow((mc,id_y),(mc,sc_y+sc_h))
cons_y=106
box(rx,cons_y-6,rw,12,[("Related reports consolidated",N),("into study families (n = 14)",N)],fc="white")
ro_y,ro_h=82,16
arrow((mc,sc_y),(mc,ro_y+ro_h))
ax.plot([mc,rx],[cons_y,cons_y],color=INK,lw=0.6); arrow((rx-0.01,cons_y),(rx,cons_y))
box(mx,ro_y,mw,ro_h,fc=T_BLUE,lines=[("Reports sought for retrieval",B),("(n = 290)",B),("304 retained less 14 consolidated",S)])
box(rx,ro_y-2,rw,18,fc=T_ORANGE,lines=[("Reports not assessed (n = 6)",B),("Not retrieved (n = 4)",S),("Ineligible at retrieval closure",S),("(n = 2)",dict(S,indent=4.5))])
arrow((mx+mw,ro_y+ro_h/2),(rx,ro_y+ro_h/2))
el_y,el_h=52,14
arrow((mc,ro_y),(mc,el_y+el_h))
box(mx,el_y,mw,el_h,fc=T_BLUE,lines=[("Reports assessed for eligibility",B),("(n = 284), full text",B)])
ex_y,ex_h=44,30
box(rx,ex_y,rw,ex_h,fc=T_ORANGE,lines=[("Reports excluded (n = 47)",B),
    ("S1: no implemented agent",S),("(n = 2)",dict(S,indent=4.5)),
    ("S2: eligibility failures (n = 31)",S),
    ("S3: no reusable method (n = 13)",S),
    ("Retracted publication (n = 1)",S)])
arrow((mx+mw,el_y+el_h/2),(rx,el_y+el_h/2))
in_y,in_h=12,28
arrow((mc,el_y),(mc,in_y+in_h))
box(mx,in_y,mw,in_h,fc=T_GREEN,lines=[("Studies included in review (n = 237)",B),("S1 Engineering agents 40",S),("S2 Agent security 134",S),("S3 Computational assurance 63",S),("Reports of included studies",B),("(n = 237)",B)],lw=1.0)
# phase rail
for lab,y0,y1 in (("Identification",id_y,id_y+id_h),("Screening",el_y,sc_y+sc_h),("Included",in_y,in_y+in_h)):
    ax.add_patch(FancyBboxPatch((2,y0),7,y1-y0,boxstyle="square,pad=0",fc=RAIL,ec=INK,lw=0.6))
    ax.text(5.5,(y0+y1)/2,lab,rotation=90,ha="center",va="center",fontsize=8.5,weight="bold",color="white")
fig.canvas.draw();renderer=fig.canvas.get_renderer()
for patch,text in contained:
    outer,inner=patch.get_window_extent(renderer),text.get_window_extent(renderer)
    assert inner.x0>=outer.x0 and inner.x1<=outer.x1 and inner.y0>=outer.y0 and inner.y1<=outer.y1,text.get_text()
for ext,kw in (("pdf",{}),("png",{"dpi":220})):
    fig.savefig(f"{os.environ.get('FIG_PREVIEW',OUT) if ext=='png' else OUT}/fig02_prisma_flow.{ext}",facecolor="white",bbox_inches="tight",pad_inches=0.02,**kw)
