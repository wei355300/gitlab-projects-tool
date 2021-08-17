#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# 更新本地git仓库代码
# 接收根目录, 能够通过入参指定是否更新子目录, 以及子目录的层级
#

import argparse
import os
import re
from subprocess import check_output

# https://gitpython.readthedocs.io/en/stable/index.html
import git


# from git import Repo

def _remove_merged_branch(path, branch_regex, isDelRemot, itertor):
    "删除已经合并到master分支的分支, is_origin表示是否删除远程分支"
    if _is_git(path):
        _remove_branch(path, branch_regex, isDelRemot)

    if not itertor:
        return
    child_dirs = os.listdir(path)
    for child_dir in child_dirs:
        sub_path = os.path.join(path, child_dir)
        _remove_merged_branch(sub_path, branch_regex, isDelRemot, False)


def _remove_branch(path, branch_regex, isDelRemot):
    "删除已经合并到master分支的分支, is_origin表示是否删除远程分支"
    _del_local_branches(path, branch_regex)
    if isDelRemot:
        _del_remote_branches(branch_regex)


def _del_local_branches(path, branch_regex):
    repo = git.Repo.init(path)
    assert repo
    branch = repo.heads['%s', branch_regex]
    # head = repo.refs.head.head(branch_regex)
    if branch:
        repo.delete_head(branch)

    branches = _get_merged_branch('git branch --merged master', branch_regex)
    branch_list = ' '.join(str(b) for b in branches)
    return check_output('git branch -d %s' % branch_list, shell=True).strip()


def _del_remote_branches(branch_regex):
    branches = _get_merged_branch('git branch -r --merged master', branch_regex)
    for b in branches:
        return check_output('git push origin --delete %s' % b.strip(), shell=True).strip()


def _get_merged_branch(cmd, branch_regex):
    "获取已经merged到master的分支"
    raw_results = check_output(cmd, shell=True)
    branches = [b.strip() for b in raw_results.split('\n')
                if b.strip() and not b.startswith('*') and b.strip() != 'master']
    # todo regex branch by $branch_regex
    match_branches = []
    for b in branches:
        m = re.match(branch_regex, b.strip())
        if m:
            match_branches.append(m.group(1))
    return match_branches


def _is_git(path):
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)


def _exec_update_local(repo, branch):
    "checkout local branch"

    repo.git.checkout(branch)
    print('更新: ', branch)
    repo.git.pull()


def _exec_update_remote(repo, branch):
    "checkout remote branch"

    # 判断远程分支是否存在
    remote_refs = repo.remotes.origin.refs
    if branch in remote_refs:
        print('远程分支存在: ', branch)

        repo.create_head(branch, repo.remotes.origin.refs[branch]).set_tracking_branch(repo.remotes.origin.refs[branch]).checkout()

        repo.remotes.origin.pull()

    else:
        print('远程分支不存在')
    return


def _exec_update(path, branch):
    if not _is_git(path):
        print("非git目录, 跳过:", path)
        return

    print("执行: ", path)

    repo = git.Repo.init(path)
    # 丢弃所有变更
    repo.git.reset("--hard")

    if branch in repo.branches:
        _exec_update_local(repo, branch)
    else:
        _exec_update_remote(repo, branch)

    print('更新完成\n')

    return


def _exec_update_loop(dir, branch, deep=0):
    "具体执行Git目录的更新"

    # 更新当前目录
    _exec_update(dir, branch)

    # 是否需要更新子目录及深度
    # 循环更新子目录(包括目录深度)
    if int(deep) < 1:
        return

    child_dirs = os.listdir(dir)
    for child_dir in child_dirs:
        sub_dir_path = os.path.join(dir, child_dir)
        if os.path.isdir(sub_dir_path):
            _exec_update(sub_dir_path, branch)

    print("\n\n执行完毕")
    return


def update_branch(path, branch, iterator=False):
    _exec_update_loop(path, branch, 1 if iterator else 0)


def delete_branch(path, branch_regex, isDelRemot=False, itertor=False):
    "删除已经merged到master的分支"
    _remove_merged_branch(path, branch_regex, isDelRemot, itertor)


parser = argparse.ArgumentParser()
parser.add_argument('path', help='工程所在的绝对路径')
parser.add_argument('branch', help='分支名称, 如果与 -d 配合使用, 可通过正则表达式匹配删除多个分支')
parser.add_argument('-u', '--update', action='store_true', default=False, help='更新分支')
parser.add_argument('-d', '--delete', action='store_true', default=False, help='删除分支')
parser.add_argument('-r', '--remote', action='store_true', default=False, help='是否包含远程分支')
parser.add_argument('-i', '--iterator', action='store_true', default=False, help='是否判断子目录, 仅第一层子目录')
# parser.add_argument('-f', '--force', action='store_true', default=False, help='是否判断子目录')

args = parser.parse_args()

if __name__ == '__main__':
    dir = args.path
    branch_regex = args.branch
    iterator = args.iterator
    if args.update:
        update_branch(dir, branch_regex, iterator)
    elif args.delete:
        delete_branch(dir, branch_regex, args.remote, iterator)
    else:
        print('*******************************')
        print('Pls pass -h for more information')
        print('*******************************')
