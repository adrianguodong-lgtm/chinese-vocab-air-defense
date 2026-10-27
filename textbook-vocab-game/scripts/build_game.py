#!/usr/bin/env python3
"""Replace only WORDS / WORD_EN / WORD_AUDIO, preserving all other bytes."""
import argparse, base64, hashlib, json, re
from pathlib import Path
TABLES = ('WORDS', 'WORD_EN', 'WORD_AUDIO')

def spans(text):
    result = {}
    for name in TABLES:
        matches = list(re.finditer(r'\bconst\s+' + name + r'\s*=\s*', text))
        if len(matches) != 1:
            raise ValueError('模板必须恰有一个 const ' + name)
        start = matches[0].end()
        _, used = json.JSONDecoder().raw_decode(text[start:])
        result[name] = (start, start + used)
    return result

def immutable(text):
    for name, (a, b) in sorted(spans(text).items(), key=lambda item: item[1][0], reverse=True):
        text = text[:a] + '<' + name + '>' + text[b:]
    return text

def build(template, manifest, clips, output):
    data = json.loads(Path(manifest).read_text(encoding='utf-8'))
    words = data['words']
    names = [w['word'] for w in words]
    if not names or len(names) != len(set(names)):
        raise ValueError('词汇为空或有重复')
    for w in words:
        if not re.fullmatch(r'[\u3400-\u9fff]+', w['word']):
            raise ValueError('词条只能包含汉字：' + w['word'])
        if any(w['word'] in other for other in names if other != w['word']):
            raise ValueError('未执行最长优先：' + w['word'])
        if not w.get('pinyin') or not w.get('english'):
            raise ValueError('缺少拼音或英文：' + w['word'])
    audio = {}
    for w in words:
        path = (Path(clips) / w['audio']).resolve()
        if path.parent != Path(clips).resolve() or path.suffix.lower() != '.mp3':
            raise ValueError('audio 必须是切片目录内的 MP3 文件名')
        raw = path.read_bytes()
        if len(raw) < 100:
            raise ValueError('音频为空或过短：' + w['word'])
        audio[w['word']] = 'data:audio/mpeg;base64,' + base64.b64encode(raw).decode('ascii')
    values = {'WORDS': [{'word': w['word'], 'pinyin': w['pinyin']} for w in words],
              'WORD_EN': {w['word']: w['english'] for w in words}, 'WORD_AUDIO': audio}
    original = Path(template).read_bytes().decode('utf-8')
    output_text = original
    for name, (a, b) in sorted(spans(original).items(), key=lambda item: item[1][0], reverse=True):
        value = json.dumps(values[name], ensure_ascii=False, indent=4).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        output_text = output_text[:a] + value + output_text[b:]
    if immutable(original) != immutable(output_text):
        raise ValueError('检测到三张表之外的改动，取消输出')
    dest = Path(output)
    if dest.suffix.lower() != '.html':
        raise ValueError('输出必须是 .html')
    dest.parent.mkdir(parents=True, exist_ok=True)
    base = dest
    i = 2
    while dest.exists():
        dest = base.with_name(base.stem + '_' + str(i) + '.html'); i += 1
    with dest.open('xb') as handle:
        handle.write(output_text.encode('utf-8'))
    digest = hashlib.sha256(immutable(original).encode('utf-8')).hexdigest()
    print(json.dumps({'output': str(dest.resolve()), 'words': len(words), 'embedded_audio': len(audio),
                      'changed': list(TABLES), 'unchanged_code_sha256': digest}, ensure_ascii=False, indent=2))
    return dest

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True); p.add_argument('--clips-dir', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--template', default=str(Path(__file__).resolve().parents[1] / 'assets/game-template.html'))
    a = p.parse_args()
    build(a.template, a.manifest, a.clips_dir, a.output)
