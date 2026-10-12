"""Local font discovery. Fonts are not bundled."""
import os
from pathlib import Path

def font_path(kind='zh'):
    env=os.environ.get('MV_FONT_'+kind.upper()) or (os.environ.get('MV_FONT_ZH') if kind=='ink' else None)
    names={'zh':['C:/Windows/Fonts/msyh.ttc'], 'ink':['C:/Windows/Fonts/simkai.ttf','C:/Windows/Fonts/msyh.ttc'], 'ja':['C:/Windows/Fonts/simsun.ttc'], 'en':['C:/Windows/Fonts/georgia.ttf']}[kind]
    names += (['/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'] if kind=='en' else ['/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/System/Library/Fonts/PingFang.ttc'])
    for path in ([env] if env else [])+names:
        if Path(path).is_file(): return path
    raise FileNotFoundError('Set MV_FONT_'+kind.upper()+' to an installed font file. See README.md.')
