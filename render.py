"""Portable horizontal export, CPU encoder by default, optional user-owned audio."""
import argparse,subprocess,shutil
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--frame',type=int,help='Render one 4K PNG frame instead of video')
    ap.add_argument('--start',type=float,default=0)
    ap.add_argument('--seconds',type=float,help='Default: through the end of the film')
    ap.add_argument('--width',type=int,default=1920,choices=[960,1920,3840])
    ap.add_argument('--audio',type=Path,help='Your own licensed audio; otherwise exports silent video')
    ap.add_argument('--encoder',choices=['libx264','h264_nvenc'],default='libx264')
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    import production as p
    from PIL import Image
    if args.frame is not None:
        if not 0<=args.frame<p.T['frame_count']:ap.error('frame out of range')
        out=args.output or Path('output/frame.png');out.parent.mkdir(parents=True,exist_ok=True)
        p.horizontal(args.frame).save(out);print(out);return
    ff=shutil.which('ffmpeg')
    if not ff:ap.error('Install FFmpeg and put it on PATH')
    if args.audio and not args.audio.is_file():ap.error('audio file not found')
    lo=round(args.start*30);hi=min(p.T['frame_count'],lo+round(args.seconds*30)) if args.seconds is not None else p.T['frame_count']
    if not 0<=lo<hi<=p.T['frame_count']:ap.error('invalid time range')
    out=args.output or Path('output/dear-you.mp4');out.parent.mkdir(parents=True,exist_ok=True)
    h=args.width*9//16
    cmd=[ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{args.width}x{h}','-r','30','-i','pipe:0']
    if args.audio:cmd+=['-ss',str(lo/30),'-i',str(args.audio.resolve()),'-map','0:v','-map','1:a:0','-c:a','aac','-b:a','192k']
    else:cmd+=['-an']
    cmd+=['-c:v',args.encoder]+(['-preset','fast','-crf','18'] if args.encoder=='libx264' else ['-preset','p5','-cq','18'])
    cmd+=['-pix_fmt','yuv420p','-t',str((hi-lo)/30),'-movflags','+faststart',str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(lo,hi):
            im=p.horizontal(n)
            if args.width!=3840:im=im.resize((args.width,h),Image.Resampling.LANCZOS)
            proc.stdin.write(im.tobytes())
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('FFmpeg export failed')
    print(out)

if __name__=='__main__':main()
