"""
1. 同步 gitlab 上的所有项目
2. 计算 gitlab 上的代码行数

pip install --upgrade python-gitlab
ref: https://python-gitlab.readthedocs.io/en/stable/

"""
import os
import subprocess
import gitlab


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


def _list_projects_in_group(group):
    """拉取 gitlab 的 Group 信息, 创建本地目录结构

    :param group:
    :return:
    """
    is_ignore = _is_ignore_group(group.name)
    if is_ignore:
        return []
    return group.projects.list(all=True)


def _pull_project(project, path):
    project_name = project.name

    if os.path.exists(os.path.join(path, ".git")):
        print(""" {dst_projects_path} exists, try update """.format(
            dst_projects_path=path,
        ))
        subprocess.call(""" cd {dst_projects_path} && git pull """.format(
            dst_projects_path=path)
            , shell=True)
    else:
        project_url = project.http_url_to_repo
        subprocess.call(['git', 'clone', project_url, path])


def _pull(_gitlab, local_projects_dir):
    groups = _gitlab.groups.list(all=True)
    lines_total = 0
    for _group in groups:
        # 创建 Group 目录
        if _is_ignore_group(_group.name):
            print("ignore group: {group_name}".format(group_name=_group.name))
            continue

        if not os.path.exists(os.path.join(local_projects_dir, _group.name)):
            os.makedirs(os.path.join(local_projects_dir, _group.name))

        _projects = _list_projects_in_group(_group)

        for _project in _projects:
            if _is_ignore_project(_project.name):
                continue
            _project_path = os.path.join(local_projects_dir, _group.name, _project.name)
            if not os.path.exists(_project_path):
                os.makedirs(_project_path)

            _pull_project(_project, _project_path)


def pull_projects(git_lab_url, git_lab_private_token, git_lab_version, local_project_dir):
    gl = gitlab.Gitlab(git_lab_url, private_token=git_lab_private_token, api_version=git_lab_version)
    _pull(gl, local_project_dir)
