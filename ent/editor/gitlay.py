"""27/11: may dung chay trong thu muc ent/ cua repo cong khai, con file tam (n8n day len nhanh tmp-*) nam o GOC repo.
lay(p): lay p tu FETCH_HEAD theo duong dan tinh tu goc repo, roi tao loi tat tu thu muc dang chay toi do."""
import os, subprocess


def lay(p):
    p = str(p).strip('/')
    top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()
    subprocess.run(['git', 'checkout', 'FETCH_HEAD', '--', ':/' + p], check=True)
    cwd = os.getcwd()
    if os.path.realpath(cwd) != os.path.realpath(top):
        dst = os.path.join(cwd, p)
        if not os.path.exists(dst):
            os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
            os.symlink(os.path.join(top, p), dst)
