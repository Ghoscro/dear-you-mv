from fonts import font_path
"""V14 release renderer. 30 fps, unchanged audio; separate portrait composition."""
import argparse,json,subprocess,shutil,hashlib
from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
import animate as a
P=Path(__file__).resolve().parent
T=a.T; V=a.v; FF=shutil.which('ffmpeg'); FPS=30
CHANGED=list(range(1,51))
PANELS={}

@lru_cache(32)
def font(size,kind='zh'):
 return ImageFont.truetype(font_path(kind),size)

@lru_cache(512)
def lines(text,f,width):
 if ' ' in text and all(ord(x)<256 for x in text):
  words=text.split();out=[];line=''
  for w in words:
   candidate=(line+' '+w).strip()
   if line and f.getlength(candidate)>width:out.append(line);line=w
   else:line=candidate
  return out+[line]
 out=[]
 for paragraph in text.split('\n'):
  line=''
  for c in paragraph:
   if line and f.getlength(line+c)>width:out.append(line);line=''
   line+=c
  if line:out.append(line)
 return out

@lru_cache(2)
def wide_gallery(sid):
 art=Image.new('RGB',(3584,1580),'#211d2c');first=1 if sid==12 else 16
 for i in range(15):
  sticker=Image.open(next((P/'assets/stickers').glob(f'{first+i:02d}-*.png'))).convert('RGBA')
  tile=ImageOps.contain(sticker,(580,470),Image.Resampling.LANCZOS)
  art.paste(tile,(i%5*700+(700-tile.width)//2+42,i//5*500+(500-tile.height)//2+25),tile)
 return art

def base_frame(n):
 s,oldn=a.source_frame(n)
 for key in ['zh','en']:V.T['shots'][s['id']-1][key]=s[key]
 oldfade=V.old.T['visual_fade_start'];V.old.T['visual_fade_start']=1e9
 try: im=V.render_frame(oldn)
 finally:V.old.T['visual_fade_start']=oldfade
 if s['id'] in [1,2]:
  art=V.photo(1,V.AW,V.AH) if s['id']==1 else V.view('hesitation')
  im.paste(art,(128,174))
 if s['id'] in [12,14]:
  im.paste(wide_gallery(s['id']),(128,174))
 return im,s

def fade(im,n):
 if n/30>=T['visual_fade_start']:
  f=max(0,min(1,(T['duration']-n/30)/(T['duration']-T['visual_fade_start'])))
  return Image.blend(Image.new('RGB',im.size),im,f)
 return im

def horizontal(n):
 im,s=base_frame(n)
 return fade(a.lyric_layer.draw(im,n/30,s['id']),n)

@lru_cache(60)
def gallery(sid):
 im=Image.new('RGB',(1880,2520),'#211d2c')
 first=1 if sid==12 else 16
 for i in range(15):
  sticker=Image.open(next((P/'assets/stickers').glob(f'{first+i:02d}-*.png'))).convert('RGBA')
  tile=ImageOps.contain(sticker,(570,455),Image.Resampling.LANCZOS)
  im.paste(tile,(i%3*625+(625-tile.width)//2,i//3*500+(500-tile.height)//2),tile)
 return im

PORTRAITS={1,2,4,10,11,13,20,23,24,27,33,34,38,39,45,49}
BOOKS={9,17,22,25,36,47}

def art_image(im,s):
 if s['id'] in [1,2] or s['id'] in V.MODES:box=(128,174,3712,1754)
 else:box=tuple(s.get('art_box',[516,174,3323,1754]))
 return im.crop(box)

def vertical(n):
 base,s=base_frame(n);sid=s['id'];art=art_image(base,s)
 if sid in [3,26,41,44]:
  _,oldn=a.source_frame(n);os=V.T['shots'][sid-1];tt=(oldn-os['start_frame'])/30
  if sid in [3,26]:
   rows=tuple((line[:round(len(line)*V.ease((tt-j*.55)/.42))],105,370+j*185,56) for j,line in enumerate(V.paper_ink.CONFIG['early_lines'][str(sid)]))
  else:
   text=V.paper_ink.CONFIG['letter_lines'];k,dt,cuts=V.story_step(os,tt,len(text)+1)
   rows=[]
   for j,line in enumerate(text):
    start=0 if j==0 else cuts[min(j-1,len(cuts)-1)]
    rows.append((line if sid==44 else line[:round(len(line)*V.ease((tt-start)/.6))],105,190+j*180,56))
   if sid==44:
    rows += [(V.paper_ink.CONFIG['confession'][:round(len(V.paper_ink.CONFIG['confession'])*V.ease(tt/.85))],105,910,60)]
    if tt>.8:rows += [(V.paper_ink.CONFIG['signature'],410,1150,54)]
  art=V.paper_ink.compose(V.view('letter'),tuple(rows))
  quad=V.paper_ink.geometry('letter')[1]
  box=(max(0,int(quad[:,0].min())-90),0,min(art.width,int(quad[:,0].max())+90),art.height)
  art=art.crop(box)
 im=Image.new('RGB',(2160,3840),'#211d2c');d=ImageDraw.Draw(im)
 d.text((140,105),'DEAR YOU',font=font(46,'en'),fill='#ddc9b0')
 d.text((1990,105),'C.C. / 致你',font=font(40),fill='#bba4c8',anchor='ra')
 d.line((140,185,2020,185),fill='#6d5376',width=2)
 x,y,w,h=140,600,1880,2240
 cachekey=(sid,art.size,hashlib.blake2b(art.tobytes(),digest_size=12).digest())
 if cachekey in PANELS:
  panel=PANELS[cachekey]
 elif sid in [12,14]:
  panel=gallery(sid).resize((w,h),Image.Resampling.LANCZOS)
 elif sid in PORTRAITS:
  # Separate portrait crop. The opening retains monitor edges, face and reaching hand.
  center={1:(.35,.5),2:(.58,.4),4:(.55,.5),11:(.60,.4),20:(.5,.5),24:(.60,.5),27:(.52,.5),38:(.58,.5),39:(.58,.5)}.get(sid,(.5,.45))
  panel=ImageOps.fit(art,(w,h),Image.Resampling.LANCZOS,centering=center)
 elif sid in BOOKS and sid not in [47]:
  # Two readable panels retain both pages instead of cropping away half the book.
  panel=Image.new('RGB',(w,h),'#211d2c')
  for j in range(2):
   half=art.crop((round(art.width*j/2),0,round(art.width*(j+1)/2),art.height))
   tile=ImageOps.contain(half,(w,h//2-25),Image.Resampling.LANCZOS)
   panel.paste(tile,((w-tile.width)//2,j*h//2+(h//2-tile.height)//2))
 else:
  # Preserve complete actions and paper text; a derived atmosphere carries the tall field.
  panel=ImageOps.fit(art,(w,h),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(48))
  panel=Image.blend(panel,Image.new('RGB',panel.size,'#211d2c'),.34)
  tile=ImageOps.contain(art,(w,h),Image.Resampling.LANCZOS)
  panel.paste(tile,((w-tile.width)//2,(h-tile.height)//2))
 if cachekey not in PANELS:
  if len(PANELS)>=8:PANELS.pop(next(iter(PANELS)))
  PANELS[cachekey]=panel
 im.paste(panel,(x,y));d=ImageDraw.Draw(im)
 # Dedicated story zone prevents overlays on eyes, hands, or the letter.
 fy=2990;zh=lines(s['zh'],font(100),1830)
 for line in zh:d.text((1080,fy),line,font=font(100),fill='#fff3de',anchor='mt');fy+=140
 fy+=32
 for line in lines(s['en'],font(54,'en'),1760):
  d.text((1080,fy),line,font=font(54,'en'),fill='#d3c2dd',anchor='mt');fy+=77
 d.line((920,3530,1240,3530),fill='#bc985a',width=3)
 # Lyrics fade in the upper corners, independent of story captions.
 found=next((c for c in a.lyric_layer.DATA['cues'] if c['start']<=n/30<c['end']),None)
 if found:
  alpha=a.lyric_layer.opacity(found,n/30,s)
  layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer);yy=240
  right=found['id']%2==0;xx=2010 if right else 150;anchor='ra' if right else 'la'
  for line in lines(found['ja'],font(68,'ja'),1790):
   ld.text((xx,yy),line,font=font(68,'ja'),fill=(255,239,218,round(255*alpha)),anchor=anchor);yy+=83
  for line in lines(found['zh'],font(55),1790):
   ld.text((xx,yy+9),line,font=font(55),fill=(218,192,231,round(255*alpha)),anchor=anchor);yy+=71
  im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 return fade(im,n)

def encode(mode,lo,hi,dest):
 size='3840x2160' if mode=='horizontal' else '2160x3840';fn=horizontal if mode=='horizontal' else vertical
 dest.parent.mkdir(exist_ok=True)
 cmd=[FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',size,'-r','30','-i','pipe:0','-frames:v',str(hi-lo),'-an','-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','0','-pix_fmt','yuv420p','-g','60','-video_track_timescale','15360','-movflags','+faststart',str(dest)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for n in range(lo,hi):proc.stdin.write(fn(n).tobytes())
 finally:proc.stdin.close()
 if proc.wait():raise RuntimeError('encode failed')

def mux(mode,folder,name):
 concat=P/f'{mode}.ffconcat';concat.write_text('ffconcat version 1.0\n'+'\n'.join(f"file '{folder}/{s['id']:03d}.mp4'" for s in T['shots'])+'\n',encoding='utf-8')
 subprocess.run([FF,'-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',str(P/'soundtrack.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k','-t',str(T['duration']),'-movflags','+faststart',str(P/name)],check=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['horizontal','vertical']);ap.add_argument('--sample',action='store_true');ap.add_argument('--stills',action='store_true');ap.add_argument('--first',type=int,default=1);ap.add_argument('--last',type=int,default=50);ap.add_argument('--segments-only',action='store_true');ap.add_argument('--reuse-verified',action='store_true');o=ap.parse_args()
 if o.stills:
  (P/'review').mkdir(exist_ok=True)
  for sid in [1,2,3,12,14,20,22,40,42,43,44,47,48]:
   s=T['shots'][sid-1];n=(s['start_frame']+s['end_frame'])//2
   for mode,fn in [('h',horizontal),('v',vertical)]:fn(n).save(P/'review'/f'{mode}-{sid:02d}.jpg',quality=92)
  print('stills done',flush=True)
 elif o.sample:
  dest=P/f'opening-{o.mode}-silent.mp4';encode(o.mode,0,360,dest)
  subprocess.run([FF,'-y','-v','error','-i',str(dest),'-i',str(P/'soundtrack.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k','-t','12','-movflags','+faststart',str(P/f'opening-{o.mode}.mp4')],check=True)
 else:
  folder='segments' if o.mode=='horizontal' else 'vertical-segments'
  for s in T['shots']:
   if not o.first<=s['id']<=o.last:continue
   dest=P/folder/f"{s['id']:03d}.mp4"
   if o.mode=='horizontal' and s['id'] not in CHANGED and dest.exists():continue
   if o.reuse_verified and dest.exists():
    try:
     q=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(dest)],stderr=subprocess.DEVNULL))
     if int(q['streams'][0]['nb_frames'])==s['end_frame']-s['start_frame']:continue
    except (subprocess.CalledProcessError,ValueError,KeyError,IndexError):pass
   encode(o.mode,s['start_frame'],s['end_frame'],dest)
   print(f"{o.mode} {s['id']}/50",flush=True)
  if not o.segments_only:mux(o.mode,folder,'DEAR-YOU-v18-HORIZONTAL-4K.mp4' if o.mode=='horizontal' else 'DEAR-YOU-v14-DOUYIN-4K.mp4')
