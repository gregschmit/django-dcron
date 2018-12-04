import os
from subprocess import Popen, PIPE, STDOUT


def cmd_out(cmd):
    wd = os.path.dirname(os.path.realpath(__file__))
    p = Popen(cmd, shell=True, cwd=wd, stdout=PIPE, stderr=STDOUT)
    r, e = p.communicate()
    res = r.strip().decode()
    return res, p.returncode


def get_version():
    git_options = ['git', '/usr/local/bin/git', '/usr/bin/git']
    d = os.path.dirname(os.path.realpath(__file__))
    try:
        x = open(os.path.join(d, 'VERSION_STAMP'), 'rb').read().strip().decode()
        if x: return x
    except FileNotFoundError:
        pass
    for g in git_options:
        gitver, code = cmd_out('{0} describe --tags --always'.format(g))
        gitchanged, code = cmd_out('{0} diff-index HEAD --'.format(g))
        gitver = gitver.replace('v', '').split('-g')[0].replace('-', '.')
        if ' ' in gitver: gitver = '0'
        else: break
    if not gitver or 'fatal' in gitver or '\n' in gitver:
        return '0'
    if gitchanged.strip():
        gitver += '+changed'
    return gitver


def stamp_directory(d):
    v = get_version()
    with open(os.path.join(d, 'VERSION_STAMP'), 'wb') as f:
        f.write(v.encode() + b'\n')


def unstamp_directory(d):
    os.remove(os.path.join(d, 'VERSION_STAMP'))


if __name__ == '__main__':
    print(get_version())
