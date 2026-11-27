#!/usr/bin/env python3
"""Chay wb.py tren GitHub Actions: SPEC_JSON = {"branch": "tmp-wbg-...", "dir": "tmp/<job>"}.
Nhanh tam chua spec.json + voice.wav + hinh AI; tai nguyen chung (font, tay, nhac) nam o editor/wb/."""
import json, os, subprocess, sys
inp = json.loads(os.environ['SPEC_JSON'])
br, d = inp['branch'], inp['dir'].strip('/')
subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', br], check=True)
__import__('gitlay').lay(d)
root = os.getcwd(); D = os.path.join(root, d)
spec = json.load(open(os.path.join(D, 'spec.json'), encoding='utf-8'))
W = os.path.join(root, 'editor', 'wb')
spec['dir'] = D
spec['out'] = os.path.join(root, 'out', 'out.mp4')
spec['tmp'] = '/tmp/wb'
spec.setdefault('hand', os.path.join(W, 'hand.png'))
spec.setdefault('font', os.path.join(W, 'PatrickHand.ttf'))
m = spec.get('music_pick')
if m: spec['music'] = os.path.join(W, m)
os.makedirs(os.path.join(root, 'out'), exist_ok=True)
json.dump(spec, open('/tmp/wb_spec.json', 'w'), ensure_ascii=False)
r = subprocess.run([sys.executable, os.path.join(root, 'editor', 'wb.py'), '/tmp/wb_spec.json'])
sys.exit(r.returncode)
