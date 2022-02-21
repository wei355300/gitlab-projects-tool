"""
1. 同步 gitlab 上的所有项目

pip install --upgrade python-gitlab
ref: https://python-gitlab.readthedocs.io/en/stable/

"""
import os
import subprocess
import gitlab
import json


ignore_groups = ['test',
                 'go', 'olab', 'server.doctor', 'star_chain',
                 'app.android', 'app.ios', 'app', 'server.sip', 'smartdevice',
                 'Hardware', 'homestation', 'homestation.libs',
                 'fit']
ignore_projects = ['com-petkit-cdn', 'mantas-docker', 'k8s-yaml', 'com-petkit-website-food',
                   'com-petkit-website-web', 'com.petkit.fanli', 'com.petkit.pstore',
                   'com-petkit-app-html', 'com-petkit-pstore-web', 'com-petkit-pstore-mobile',
                   'com-mantas-ma']


def _is_ignore_group(group_name):
    for ig in ignore_groups:
        if ig == group_name:
            return True


def _is_ignore_project(project_name):
    for ip in ignore_projects:
        if ip == project_name:
            return True


def _replace_name(name):
    return name.replace(".", "_")


def _pull_project(project, parent_dir):
    _project_name = project.name
    if _is_ignore_project(_project_name):
        return
    _project_name = _replace_name(_project_name)
    _project_path = os.path.join(parent_dir, _project_name)
    if not os.path.exists(_project_path):
        os.makedirs(_project_path)

    if os.path.exists(os.path.join(_project_path, ".git")):
        print("pull project: {project_name}".format(project_name=_project_name))
        subprocess.call(""" cd {_project_path} && git pull """.format(_project_path=_project_path), shell=True)
    else:
        print("clone project: {project_name}".format(project_name=_project_name))
        project_url = project.http_url_to_repo
        subprocess.call(['git', 'clone', project_url, _project_path])


def _pull_group(_gitlab, _group, _parent_dir):

    _group_name = _group.name

    print("pull group: {group_name}".format(group_name=_group_name))

    if _is_ignore_group(_group_name):
        print("Skip group: {group_name}".format(group_name=_group_name))
        return

    _group_name = _replace_name(_group_name)
    _group_path = os.path.join(_parent_dir, _group_name)
    if not os.path.exists(_group_path):
        os.makedirs(os.path.join(_parent_dir, _group_name))

    _sub_groups = _group.subgroups.list()

    if len(_sub_groups):
        for _sub_group in _sub_groups:
            _pull_group(_gitlab, _gitlab.groups.get(_sub_group.id), _group_path)

    _projects = _group.projects.list(all=True)

    if not len(_projects):
        print("no project in {group_name}".format(group_name=_group_name))
        return

    for _project in _projects:
        _pull_project(_project, _group_path)


# 通过递归的方式拉取 group 及其子组的 project
def _pull(_gitlab, local_projects_dir):
    groups = _gitlab.groups.list(all=True)

    if not len(groups):
        print('no groups exists; break!')
        return

    for _group in groups:
        _pull_group(_gitlab, _group, local_projects_dir)


def _read_local_config(json_file):
    """读本本地配置文件"""
    with open(json_file) as f:
        _config = json.load(f)
    return _config


def pull_projects(git_lab_url, git_lab_private_token, git_lab_version, local_project_dir):
    gl = gitlab.Gitlab(git_lab_url, private_token=git_lab_private_token, api_version=git_lab_version)
    _pull(gl, local_project_dir)


if __name__ == '__main__':
    config = _read_local_config('config.json')
    pull_projects(git_lab_url=config['git_lab_url'], git_lab_private_token=config['git_lab_private_token'],
                  git_lab_version=config['git_lab_version'], local_project_dir=config['local_project_dir'])
