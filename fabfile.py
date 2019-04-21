# -*- coding: utf-8 -*-
import os
import tarfile

from fabric.api import env, run, put

env.user = 'root'
env.password = 'Shuhe123'
env.hosts = ['192.168.0.250']
env.port = '22'

exclude_names = ['fabfile.py', 'venv']


def filter_func(tarinfo):
    if tarinfo in exclude_names:
        return True
    elif tarinfo.endswith('fabfile.py'):
        return True
    elif tarinfo.endswith('.git'):
        return True
    elif tarinfo.endswith('.idea'):
        return True
    elif tarinfo.endswith('.html'):
        return True
    elif tarinfo.endswith('.pyc'):
        return True
    else:
        return False


# 本地压缩到服务器
def deploy():
    # local
    basedir = os.getcwd()
    source_folder = '/home/wuzhaoxiong'
    tar = tarfile.open('the_tar.gz', 'w:gz')
    tar.add(basedir, exclude=filter_func)
    tar.close()
    # put
    put(os.path.join(basedir, 'the_tar.gz'), source_folder)
    # run
    run("""
        cd {} &&
        tar -xf the_tar.gz &&
        rm -f the_tar.gz
        """.format(source_folder))
