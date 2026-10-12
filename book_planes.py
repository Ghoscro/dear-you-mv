from fonts import font_path
"""Photos, frames and page notes share the physical left/right page planes."""
from functools import lru_cache
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
AW,AH=3584,1580;PW,PH=1400,1600
QUADS={'left':[[245,148],[818,146],[814,790],[218,790]],'right':[[858,146],[1395,148],[1450,783],[858,787]]}
@lru_cache(2)
def matrix(side):
 with Image.open(P/'assets'/'album.png') as im:w,h=im.size
 scale=max(AW/w,AH/h);offset=np.array([(w*scale-AW)/2,(h*scale-AH)/2])
 q=np.float32(QUADS[side])*scale-offset
 return cv2.getPerspectiveTransform(np.float32([[0,0],[PW,0],[PW,PH],[0,PH]]),q.astype(np.float32))
def sheet():return Image.new('RGBA',(PW,PH))
def mount(page,picture,x,y,w,h):
 x,y,w,h=map(round,[x,y,w,h])
 d=ImageDraw.Draw(page)
 d.rectangle((x+10,y+13,x+w+42,y+h+77),fill=(31,18,27,125))
 frame=Image.new('RGBA',(w+32,h+64),'#efdfc7');frame.paste(picture.resize((w,h),Image.Resampling.LANCZOS),(16,16))
 ImageDraw.Draw(frame).line((16,h+46,w+16,h+46),fill='#b79a77',width=2)
 page.alpha_composite(frame,(x,y))
def note(page,text,x,y,size=34):
 ImageDraw.Draw(page).text((x,y),text,font=ImageFont.truetype(font_path("en"),size),fill='#68435e',anchor='mm')
def project(im,page,side):
 layer=Image.fromarray(cv2.warpPerspective(np.array(page),matrix(side),(AW,AH),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT))
 im.paste(layer,(0,0),layer)
 return im

def closeup(im,side,region):
 x,y,x1,y1=region
 pts=cv2.perspectiveTransform(np.float32([[x,y],[x1,y],[x1,y1],[x,y1]]).reshape(1,-1,2),matrix(side))[0]
 lo=pts.min(axis=0)-12;hi=pts.max(axis=0)+12;cx,cy=(lo+hi)/2
 w,h=hi-lo;w=max(w,h*AW/AH);h=w*AH/AW
 box=tuple(round(v) for v in [cx-w/2,cy-h/2,cx+w/2,cy+h/2])
 return im.crop(box).resize((AW,AH),Image.Resampling.LANCZOS)
