from fonts import font_path
"""Native-resolution ink in paper coordinates, projected before camera cropping.

Coordinates are editable in paper-text.json. Existing raster paintings are
unchanged. Every line shares the same measured paper plane, including partial
writing, the confession, the signature, and the recipient label.
"""
from pathlib import Path
from functools import lru_cache
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

P=Path(__file__).resolve().parent
CONFIG=json.loads((P/'paper-text.json').read_text(encoding='utf-8'))
AW,AH=3584,1580

@lru_cache(2)
def geometry(name):
 p=CONFIG['planes'][name]
 with Image.open(P/'assets'/f"{p['asset']}.png") as src:
  w,h=src.size
 scale=max(AW/w,AH/h)
 offset=np.array([(w*scale-AW)/2,(h*scale-AH)/2])
 quad=np.array(p['quad_source_pixels'],np.float32)*scale-offset
 pw,ph=p['size']
 matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[pw,0],[pw,ph],[0,ph]]),quad.astype(np.float32))
 return matrix,quad

def project(points,name='letter'):
 return cv2.perspectiveTransform(np.float32(points).reshape(1,-1,2),geometry(name)[0])[0]

@lru_cache(16)
def ink_font(size):
 return ImageFont.truetype(font_path("ink"),size*3)

@lru_cache(64)
def projected_ink(rows,name,box=None):
 rows=[r for r in rows if r[0]]
 if not rows:return None
 # Supersample the ink, including signature close-ups, while retaining the
 # painting's texture and all original colors beneath its transparent layer.
 bounds=[]
 for text,x,y,size in rows:
  l,t,r,b=ink_font(size).getbbox(text,anchor='lm')
  bounds.append((x+l/3,y+t/3,x+r/3,y+b/3))
 x0,y0=np.floor(np.min(np.array(bounds)[:,:2],axis=0)-3).astype(int)
 x1,y1=np.ceil(np.max(np.array(bounds)[:,2:],axis=0)+3).astype(int)
 layer=Image.new('RGBA',((x1-x0)*3,(y1-y0)*3))
 draw=ImageDraw.Draw(layer)
 for text,x,y,size in rows:
  draw.text(((x-x0)*3,(y-y0)*3),text,font=ink_font(size),fill=CONFIG['ink'],anchor='lm')
 m=geometry(name)[0] @ np.array([[1/3,0,x0],[0,1/3,y0],[0,0,1]],float)
 if box:
  bx,by,bx1,by1=box;sx,sy=AW/(bx1-bx),AH/(by1-by)
  m=np.array([[sx,0,-bx*sx],[0,sy,-by*sy],[0,0,1]]) @ m
 q=cv2.perspectiveTransform(np.float32([[0,0],[layer.width,0],[layer.width,layer.height],[0,layer.height]]).reshape(1,-1,2),m)[0]
 lo=np.maximum([0,0],np.floor(q.min(axis=0)-3)).astype(int)
 hi=np.minimum([AW,AH],np.ceil(q.max(axis=0)+3)).astype(int)
 if np.any(hi<=lo):return None
 local=np.array([[1,0,-lo[0]],[0,1,-lo[1]],[0,0,1]],float) @ m
 warped=cv2.warpPerspective(np.array(layer),local,tuple((hi-lo).tolist()),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
 return Image.fromarray(warped),tuple(lo.tolist())

def compose(background,rows,name='letter',box=None):
 im=background.copy();ink=projected_ink(rows,name,box)
 if ink:im.paste(ink[0],ink[1],ink[0])
 return im

def closeup(im,region,rows=None):
 # Expand the camera rectangle to contain the entire requested paper region.
 # Matching the art aspect avoids a second fit crop slicing through glyphs.
 x0,y0,x1,y1=region
 pts=project([[x0,y0],[x1,y0],[x1,y1],[x0,y1]])
 lo=pts.min(axis=0)-35;hi=pts.max(axis=0)+35;cx,cy=(lo+hi)/2
 w,h=hi-lo;w=max(w,h*AW/AH);h=w*AH/AW
 cx=max(w/2,min(AW-w/2,cx));cy=max(h/2,min(AH-h/2,cy))
 box=tuple(round(v) for v in [cx-w/2,cy-h/2,cx+w/2,cy+h/2])
 return camera_compose(im,box,rows)

def text_closeup(im,rows,all_rows=None):
 points=[]
 for text,x,y,size in rows:
  l,t,r,b=ink_font(size).getbbox(text,anchor='lm')
  points.extend([[x+l/3,y+t/3],[x+r/3,y+t/3],[x+r/3,y+b/3],[x+l/3,y+b/3]])
 pts=project(points);lo=pts.min(axis=0)-25;hi=pts.max(axis=0)+25
 cx,cy=(lo+hi)/2;w,h=hi-lo;w=max(w,h*AW/AH);h=w*AH/AW
 box=tuple(round(v) for v in [cx-w/2,cy-h/2,cx+w/2,cy+h/2])
 return camera_compose(im,box,all_rows)

def camera_compose(im,box,rows=None,name='letter'):
 background=im.crop(box).resize((AW,AH),Image.Resampling.LANCZOS)
 return compose(background,tuple(rows),name,box) if rows is not None else background
