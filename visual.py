from fonts import font_path
"""V12: Chinese letter text projected onto the physical paper and label."""
from legacy import *
from PIL import ImageOps,ImageEnhance
import legacy as old
import paper_ink
import book_planes as book
P=Path(__file__).resolve().parent
OUT='DEAR-YOU-v12-4K-chinese-letter.mp4'
retained_renderer=old.render_frame
AW,AH=3584,1580
REPAIRED={3,26,41,44,48}

def story_step(s,t,parts):
 """Partition this shot on its real music beats; no early saturated counter."""
 ev=local_beats(s);dur=(s['end_frame']-s['start_frame'])/30
 cuts=sorted(set(min(ev,key=lambda b:abs(b-dur*j/parts)) for j in range(1,parts))) if ev else []
 k=sum(t>=b for b in cuts)
 return k,t-(cuts[k-1] if k else 0),cuts

@lru_cache(48)
def work_picture(name,w,h):
 if name=='stickers':
  # Preserve every individual expression instead of cropping two wide galleries.
  im=Image.new('RGB',(w,h),'#211d2c');index=0;cw=w//6;ch=h//5
  for sid in [12,14]:
   src=Image.open(P/'stills'/f'{sid:03d}.png').convert('RGB')
   for e in T['shots'][sid-1]['expression_boxes']:
    tile=ImageOps.contain(src.crop(tuple(e['box'])),(cw-14,ch-14),method=Image.Resampling.LANCZOS)
    im.paste(tile,(index%6*cw+(cw-tile.width)//2,index//6*ch+(ch-tile.height)//2));index+=1
  return im
 elif name=='mv':im=photo(1,1600,900)
 else:im=asset('dragon-gift')
 return ImageOps.fit(im,(w,h),method=Image.Resampling.LANCZOS)

@lru_cache(48)
def work_card_asset(name,w,h,angle=0):
 p=Image.new('RGBA',(w+32,h+96),'#efdfc7');p.paste(work_picture(name,w,h),(16,16))
 d=ImageDraw.Draw(p)
 d.text(((w+32)//2,h+55),{'mv':'OUR FIRST CUT','stickers':'30 EXPRESSIONS','dragon':'MADE TOGETHER'}[name],font=font(15,True),fill='#68435e',anchor='mm')
 p=p.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 sh=Image.new('RGBA',p.size,(15,6,22,0));sh.putalpha(p.getchannel('A').point(lambda x:round(x*.55)))
 return p,sh

def work_card(im,name,x,y,w,h,angle=0):
 p,sh=work_card_asset(name,w,h,angle);im.paste(sh,(round(x)+13,round(y)+17),sh);im.paste(p,(round(x),round(y)),p)

@lru_cache(8)
def _work_spread(names):
 im=view('album').copy()
 left,right=book.sheet(),book.sheet()
 if 'mv' in names:
  book.mount(left,work_picture('mv',1100,700),135,370,1100,700)
  book.note(left,'OUR FIRST CUT',700,1190)
 if 'portrait' in names:
  # Album pages hold photographic memories; sticker grids stay on the desk.
  book.mount(right,photo(10,1100,520),110,200,1100,520)
  book.note(right,'OUR YESTERDAYS',700,825,28)
 if 'dragon' in names:
  book.mount(right,work_picture('dragon',1100,380),110,930,1100,380)
  book.note(right,'MADE TOGETHER',700,1450,28)
 book.note(left,'C.C. + MIKE',700,1330,42)
 book.project(im,left,'left');book.project(im,right,'right')
 return im

def work_spread(names=('mv','portrait','dragon')):
 return _work_spread(names).copy()

def continuity_scene(s,t):
 sid=s['id'];k,dt,cuts=story_step(s,t,4 if sid in [16,18,21] else 3)
 if sid==16:
  im=view('desk').copy()
  for j,name in enumerate(['mv','stickers','dragon']):
   if j<=k:work_card(im,name,330+j*1010,390+(j%2)*100,870,570,[-3,1,3][j])
  if k==3:im=work_spread()
 elif sid==17:
  im=work_spread(('mv',) if k==0 else ('mv','portrait'))
  if k==2:im=work_spread()
 elif sid==18:
  if k>=3:
   im=work_spread();d=ImageDraw.Draw(im)
   d.text((1050,1300),'PRESERVED.  CONTINUING.',font=font(18,True),fill='#68435e',anchor='mm')
  else:
   im=view('desk').copy();d=ImageDraw.Draw(im)
   # The same recovered MV image starts as physically separated pieces.
   pic=work_picture('mv',2000,920)
   gap=340 if k==0 else round(340*(1-ease(dt/.32))) if k==1 else 0
   left=Image.new('RGB',(1018,950),'#eddbc1');left.paste(pic.crop((0,0,1000,920)),(9,15))
   right=Image.new('RGB',(1018,950),'#eddbc1');right.paste(pic.crop((1000,0,2000,920)),(9,15))
   x=AW//2-1018;im.paste(left,(x-gap//2,270));im.paste(right,(x+1018+gap//2,270))
   d=ImageDraw.Draw(im)
   if k==2:
    # On the next musical phrase the missing section is visibly stitched.
    reach=ease(dt/.35)
    for y in range(285,round(285+900*reach),45):d.line((AW//2-22,y,AW//2+22,y+19),fill='#ffdb9d',width=7)
   d.text((AW//2,1350),['SCATTERED','FOUND THE MATCH','JOINED THE EDGES'][k],font=font(25,True),fill='#f0dbb7',anchor='mm')
 elif sid==19:
  im=work_spread()
  # The first project, her photograph and the shared gift have distinct closeups.
  side,region=[('left',(110,340,1290,1250)),('right',(80,170,1270,875)),('right',(80,900,1270,1500))][k]
  im=book.closeup(im,side,region)
 else:
  name=['mv','stickers','dragon','dragon'][k]
  if k==3:im=work_spread()
  else:
   im=view('desk').copy();work_card(im,name,720,170,2060,1100,0)
 return im

def shared_page_scene(s,t):
 k,dt,cuts=story_step(s,t,2)
 # First the watercolor pair, then the entire visibly open book.
 return view('shared-page',(.15,.17,.85,.84) if k==0 else None).copy()

def writing_scene(s,t,signed=False):
 lines=paper_ink.CONFIG['letter_lines']
 if signed:
  k,dt,cuts=story_step(s,t,3)
  words=paper_ink.CONFIG['confession'];count=round(len(words)*ease(t/.85))
  rows=[(line,105,190+j*180,56) for j,line in enumerate(lines)]
  rows.append((words[:count],105,910,60))
  if k>=1:
   signature=paper_ink.CONFIG['signature']
   rows.append((signature[:round(len(signature)*ease(dt/.5))] if k==1 else signature,410,1150,54))
  im=view('letter');rows=tuple(rows)
  if k==0:return paper_ink.closeup(im,(50,115,950,995),rows)
  focus=[(paper_ink.CONFIG['confession'],105,910,60),(paper_ink.CONFIG['signature'],410,1150,54)]
  if k==1:return paper_ink.text_closeup(im,focus,rows)
  return paper_ink.closeup(im,(50,110,970,1240),rows)
 k,dt,cuts=story_step(s,t,len(lines)+1)
 rows=[]
 for j,line in enumerate(lines):
  begin=0 if j==0 else cuts[min(j-1,len(cuts)-1)]
  rows.append((line[:round(len(line)*ease((t-begin)/.60))],105,190+j*180,56))
 im=paper_ink.compose(view('letter'),tuple(rows))
 if k>=len(lines):
  im=paper_ink.closeup(view('letter'),(50,115,950,825),rows)
 return im

def confession_scene(s,t):
 sid=s['id'];k,dt,cuts=story_step(s,t,3)
 if sid==40:
  if k==0:
   im=view('desk').copy();work_card(im,'stickers',620,190,2230,1140,0)
  elif k==1:im=view('hesitation').copy()
  else:
   # Follow her gaze to the still-unwritten letter, no repeated portrait insert.
   im=view('hesitation',(.05,.61,.67,.95)).copy()
 elif sid==41:return writing_scene(s,t)
 elif sid==42:
  if k==0:im=view('letter',(.08,.20,.31,.46)).copy() # actual gold nib at rest
  elif k==1:im=view('hesitation',(.40,.23,.89,.69)).copy() # uncertain eyes
  else:im=view('hesitation').copy() # reason for the pause
 elif sid==43:
  if k==0:im=work_spread()
  elif k==1:im=view('dragon-gift').copy()
  else:im=view('shared-page').copy() # wanting to continue with this person
 else:return writing_scene(s,t,signed=True)
 return im

def delivery_scene(s,t):
 sid=s['id'];k,dt,cuts=story_step(s,t,2 if sid!=47 else 3)
 if sid==46:
  # Folded sheet -> open envelope. Both are new physical states.
  return view('folded-letter',(.20,.25,.67,.86) if k==0 else None).copy()
 if sid==47:
  if k==0:return work_spread(('mv','portrait'))
  if k==1:return view('dragon-gift').copy()
  return work_spread()
 rows=((paper_ink.CONFIG['recipient'],175,80,66),)
 im=paper_ink.compose(view('letter-for-you'),rows,'label')
 # The last view addresses the viewer; no additional photo or content sway.
 if k==1:
  # Match the original fit camera while projecting the address at final size.
  im=paper_ink.camera_compose(view('letter-for-you'),(610,453,2840,1437),rows,'label')
 return im

@lru_cache(32)
def asset(name):
 return Image.open(P/'assets'/f'{name}.png').convert('RGB')

@lru_cache(64)
def view(name,box=None):
 im=asset(name)
 if box:im=im.crop(tuple(round(v*sz) for v,sz in zip(box,[im.width,im.height,im.width,im.height])))
 return ImageOps.fit(im,(AW,AH),method=Image.Resampling.LANCZOS)

@lru_cache(40)
def photo(sid,w,h):
 s=T['shots'][sid-1];im=Image.open(P/'stills'/f'{sid:03d}.png').convert('RGB').crop(tuple(s.get('art_box',[516,174,3324,1754])))
 return ImageOps.fit(im,(w,h),method=Image.Resampling.LANCZOS)

@lru_cache(64)
def card_asset(sid,w,h,angle):
 w,h=round(w),round(h);p=Image.new('RGBA',(w+24,h+60),'#efdfc7');p.paste(photo(sid,w,h),(12,12))
 d=ImageDraw.Draw(p);d.line((14,h+37,w-5,h+37),fill='#b79a77',width=2)
 p=p.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 # Dark offset shadow; the photograph itself is opaque paper with a textured image.
 sh=Image.new('RGBA',p.size,(15,6,22,0));sh.putalpha(p.getchannel('A').point(lambda x:round(x*.55)))
 return p,sh

def card(im,sid,x,y,w=470,h=330,angle=0):
 p,sh=card_asset(sid,w,h,angle)
 im.paste(sh,(round(x)+12,round(y)+17),sh);im.paste(p,(round(x),round(y)),p)

def local_beats(s):
 start=s['start_frame']/30;end=s['end_frame']/30
 return [b-start for b in M['beats'] if start+.15<b<end-.15]

def phase(s,t,step=2):
 ev=local_beats(s)[::step];k=sum(t>=b for b in ev)
 elapsed=t-(ev[k-1] if k else 0)
 return k,elapsed

def editorial_phase(s,t,count):
 ev=local_beats(s);dur=(s['end_frame']-s['start_frame'])/30
 cuts=sorted(set(min(ev,key=lambda b:abs(b-dur*j/count)) for j in range(1,count))) if ev else []
 return sum(t>=b for b in cuts)

def album_scene(s,t):
 k,dt=phase(s,t,2);im=view('album').copy()
 # Photographic memories land on textured pages within 0.27s, then a new spread
 # is revealed by a short curved-strip leaf wipe on every second music beat.
 pool=[2,4,10,11,20,23,24,27,33,34,38,39]
 sid=s['id'];seed=({9:0,16:2,21:4,22:6,25:8}.get(sid,0)+k*2)%len(pool)
 a=pool[seed];b=pool[(seed+1)%len(pool)]
 settle=1-ease(dt/.27)
 return album_art(a,b,round(settle*70),seed,sid)

@lru_cache(16)
def album_art(a,b,settle,seed,sid):
 im=view('album').copy()
 left,right=book.sheet(),book.sheet()
 book.mount(left,photo(a,1100,800),130,370+settle,1100,800)
 book.mount(right,photo(b,1100,800),100,370-settle,1100,800)
 book.note(left,f'{seed+1:02d}  /  OUR YESTERDAYS',700,1330)
 book.note(right,'C.C.  +  MIKE',700,1330,42)
 book.project(im,left,'left');book.project(im,right,'right')
 d=ImageDraw.Draw(im)
 if sid==25:d.line((1800,180,1800,1350),fill='#6b376f',width=22)
 # A clean photographic match-cut replaces the rejected imitation page flip.
 return im

def montage_scene(s,t):
 im=view('desk').copy();sid=s['id'];k,dt=phase(s,t,1)
 pool=[2,4,10,11,13,14,20,23,24,27,33,34,38,39]
 pool=pool[(sid*2)%len(pool):]+pool[:(sid*2)%len(pool)]
 for j in range(4):
  on=max(0,t-j*.19);a=ease(on/.26)
  x=350+j*710;y=380+(j%2)*80+(1-a)*340
  if sid==15:
   recover=ease((t-j*.82)/.28)
   x+=int((1-recover)*(j-1.5)*120);y=380+(j%2)*80+(1-recover)*(210 if j%2 else -170)
  card(im,pool[(j+(k//2 if sid in [5,19] else 0))%len(pool)],x,y,610,460,(-1)**j*3)
 d=ImageDraw.Draw(im)
 if sid in [6,18,28]:
  # Repair joints advance on successive beats and finish with a clear gold seam.
  count=min(3,1+k)
  for j in range(count):
   x=1030+j*710;d.line((x,680,x+80,680),fill='#ffd699',width=8)
   d.ellipse((x+28,665,x+58,695),fill='#f9d9b0')
 else:
  x=350+(k%4)*710;d.line((x,1050,x+610,1050),fill='#e8bc7f',width=5)
 d.text((AW//2,1250),{15:'FRAGMENTS',17:'FOUND AGAIN',18:'CONTINUITY',19:'TOGETHER',28:'TRY AGAIN'}.get(sid,'OUR WORK'),font=font(22,True),fill='#ead4be',anchor='mm')
 return im

def sound_scene(s,t):
 im=view('desk').copy();d=ImageDraw.Draw(im);k,dt=phase(s,t,1)
 card(im,4 if s['id']==7 else 10,380,330,790,620,-3)
 for row in range(2):
  for j in range(65):
   amp=(.25+.75*math.exp(-dt*8))*(45+100*(.5+.5*math.sin(j*.43+t*5+row)))
   x=1580+j*22;y=620+row*290
   d.line((x,y-amp,x,y+amp),fill='#ebc285' if row else '#c4a1dc',width=8)
 d.text((2280,1120),'IN THE SAME RHYTHM',font=font(24,True),fill='#f4d9b0',anchor='mm')
 return im

def dragon_scene(s,t):
 k,dt=phase(s,t,2);sid=s['id']
 # Motivated hard cuts between object details and physical construction states.
 if sid==29:seq=[('dragon-work',(.0,.55,.54,1)),('dragon-work',(.50,.44,.96,.91)),('dragon-work',None)]
 elif sid==30:seq=[('dragon-work',None),('dragon-work',(.29,.15,.69,.80)),('dragon-gift',None)]
 elif sid==31:seq=[('dragon-gift',(.24,.14,.77,.72)),('dragon-gift',None)]
 else:seq=[('dragon-gift',(.24,.49,.82,.99)),('dragon-gift',None)]
 k=editorial_phase(s,t,len(seq));name,box=seq[k];im=view(name,box).copy()
 # A brief warm glint marks assembly completion; it never replaces a new state.
 if sid==30 and k>=2 and dt<.16:
  im=Image.blend(im,Image.new('RGB',im.size,'#ffe0bd'),.10*(1-dt/.16))
 return im

def letter_scene(s,t):
 sid=s['id'];k,dt=phase(s,t,2)
 lines=paper_ink.CONFIG['early_lines'][str(sid)]
 rows=[]
 for j,line in enumerate(lines):
  delay=j*.55;num=round(len(line)*ease((t-delay)/.42))
  rows.append((line[:num],105,370+j*185,56))
 im=paper_ink.compose(view('letter'),tuple(rows))
 cut=editorial_phase(s,t,3)
 if cut==1:
  im=paper_ink.closeup(view('letter'),(45,305,950,695),rows)
 elif cut==2:
  card(im,10,2420,310,600,440,-4)
 return im

def future_scene(s,t):
 k,dt=phase(s,t,2);sid=s['id']
 if sid==35:seq=[('studio',(.0,.48,.54,1)),('studio',None)]
 elif sid==36:seq=[('studio',(.25,.22,.89,.87)),('studio',None)]
 else:seq=[('dragon-gift',(.22,.46,.83,.99)),('letter',None)]
 k=editorial_phase(s,t,len(seq));name,box=seq[k];im=view(name,box).copy()
 if sid==37 and k>0:
  a=ease(dt/.27);card(im,34,2280,330+(1-a)*130,660,490,4)
 return im

def render_frame(n):
 s=next(s for s in T['shots'] if s['start_frame']<=n<s['end_frame']);sid=s['id']
 if sid not in MODES:return retained_renderer(n)
 im=old.base(sid).copy();t=(n-s['start_frame'])/30
 if sid in [16,17,18,19,21]:art=continuity_scene(s,t)
 elif sid==36:art=shared_page_scene(s,t)
 elif sid in [40,41,42,43,44]:art=confession_scene(s,t)
 elif sid in [46,47,48]:art=delivery_scene(s,t)
 elif sid in [9,22,25]:art=album_scene(s,t)
 elif sid in [5,6,15,17,18,19,28]:art=montage_scene(s,t)
 elif sid in [7,8]:art=sound_scene(s,t)
 elif sid in [29,30,31,32]:art=dragon_scene(s,t)
 elif sid in [35,36,37]:art=future_scene(s,t)
 else:art=letter_scene(s,t)
 im.paste(art,(128,174));return im

# Reuse the proven encoding path; all changed shots call this renderer.
def encode(s,start=None,end=None,name=None):
 if s['id'] not in MODES and s['id']!=50:
  # Render edited captions once before looping a retained illustration.
  import tempfile
  lo=s['start_frame'] if start is None else start;hi=s['end_frame'] if end is None else end
  path=P/'segments'/f'{s["id"]:03d}.mp4' if name is None else P/name
  path.parent.mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='mv-caption-') as tmp:
   still=Path(tmp)/'frame.png';render_frame(lo).save(still)
   subprocess.run([FF,'-y','-v','error','-loop','1','-framerate','30','-i',str(still),'-frames:v',str(hi-lo),'-an','-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','0','-pix_fmt','yuv420p','-g','60','-video_track_timescale','15360','-movflags','+faststart',str(path)],check=True)
  print('Rendered edited still',s['id'],flush=True);return
 original=old.render_frame;old.render_frame=render_frame
 try:old.encode(s,start,end,name)
 finally:old.render_frame=original

def mux():
 concat=P/'segments.ffconcat';concat.write_text('ffconcat version 1.0\n'+'\n'.join(f"file 'segments/{s['id']:03d}.mp4'" for s in T['shots'])+'\n',encoding='utf-8')
 subprocess.run([FF,'-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',str(P/'soundtrack.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k','-t','206.7','-movflags','+faststart',str(P/OUT)],check=True)

def samples():
 (P/'samples').mkdir(exist_ok=True)
 for sid in [9,18,22,29,30,41,46]:
  s=T['shots'][sid-1];board=Image.new('RGB',(1920,360))
  for j,u in enumerate([.15,.5,.85]):
   im=render_frame(s['start_frame']+int((s['end_frame']-s['start_frame']-1)*u));im.save(P/'samples'/f'{sid}-{j}.jpg',quality=95);board.paste(im.resize((640,360)),(j*640,0))
  board.save(P/'samples'/f'review-{sid}.jpg',quality=95)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--samples',action='store_true');ap.add_argument('--render',action='store_true');ap.add_argument('--repair-render',action='store_true');ap.add_argument('--shot',type=int);o=ap.parse_args()
 if o.samples:samples()
 if o.shot:encode(T['shots'][o.shot-1])
 if o.render or o.repair_render:
  for s in T['shots']:
   if o.render or s['id'] in REPAIRED or not (P/'segments'/f'{s["id"]:03d}.mp4').exists():encode(s)
  mux()

