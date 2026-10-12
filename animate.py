from fonts import font_path
"""V13: same story and assets, retimed to the supplied 勇者 recording."""
from pathlib import Path
import json,subprocess,shutil,argparse,tempfile
import numpy as np
from PIL import Image
import visual as v
import lyric_layer
P=Path(__file__).resolve().parent
T=json.loads((P/'timeline.json').read_text(encoding='utf-8'))
M=json.loads((P/'music-analysis.json').read_text(encoding='utf-8'))
WARPS=json.loads((P/'timewarp.json').read_text(encoding='utf-8'))
OUT='DEAR-YOU-v13-4K-YUUSHA.mp4'
MODES=v.MODES
FF=shutil.which('ffmpeg');REPAIRED=set(range(1,51))
def source_frame(n):
 s=next(s for s in T['shots'] if s['start_frame']<=n<s['end_frame'])
 knots=np.array(WARPS[s['id']-1]['knots'])
 return s,int(round(np.interp(n,knots[:,0],knots[:,1])))
def render_frame(n):
 s,oldn=source_frame(n);original=v.T['shots'][s['id']-1]
 for key in ['zh','en']:original[key]=s[key]
 # Disable the old song's ending fade, then fade the final composed picture
 # and new lyric layer together against the new audio's natural tail.
 oldfade=v.old.T['visual_fade_start'];v.old.T['visual_fade_start']=1e9
 try:im=v.render_frame(oldn)
 finally:v.old.T['visual_fade_start']=oldfade
 im=lyric_layer.draw(im,n/30,s['id'])
 if n/30>=T['visual_fade_start']:
  factor=max(0,min(1,(T['duration']-n/30)/(T['duration']-T['visual_fade_start'])))
  im=Image.blend(Image.new('RGB',im.size),im,factor)
 return im
def encode(s,start=None,end=None,name=None):
 lo=s['start_frame'] if start is None else start;hi=s['end_frame'] if end is None else end
 dest=P/'segments'/f"{s['id']:03d}.mp4" if name is None else P/name;dest.parent.mkdir(exist_ok=True)
 cmd=[FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','3840x2160','-r','30','-i','pipe:0','-frames:v',str(hi-lo),'-an','-c:v','h264_nvenc','-preset','p5','-rc','vbr','-cq','18','-b:v','0','-pix_fmt','yuv420p','-g','60','-video_track_timescale','15360','-movflags','+faststart',str(dest)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for n in range(lo,hi):proc.stdin.write(render_frame(n).tobytes())
 finally:proc.stdin.close()
 if proc.wait():raise RuntimeError('Encoder failed')
 print('Rendered shot',s['id'],flush=True)
def mux():
 concat=P/'segments.ffconcat';concat.write_text('ffconcat version 1.0\n'+'\n'.join(f"file 'segments/{s['id']:03d}.mp4'" for s in T['shots'])+'\n',encoding='utf-8')
 subprocess.run([FF,'-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',str(P/'soundtrack.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k','-t',str(T['duration']),'-movflags','+faststart',str(P/OUT)],check=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');ap.add_argument('--resume',action='store_true');ap.add_argument('--shot',type=int);o=ap.parse_args()
 if o.shot:encode(T['shots'][o.shot-1])
 if o.render or o.resume:
  for s in T['shots']:
   if o.render or not (P/'segments'/f"{s['id']:03d}.mp4").exists():encode(s)
  mux()
