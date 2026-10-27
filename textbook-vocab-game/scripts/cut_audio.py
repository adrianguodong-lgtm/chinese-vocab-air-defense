#!/usr/bin/env python3
"""Cut reviewed timestamps, then reject silent or mismatched clips."""
import argparse, array, json, math, shutil, subprocess, sys
from pathlib import Path

def ffmpeg_path(explicit=None):
    if explicit: return explicit
    found = shutil.which('ffmpeg')
    if found: return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise RuntimeError('未找到 FFmpeg；请安装或使用 --ffmpeg 指定路径')

def decode(ff, args):
    raw = subprocess.check_output([ff, '-v', 'error', *args, '-ar', '16000', '-ac', '1', '-f', 's16le', '-'])
    a = array.array('h'); a.frombytes(raw)
    if sys.byteorder != 'little': a.byteswap()
    return a

def check_clip(ff, path, reference=None):
    a = decode(ff, ['-i', str(path)])
    rms = math.sqrt(sum(v*v for v in a) / max(1, len(a))) / 32768
    if len(a) < 800 or rms < .0005:
        raise ValueError('片段无有效发音：' + str(path))
    info = {'file': str(path), 'duration': len(a)/16000, 'rms': rms}
    if reference is not None:
        n = min(len(a), len(reference))
        aa, bb = a[:n], reference[:n]
        ma, mb = sum(aa)/n, sum(bb)/n
        cov = sum((x-ma)*(y-mb) for x,y in zip(aa,bb))
        denom = math.sqrt(sum((x-ma)**2 for x in aa) * sum((y-mb)**2 for y in bb))
        corr = cov / denom if denom else 0
        if corr < .9: raise ValueError('切片与指定原录音区间不一致：' + str(path))
        info['source_correlation'] = corr
    return info

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True);p.add_argument('--source',required=True)
    p.add_argument('--out-dir',required=True);p.add_argument('--ffmpeg')
    a=p.parse_args(); ff=ffmpeg_path(a.ffmpeg)
    words=json.loads(Path(a.manifest).read_text(encoding='utf-8'))['words']
    source=decode(ff,['-i',a.source]); out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for w in words:
        start,end=float(w['start']),float(w['end'])
        if not (0 <= start < end <= len(source)/16000 + .03): raise ValueError('裁剪时间非法：'+w['word'])
        dest=out/w['audio']
        if dest.parent.resolve()!=out.resolve() or dest.suffix.lower()!='.mp3':raise ValueError('非法音频文件名')
        if dest.exists():raise FileExistsError(dest)
        dur=end-start;fade=min(.008,dur/8)
        try:
            subprocess.run([ff,'-v','error','-n','-ss',str(start),'-i',a.source,'-t',str(dur),
              '-af',f'asetpts=PTS-STARTPTS,afade=t=in:d={fade},afade=t=out:st={dur-fade}:d={fade}',
              '-ar','44100','-ac','1','-c:a','libmp3lame','-b:a','96k',str(dest)],check=True)
            report=check_clip(ff,dest,source[round(start*16000):round(end*16000)])
            report['word']=w['word'];results.append(report)
        except Exception:
            if dest.exists():dest.unlink()
            raise
    print(json.dumps(results,ensure_ascii=False,indent=2))
