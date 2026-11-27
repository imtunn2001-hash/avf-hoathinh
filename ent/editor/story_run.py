#!/usr/bin/env python3
"""Chay explain.py tren GitHub Actions: SPEC_JSON = {"branch": "tmp-story-...", "dir": "tmp/<job>"}.
Nhanh tam chua spec.json + giong + hinh canh; nhac nen o editor/story/."""
import json, os, subprocess, sys
inp = json.loads(os.environ['SPEC_JSON'])
br, d = inp['branch'], inp['dir'].strip('/')
subprocess.run(['git', 'fetch', '-q', '--depth', '1', 'origin', br], check=True)
__import__('gitlay').lay(d)
root = os.getcwd(); D = os.path.join(root, d)
spec = json.load(open(os.path.join(D, 'spec.json'), encoding='utf-8'))
spec['dir'] = D; spec['out'] = os.path.join(root, 'out', 'out.mp4'); spec['tmp'] = '/tmp/story'
os.makedirs(os.path.join(root, 'out'), exist_ok=True)
json.dump(spec, open('/tmp/story_spec.json', 'w'), ensure_ascii=False)
r = subprocess.run([sys.executable, os.path.join(root, 'editor', 'explain.py'), '/tmp/story_spec.json'])
if r.returncode == 0 and inp.get('sample_branch'):
    g = ['git', '-c', 'user.name=avf-bot', '-c', 'user.email=avf-bot@users.noreply.github.com']
    subprocess.run(['git', 'checkout', '-q', '-b', inp['sample_branch']], check=True)
    subprocess.run(['git', 'add', '-f', 'out/out.mp4'], check=True)
    subprocess.run(g + ['commit', '-q', '-m', 'sample'], check=True)
    subprocess.run(['git', 'push', '-q', '-f', 'origin', 'HEAD:refs/heads/' + inp['sample_branch']], check=True)
sys.exit(r.returncode)
