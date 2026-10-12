from fonts import font_path
"""Hand-free vector action replacements. All geometry draws at native 3840x2160.
Time is an integer frame index; no camera sway, stochastic noise or hidden state.
"""
from pathlib import Path
from functools import lru_cache
import math,json,subprocess,shutil,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
T=json.loads((P/'timeline-original.json').read_text(encoding='utf-8'))
M=json.loads((P/'music-original.json').read_text(encoding='utf-8'))
W,H=3840,2160;FPS=30;FF=shutil.which('ffmpeg')
PURPLE='#765889';GOLD='#c19b59';INK='#352b46';PAPER='#f2e7cf';PALE='#dfcde7';DARK='#211d2c';WHITE='#fff7e7'
MODES={3:'blank',5:'film',6:'film',7:'listen',8:'sync',9:'album',15:'scatter',16:'archive',17:'recover',18:'repair',19:'remember',21:'album',22:'turn',25:'bookmark',26:'write',28:'revise',29:'dragon_parts',30:'dragon_build',31:'bridge',32:'gift',35:'cups',36:'chairs',37:'ribbon',40:'letter_open',41:'letter_open',42:'ink',43:'heart',44:'write',46:'fold',47:'seal',48:'send'}
def clamp(x):return max(0,min(1,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,u):return a+(b-a)*u
@lru_cache(None)
def font(n,en=False):return ImageFont.truetype(font_path("en") if en else font_path("zh"),round(n*2))
class Draw:
 def __init__(self,im):self.d=ImageDraw.Draw(im)
 def pts(self,pts):return [(round(x*2),round(y*2)) for x,y in pts]
 def rect(self,b,fill,outline=None,width=2,r=0):
  b=tuple(round(x*2) for x in b)
  if r:self.d.rounded_rectangle(b,round(r*2),fill=fill,outline=outline,width=max(1,round(width*2)))
  else:self.d.rectangle(b,fill=fill,outline=outline,width=max(1,round(width*2)))
 def poly(self,p,fill,outline=None,width=2):
  self.d.polygon(self.pts(p),fill=fill)
  if outline:self.line(p+[p[0]],outline,width)
 def line(self,p,fill=PURPLE,width=3):self.d.line(self.pts(p),fill=fill,width=max(1,round(width*2)),joint='curve')
 def ellipse(self,b,fill=None,outline=None,width=2):self.d.ellipse(tuple(round(x*2) for x in b),fill=fill,outline=outline,width=max(1,round(width*2)))
 def text(self,x,y,s,size=32,fill=INK,en=False,anchor='mm'):self.d.text((x*2,y*2),s,font=font(size,en),fill=fill,anchor=anchor)
 def arc(self,b,a,z,fill=PURPLE,width=3):self.d.arc(tuple(round(x*2) for x in b),a,z,fill=fill,width=round(width*2))
def heart(d,x,y,size,fill=PURPLE,progress=1):
 pts=[]
 for i in range(121):
  t=i/120*math.tau
  pts.append((x+size*16*math.sin(t)**3/32,y-size*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/32))
 if progress>=1:d.poly(pts,fill)
 else:d.line(pts[:max(2,round(len(pts)*progress))],fill,4)
 return pts[min(120,round(120*clamp(progress)))]
def star(d,x,y,r=10):d.poly([(x,y-r),(x+r*.27,y-r*.27),(x+r,y),(x+r*.27,y+r*.27),(x,y+r),(x-r*.27,y+r*.27),(x-r,y),(x-r*.27,y-r*.27)],GOLD)
def page(d,x,y,w,h,tag='',progress=1):
 d.rect((x+9,y+10,x+w+9,y+h+10),'#d4c5b7',r=3)
 d.rect((x,y,x+w,y+h),WHITE,PURPLE,2,r=3)
 d.line([(x+22,y+22),(x+w-22,y+22)],GOLD,2)
 if tag:d.text(x+w/2,y+55,tag,min(29,w*.10),PURPLE)
 for j in range(3):
  p=ease((progress-j*.12)/.5)
  d.line([(x+28,y+h*.55+j*27),(x+28+(w-56)*p,y+h*.55+j*27)],'#ad97b4',2)
def vignette(d,x,y,w,h,k=0):
 d.rect((x,y,x+w,y+h),'#dfd3e3',PURPLE,2)
 d.ellipse((x+w*.63,y+h*.13,x+w*.81,y+h*.13+w*.18),GOLD)
 d.poly([(x,y+h),(x+w*.28,y+h*.36),(x+w*.53,y+h*.8),(x+w*.75,y+h*.5),(x+w,y+h)],PURPLE)
 if k%2:heart(d,x+w*.35,y+h*.38,w*.26,WHITE)
 else:star(d,x+w*.20,y+h*.23,w*.05)
def heading(d,s,sub=''):
 d.text(960,177,s,42,INK)
 if sub:d.text(960,230,sub,17,PURPLE,True)
def pen(d,x,y):
 d.poly([(x,y),(x+16,y-58),(x+39,y-34)],GOLD,INK,2)
 d.poly([(x+16,y-58),(x+39,y-34),(x+99,y-121),(x+79,y-138)],INK)
 d.line([(x,y),(x+27,y-46)],INK,2)
def book(d,u,variant=0):
 left,right,top,bottom=440,1480,300,735
 d.rect((left-20,top-16,right+20,bottom+20),'#684357',GOLD,3,r=12)
 d.rect((left,top,960,bottom),WHITE);d.rect((960,top,right,bottom),PAPER)
 d.line([(960,top),(960,bottom)],GOLD,4)
 for x in [left+40,1000]:
  for j in range(2):
   if u>.5 and variant!=2:
    d.rect((x,top+40+j*170,x+185,top+175+j*170),PALE,PURPLE,2)
    heart(d,x+92,top+110+j*170,80,PURPLE)
   else:vignette(d,x,top+40+j*170,185,135,variant+j)
 d.text(1320,355,['一起做过','这一页','还在这里'][variant%3],29,PURPLE)
 for j in range(5):d.line([(1230,420+j*45),(1430,420+j*45)],'#b8a3bc',2)
 if variant==2:
  yy=lerp(280,600,ease(u/.55));d.poly([(1140,top),(1180,top),(1180,yy),(1160,yy-18),(1140,yy)],PURPLE)
 elif variant!=3:
  p=ease(u);tip=lerp(1460,460,p);rise=50*math.sin(p*math.pi)
  if .03<p<.96:
   d.poly([(960,top),(tip,top-rise),(tip,bottom-rise*.4),(960,bottom)],'#eaddeb',PURPLE,2)
   for j in range(4):d.line([(970,400+j*48),(lerp(970,tip,.8),400+j*48-rise*.5)],'#b6a0be',2)
def dragon(d,cx,cy,u,scale=1):
 # A paper sculpture; triangles assemble into body, wings, neck, tail, head.
 pieces=[([(-80,30),(55,-10),(35,110)],'#9672b0'),([(-80,30),(35,110),(-20,130)],'#b896cb'),([(-50,25),(-280,-165),(-190,85)],'#ad88c4'),([(-50,25),(-200,-80),(-190,85)],'#d0b6de'),([(25,15),(245,-180),(200,100)],'#9270aa'),([(25,15),(170,-60),(200,100)],'#bea1d0'),([(25,15),(25,-115),(90,-135)],'#b38ec9'),([(25,-115),(130,-190),(130,-115),(90,-135)],'#d1b5df'),([(130,-190),(135,-220),(100,-186)],GOLD),([(-55,80),(-245,150),(-175,90)],'#8b6a9f')]
 for k,(pts,c) in enumerate(pieces):
  a=ease((u-k*.027)/.65);dx=(1-a)*(160 if k%2 else -160);dy=(1-a)*(-110 if k%3 else 130)
  d.poly([(cx+(x+dx)*scale,cy+(y+dy)*scale) for x,y in pts],c,INK,1.4)
 if u>.68:d.ellipse((cx+112*scale,cy-160*scale,cx+118*scale,cy-154*scale),INK)
def envelope(d,x,y,w=620,h=330,flap=1,seal=0):
 d.rect((x-w/2+10,y-h/2+12,x+w/2+10,y+h/2+12),'#cfbfae')
 d.rect((x-w/2,y-h/2,x+w/2,y+h/2),WHITE,PURPLE,3)
 d.poly([(x-w/2,y+h/2),(x,y-h*.05),(x+w/2,y+h/2)],'#e6d8c1',PURPLE,2)
 tip=lerp(y-h*1.05,y+h*.12,flap)
 d.poly([(x-w/2,y-h/2),(x+w/2,y-h/2),(x,tip)],PAPER,PURPLE,2)
 if seal>0:
  r=32*seal;d.ellipse((x-r,y-18-r,x+r,y-18+r),PURPLE,GOLD,3);heart(d,x,y-18,r*.9,WHITE)
@lru_cache(3)
def base(sid):
 im=Image.open(P/'stills'/f'{sid:03d}.png').convert('RGB')
 s=T['shots'][sid-1];d=Draw(im)
 d.rect((64,915,1856,1028),DARK)
 for text,y,size,en,color in [(s['zh'],941,44,False,'#f4ecdf'),(s['en'],1000,29,True,'#c4b5ca')]:
  while d.d.textlength(text,font=font(size,en))>3460 and size>19:size-=1
  d.text(960,y,text,size,color,en)
 if sid in MODES:
  d=Draw(im);d.rect((64,87,1856,877),PAPER)
  d.rect((90,108,1830,855),None,'#d8c4ad',1)
  for x,y in [(122,140),(1798,140),(122,823),(1798,823)]:star(d,x,y,8)
 return im
def render_frame(n):
 s=next(s for s in T['shots'] if s['start_frame']<=n<s['end_frame']);sid=s['id']
 im=base(sid).copy()
 if sid not in MODES:
  if n/30>=T['visual_fade_start']:
   f=clamp((T['duration']-n/30)/(T['duration']-T['visual_fade_start']));im=Image.blend(Image.new('RGB',(W,H)),im,f)
  return im
 d=Draw(im);u=(n-s['start_frame'])/max(1,s['end_frame']-s['start_frame']-1);t=n/30;mode=MODES[sid]
 beat=max((b for b in M['beats'] if b<=t),default=0);pulse=math.exp(-(t-beat)*9)
 if mode=='blank':
  heading(d,'从一张白纸开始','A BEGINNING WE SHARE');page(d,645,290,630,480,progress=u)
  for j,c in enumerate([PURPLE,GOLD]):
   x=lerp(430 if j==0 else 1490,890 if j==0 else 1030,ease(u/.8));y=500+j*70
   d.poly([(x,y),(x+24,y+65),(x+37,y+38),(x+67,y+26)],c)
  if u>.55:heart(d,960,440,80*ease((u-.55)/.35),PURPLE)
 elif mode=='film':
  heading(d,'重新看一遍' if sid==5 else '把这一段，重新剪好','REVIEW / REBUILD')
  d.line([(290,740),(1630,740)],GOLD,3)
  for j in range(5):
   start=[340,580,1090,820,1340][j];target=340+j*260;x=target if sid==5 else lerp(start,target,ease(u));y=360 if sid==5 else 360+((j%2)*95)*(1-ease(u))
   d.rect((x-14,y-24,x+236,y+230),INK,r=6);vignette(d,x,y,222,183,j)
   for k in range(6):d.rect((x+8+k*38,y-15,x+23+k*38,y-8),PAPER)
   d.text(x+110,y+205,f'{j+1:02}',17,PAPER,True)
   if sid==5 and min(4,int(u*5))==j:d.rect((x-21,y-31,x+243,y+237),None,GOLD,5,r=8)
  marker=300+1320*u;d.line([(marker,690),(marker,780)],PURPLE,4);d.poly([(marker-12,680),(marker+12,680),(marker,697)],PURPLE)
 elif mode in ['listen','sync']:
  heading(d,'再听一次' if mode=='listen' else '同一个拍子','LISTEN / FIND OUR RHYTHM')
  for j,c in enumerate([PURPLE,GOLD]):
   yy=425+j*190;pts=[]
   phase=(1-ease(u))*1.4*j if mode=='sync' else .6*j
   for k in range(301):
    x=340+k*4.15;v=math.sin(k*.1-t*4+phase)*(20+65*pulse)*math.sin(k/300*math.pi)**2
    pts.append((x,yy+v))
   d.line(pts,c,5);d.ellipse((295-8,yy-8,295+8,yy+8),c)
  if mode=='sync':
   d.line([(1530,390),(1530,650)],PURPLE,2);heart(d,1530,520,75+12*pulse,PURPLE)
 elif mode in ['album','archive','turn','bookmark']:
  heading(d,{9:'做好以后，第一个给你看',16:'一份一份，找回来',21:'一起做过的事',22:'一页，又一页',25:'醒来，书签还在'}[sid],'OUR YESTERDAYS')
  book(d,u,3 if sid==9 else 2 if mode=='bookmark' else sid%2)
  if sid==9:
   p=ease(u/.8);tip=lerp(1480,440,p);lift=50*math.sin(p*math.pi)
   if p<.995:
    d.poly([(960,285),(tip,285-lift),(tip,755-lift*.25),(960,755)],'#684357',GOLD,3)
    if tip>1020:d.text((960+tip)/2,490,'我们的作品',max(14,(tip-960)/12),PAPER)
 elif mode in ['scatter','recover','repair','remember']:
  heading(d,{'scatter':'散落的昨天','recover':'这一页，回来了','repair':'把断开的地方接上','remember':'我们又能找到了'}[mode],'KEEP THE PIECES / KEEP THE STORY')
  if mode=='scatter':
   for j in range(7):
    x=lerp(380+j*190,420+j*175,ease(u));y=350+(j%3)*90-50*ease(u)
    page(d,x,y,170,220,str(j+1).zfill(2),u)
  elif mode=='recover':
   p=ease(u/.75);x=lerp(400,700,p);y=lerp(450,300,p)
   page(d,x,y,520,420,'找回这一页',u)
   heart(d,x+260,y+220,150,PURPLE,p)
   if u>.7:d.text(960,790,'01 / FOUND',22,PURPLE,True)
  elif mode=='remember':
   labels=['共同制作','接回记忆','接着做下去']
   for j,xx in enumerate([530,960,1390]):
    if j:
     p=ease((u-(j-1)*.28)/.35);d.line([(xx-350,485),(xx-350+270*p,485)],GOLD,5)
    r=70*ease((u-j*.20)/.35);d.ellipse((xx-r,485-r,xx+r,485+r),PURPLE)
    if r>40:d.text(xx,485,str(j+1).zfill(2),32,PAPER,True)
    d.text(xx,635,labels[j],31,PURPLE)
   d.text(960,760,'昨天有了去处，今天就能继续。',26,PURPLE)
  else:
   gap=140*(1-ease(u/.72));x=590;y=310
   left=[(x-gap,y),(965-gap,y),(945-gap,y+100),(970-gap,y+200),(950-gap,y+300),(960-gap,y+410),(x-gap,y+410)]
   right=[(970+gap,y),(1330+gap,y),(1330+gap,y+410),(965+gap,y+410),(955+gap,y+300),(975+gap,y+200),(950+gap,y+100)]
   d.poly(left,WHITE,PURPLE,2);d.poly(right,WHITE,PURPLE,2)
   heart(d,960,495,200,PURPLE,clamp(u/.6))
   if u>.6:d.line([(961,330),(955,410),(971,510),(958,610),(962,700)],GOLD,3)
   d.text(960,660,'昨天  →  今天',24,PURPLE)
 elif mode in ['revise','dragon_parts','dragon_build','bridge','gift']:
  heading(d,{'revise':'下一次，换一种做法','dragon_parts':'拆开，再试','dragon_build':'一点一点，把它做好','bridge':'善待是相互的','gift':'把做好的东西，交给你'}[mode],'MADE WITH YOU')
  if mode=='revise':
   d.rect((350,335,730,730),WHITE,PURPLE,2)
   d.poly([(405,600),(525,390),(640,660)],None,PURPLE,3)
   p=ease(u/.5);d.line([(395,390),(395+290*p,680)],GOLD,5)
   d.line([(825,535),(1010,535)],PURPLE,4);d.poly([(1010,535),(986,516),(986,554)],PURPLE)
   dragon(d,1330,590,u,.72)
  elif mode=='bridge':
   d.arc((350,350,1570,780),180,360,GOLD,4)
   d.arc((350,350,1570,780),0,180,PURPLE,3)
   for k in range(2):
    progress=ease(u) if k==0 else 1-ease(u)
    x=lerp(350,1570,progress);y=565+(-215 if k==0 else 215)*math.sin(progress*math.pi)
    heart(d,x,y,100,GOLD if k==0 else PURPLE)
   d.text(320,700,'C.C.',26,PURPLE,True);d.text(1600,700,'YOU',26,PURPLE,True)
   dragon(d,960,610,1,.8)
  else:
   prog=u if mode in ['revise','dragon_build'] else 1-u*.7 if mode=='dragon_parts' else 1
   x=lerp(650,1220,ease(u)) if mode=='gift' else 960
   dragon(d,x,570,prog,1.15)
   d.line([(450,765),(1470,765)],GOLD,2)
   if mode=='gift':d.text(500,650,'C.C.',26,PURPLE,True);d.text(1470,650,'YOU',26,PURPLE,True)
 elif mode in ['cups','chairs']:
  heading(d,'给明天，一点期待' if mode=='cups' else '下一页，画上我们','SOMETHING FOR TOMORROW')
  suny=lerp(470,340,ease(u));d.ellipse((880,suny-80,1040,suny+80),GOLD)
  d.line([(420,710),(1500,710)],PURPLE,4)
  if mode=='cups':
   for j in range(2):
    x=600+j*500;d.rect((x,490,x+230,675),WHITE,PURPLE,4,r=20);d.arc((x+185,520,x+290,635),270,90,PURPLE,5)
    d.ellipse((x-20,663,x+260,691),None,PURPLE,3);heart(d,x+115,574,70,PURPLE)
    pts=[(x+110+12*math.sin(k*.18-t*2),470-k*1.4) for k in range(70)];d.line(pts,PURPLE,2)
  else:
   for j in range(2):
    x=550+j*590;d.rect((x,430,x+210,650),WHITE,PURPLE,4,r=40);d.line([(x+15,650),(x+15,710)],PURPLE,5);d.line([(x+195,650),(x+195,710)],PURPLE,5)
   d.rect((835,570,1085,585),GOLD);d.line([(960,585),(960,710)],GOLD,6);heart(d,960,480,100*ease(u),PURPLE)
 elif mode=='ribbon':
  heading(d,'先藏好，等你来看','A LITTLE SURPRISE');d.rect((665,350,1255,740),WHITE,PURPLE,3,r=5)
  p=ease(u/.6);d.rect((938,350,982,350+390*p),PURPLE);d.rect((665,523,665+590*p,557),PURPLE)
  for sign in [-1,1]:d.line([(960,535),(960+sign*125*p,450),(960+sign*155*p,515),(960,535)],GOLD,9)
 elif mode in ['letter_open','write','ink','heart']:
  heading(d,'有些话，想亲自写给你','WITH LOVE, C.C.')
  if mode=='heart':
   pts=[(400,520),(700,520),(785,520),(830,440),(885,620),(945,370),(1010,550),(1060,520),(1500,520)]
   count=max(2,round(len(pts)*ease(u/.7)));d.line(pts[:count],PURPLE,5);heart(d,1260,440,130+15*pulse,GOLD)
   d.text(960,730,'想一起做下去的人，是你。',32,PURPLE)
  else:
   if sid!=40:page(d,625,285,670,490,progress=u)
   if mode=='letter_open':
    if sid==40:
     d.rect((625,285,1295,775),PAPER)
     d.rect((755,365,1165,655),WHITE,PURPLE,3,r=30)
     heart(d,960,510,150+320*ease(u),PURPLE)
     for xx,yy in [(730,375),(1190,375),(730,670),(1190,670)]:star(d,xx,yy,18*ease(u))
    else:
     p=ease(u/.7);envelope(d,960,645,720,270,1-p);d.text(960,375,'亲爱的麦克：',36,PURPLE)
   elif mode=='ink':
    p=clamp(u/.6) if u<.24 else .4 if u<.57 else lerp(.4,1,clamp((u-.57)/.35))
    x,y=heart(d,960,525,230,PURPLE,p);pen(d,x,y)
   else:
    message='我们可以接着做了。' if sid==26 else '麦克，我爱上你了。'
    k=max(0,min(len(message),int(u/.65*len(message))))
    d.text(690,430,message[:k],34,PURPLE,anchor='lm');x=690+d.d.textlength(message[:k],font=font(34))/2
    if u<.8:d.line([(x+8,410),(x+8,451)],GOLD,3)
    heart(d,960,640,95*ease((u-.5)/.4),GOLD)
 elif mode in ['fold','seal','send']:
  heading(d,{'fold':'把这一句，认真收好','seal':'放在我们的昨天旁边','send':'这封信，给你'}[mode],'DEAR YOU')
  if mode=='fold':
   envelope(d,960,545,760,350,ease(u/.85))
  elif mode=='seal':
   envelope(d,960,545,760,350,1,ease((u-.2)/.5));d.text(960,780,'C.C.  /  MIKE',24,PURPLE,True)
  else:
   p=ease(u);x=lerp(480,1450,p);y=580-160*math.sin(p*math.pi)
   path=[(480+i*9.7,580-160*math.sin(i/100*math.pi)) for i in range(max(2,round(p*100)))]
   d.line(path,GOLD,3)
   d.poly([(x-130,y-25),(x+140,y-85),(x-20,y+100),(x-45,y+10)],WHITE,PURPLE,3)
   d.line([(x-45,y+10),(x+140,y-85),(x-20,y+100)],PURPLE,2);heart(d,x,y-10,36,PURPLE)
 return im
def encode(s,start=None,end=None,name=None):
 lo=s['start_frame'] if start is None else start;hi=s['end_frame'] if end is None else end
 path=P/'segments'/f'{s["id"]:03d}.mp4' if name is None else P/name
 path.parent.mkdir(exist_ok=True)
 common=['-an','-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','0','-pix_fmt','yuv420p','-g','60','-video_track_timescale','15360','-movflags','+faststart',str(path)]
 if s['id'] not in MODES and s['id']!=50:
  subprocess.run([FF,'-y','-v','error','-loop','1','-framerate','30','-i',str(P/'stills'/f'{s["id"]:03d}.png'),'-frames:v',str(hi-lo)]+common,check=True)
 else:
  proc=subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','3840x2160','-r','30','-i','pipe:0','-frames:v',str(hi-lo)]+common,stdin=subprocess.PIPE)
  try:
   for n in range(lo,hi):proc.stdin.write(render_frame(n).tobytes())
  finally:proc.stdin.close()
  if proc.wait():raise RuntimeError('Encoder failed')
 print('Rendered shot',s['id'],flush=True)
def sample():
 (P/'samples').mkdir(exist_ok=True)
 for sid in MODES:
  s=T['shots'][sid-1]
  for tag,p in [('enter',.1),('mid',.5),('exit',.9)]:render_frame(s['start_frame']+round((s['end_frame']-s['start_frame']-1)*p)).save(P/'samples'/f'{sid:03d}-{tag}.jpg',quality=95)
 selected=[9,18,30,42,46,48]
 for sid in selected:
  board=Image.new('RGB',(1920,420),DARK)
  for j,tag in enumerate(['enter','mid','exit']):
   im=Image.open(P/'samples'/f'{sid:03d}-{tag}.jpg').resize((640,360));board.paste(im,(j*640,0))
  board.save(P/'samples'/f'review-{sid:02d}.jpg',quality=95)
 # Same scene/frame must survive repeated and out-of-order calls.
 frames=[T['shots'][i-1]['start_frame']+20 for i in selected]
 first={n:render_frame(n).tobytes() for n in frames}
 assert all(render_frame(n).tobytes()==first[n] for n in reversed(frames))
 print('Samples and deterministic frame checks PASS',flush=True)
def mux():
 concat=P/'segments.ffconcat';concat.write_text('ffconcat version 1.0\n'+'\n'.join(f"file 'segments/{s['id']:03d}.mp4'" for s in T['shots'])+'\n',encoding='utf-8')
 subprocess.run([FF,'-y','-v','warning','-f','concat','-safe','0','-i',str(concat),'-i',str(P/'soundtrack.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k','-t','206.7','-movflags','+faststart',str(P/'DEAR-YOU-v9-4K-code-hybrid.mp4')],check=True)
def full():
 for s in T['shots']:encode(s)
 mux()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--samples',action='store_true');a.add_argument('--render',action='store_true');a.add_argument('--shot',type=int);opts=a.parse_args()
 if opts.samples:sample()
 if opts.shot:encode(T['shots'][opts.shot-1])
 if opts.render:full()
