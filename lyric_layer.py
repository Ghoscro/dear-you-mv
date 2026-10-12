from fonts import font_path
"""Source-derived Japanese/Chinese lyric notes fade in unobstructed corners."""
from pathlib import Path
from functools import lru_cache
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
P=Path(__file__).resolve().parent
DATA=json.loads((P/'lyrics.json').read_text(encoding='utf-8'))
T=json.loads((P/'timeline.json').read_text(encoding='utf-8'))
BRIGHT={3,9,19,22,25}
BOOK={9,22,25}
@lru_cache(20)
def font(size,ja=False):
 return ImageFont.truetype(font_path("ja") if ja else font_path("ink"),size)
def wrap(text,f,maxw):
 lines=[]
 for paragraph in text.split('\n'):
  line=''
  for ch in paragraph:
   if line and f.getlength(line+ch)>maxw:lines.append(line);line=''
   line+=ch
  if line:lines.append(line)
 return lines
def placement(cue,sid,width,height):
 if sid in [12,14]:return ((3840-width)//2,28)
 if sid in BOOK:return (720,230)
 if sid==19:corner=2
 elif sid in [3,26,41,46,47]:corner=1
 elif sid==44:corner=3
 elif sid==48:corner=2
 else:corner=(cue['id']+sid)%4
 return [(220,230),(3620-width,230),(3620-width,1700-height),(220,1700-height)][corner]
@lru_cache(180)
def panel(i,sid):
 cue=DATA['cues'][i];gallery=sid in [12,14]
 jf=font(48 if gallery else 64,True);cf=font(38 if gallery else 44)
 maxw=3000 if gallery else 1400
 ja=wrap(cue['ja'].replace('\n','　') if gallery else cue['ja'],jf,maxw);zh=wrap(cue['zh'],cf,maxw)
 lineh=59 if gallery else 80;ch=47 if gallery else 57
 w=round(max([jf.getlength(s) for s in ja]+[cf.getlength(s) for s in zh]))+50
 h=lineh*len(ja)+ch*len(zh)+22
 layer=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(layer)
 dark=sid in BRIGHT and not gallery;ink='#382036' if dark else '#fff8eb'
 y=10
 for s in ja:d.text((18,y),s,font=jf,fill=ink,stroke_width=2,stroke_fill='#fff0d7' if dark else '#211426');y+=lineh
 for s in zh:d.text((18,y),s,font=cf,fill='#513348' if dark else '#f0dcf5',stroke_width=1,stroke_fill='#fff0d7' if dark else '#211426');y+=ch
 # A tiny restrained gold rule ties the lyric notes to the album typography.
 d.line((18,h-5,min(w-20,178),h-5),fill='#bc985a',width=2)
 if not dark:
  shadow=Image.new('RGBA',layer.size,(27,12,37,0));shadow.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(4)).point(lambda x:round(x*.9)))
  shadow.alpha_composite(layer);layer=shadow
 return layer,placement(cue,sid,w,h)
def opacity(cue,t,s):
 fadein=min(1,max(0,(t-cue['start'])/DATA['fade_in']))
 fadeout=min(1,max(0,(cue['end']-t)/DATA['fade_out']))
 enter=min(1,max(0,(t-s['start_frame']/30)/.16))
 leave=min(1,max(0,(s['end_frame']/30-t)/.16))
 return min(fadein,fadeout,enter,leave)
def draw(im,t,sid):
 found=next(((i,c) for i,c in enumerate(DATA['cues']) if c['start']<=t<c['end']),None)
 if not found:return im
 i,c=found
 if not c.get('ja','').strip() and not c.get('zh','').strip():return im
 alpha=opacity(c,t,T['shots'][sid-1])
 if alpha<=0:return im
 layer,xy=panel(i,sid);copy=layer.copy();copy.putalpha(layer.getchannel('A').point(lambda x:round(x*alpha)))
 im.paste(copy,xy,copy);return im
