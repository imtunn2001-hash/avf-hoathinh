#!/usr/bin/env python3
"""Dung Reels quang cao page Nhip tren GitHub Actions.
SPEC_JSON = {"branch": "tmp-nhip-...", "dir": "tmp/<job>", "job": "<job>"}
Nhanh tam chua v1..v6.wav + lines.json + scene.json. Xong thi day out.mp4 len nhanh nhip-media: ads/<job>.mp4."""
import json, os, subprocess, sys, shutil
inp = json.loads(os.environ['SPEC_JSON'])
br, d, job = inp['branch'], inp['dir'].strip('/'), inp['job']
subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', br], check=True)
subprocess.run(['git', 'checkout', 'FETCH_HEAD', '--', d], check=True)
root = os.getcwd(); D = os.path.join(root, d)
os.makedirs(os.path.join(root, 'out'), exist_ok=True)
env = dict(os.environ, FONT_DIR=os.path.join(root, 'fonts'))
r = subprocess.run([sys.executable, os.path.join(root, 'editor', 'nhip_reel.py'), D, os.path.join(root, 'out', 'out.mp4')], env=env)
if r.returncode != 0: sys.exit(r.returncode)
# day len nhanh nhip-media
g = ['git', '-c', 'user.name=avf-bot', '-c', 'user.email=avf-bot@users.noreply.github.com']
w = '/tmp/nm'
shutil.rmtree(w, ignore_errors=True)
subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', 'nhip-media'], check=True)
subprocess.run(['git', 'worktree', 'add', '-f', w, 'FETCH_HEAD'], check=True)
os.makedirs(os.path.join(w, 'ads'), exist_ok=True)
shutil.copy(os.path.join(root, 'out', 'out.mp4'), os.path.join(w, 'ads', job + '.mp4'))
subprocess.run(['git', '-C', w, 'add', 'ads/' + job + '.mp4'], check=True)
subprocess.run(g + ['-C', w, 'commit', '-q', '-m', 'nhip reel ' + job], check=True)
for i in range(3):
    if subprocess.run(['git', '-C', w, 'push', '-q', 'origin', 'HEAD:refs/heads/nhip-media']).returncode == 0: break
    subprocess.run(['git', '-C', w, 'pull', '-q', '--rebase', 'origin', 'nhip-media'])
else:
    sys.exit(3)
