"""
1. 同步 gitlab 上的所有项目
2. 计算 gitlab 上的代码行数

pip install --upgrade python-gitlab
ref: https://python-gitlab.readthedocs.io/en/stable/

"""
import os
import subprocess
from concurrent.futures.process import ProcessPoolExecutor

import gitlab

# gitlab 代码仓库地址
url_gitlab = 'http://code.petkit.cn'
# gitlab 私有令牌
private_token = 'Wm4zLPS_8e7xBCZdcss1'
dst_projects_dir = os.path.expanduser('~/gitprojects')

ignore_groups = ['test',
                 'server.app', 'go', 'olab', 'server.doctor', 'star_chain',
                 'app.android', 'app.ios', 'app', 'server.sip', 'smartdevice',
                 'Hardware', 'homestation', 'homestation.libs',
                 'fit']
ignore_projects = ['com-petkit-cdn', 'mantas-docker', 'k8s-yaml', 'com-petkit-website-food',
                   'com-petkit-website-web', 'com.petkit.fanli', 'com.petkit.pstore',
                   'com-petkit-app-html', 'com-petkit-pstore-web', 'com-petkit-pstore-mobile',
                   'com-mantas-ma',
                   "com-petkit-food-doc"]
ignore_dirs = ['public/', 'bin/', 'libs/', 'lib/', 'dist/', 'plugins/', 'static/', 'assets/']

ignore_file_ext = ['.log', '.txt', '.min.js', '.zip', '.tar', '.gz', '.png', '.jpg', 'ico', '.svg', '.swf', '^\\.']

cmd_counter = 'git ls-files | grep -v -e "public/" -e "bin/" -e "libs/" -e "lib/" -e "dist/" -e "plugins/" -e "static/" -e "assets/" -e ".log$" -e ".txt$" -e "min.js" -e ".zip$" -e ".jar$" -e ".gz$" -e ".tar$" -e ".png$" -e ".jpg$" -e ".ico$" -e ".svg$"  -e ".swf$" -e "^\."'


def _is_ignore_group(group_name):
    for ig in ignore_groups:
        if ig == group_name:
            return True


def _is_ignore_project(project_name):
    for ip in ignore_projects:
        if ip == project_name:
            return True


def list_projects_in_group(group):
    """拉取 gitlab 的 Group 信息, 创建本地目录结构

    :param group:
    :return:
    """
    is_ignore = _is_ignore_group(group.name)
    if is_ignore:
        return []
    return group.projects.list(all=True)


def pull_project(project, path):
    project_name = project.name
    # dst_projects_path = os.path.join(dst_projects_dir, project_name)
    if len(path) == 0:
        path = dst_projects_dir

    #dst_projects_path = os.path.join(path, project_name)
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


def _source_code_counter(project, path):
    project_name = project.name
    # dst_projects_path = os.path.join(dst_projects_dir, project_name)
    # 空目录跳过，可能是403
    if not os.path.exists(path):
        return 0
    r = subprocess.getoutput("""
        cd {dst_projects_path} && {cmd_counter} | xargs cat | wc -l
    """.format(dst_projects_path=path,
               cmd_counter=cmd_counter))
    count_of_line = int(r.strip().split()[-1])
    # ret[project_name] = count_of_line
    return count_of_line


def source_code_counter(project, path):
    pull_project(project, path=path)
    return _source_code_counter(project, path=path)


def _do(_gitlab):
    groups = _gitlab.groups.list(all=True)
    lines_total = 0
    for _group in groups:
        # 创建 Group 目录
        if _is_ignore_group(_group.name):
            print("ignore group: {group_name}".format(group_name=_group.name))
            continue

        if not os.path.exists(os.path.join(dst_projects_dir, _group.name)):
            os.makedirs(os.path.join(dst_projects_dir, _group.name))

        _projects = list_projects_in_group(_group)

        for _project in _projects:
            if _is_ignore_project(_project.name):
                continue
            _project_path = os.path.join(dst_projects_dir, _group.name, _project.name)
            if not os.path.exists(_project_path):
                os.makedirs(_project_path)

            lines_of_project = source_code_counter(_project, _project_path)
            lines_total += lines_of_project
            with open('ret.csv', 'a') as f:
                f.write("""{group_name},{project_id},{project_name},{num_of_lines}{linesep}""".format(
                    group_name=_group.name,
                    project_id=_project.id,
                    project_name=_project.name,
                    num_of_lines=lines_of_project,
                    linesep=os.linesep,
                ))

    print("total lines: {total_lines}".format(total_lines=lines_total))


if __name__ == '__main__':
    task_list = list()
    ret = {}
    gl = gitlab.Gitlab(url_gitlab, private_token=private_token, api_version='4')
    _do(gl)

    # projects = gl.projects.list(all=True)
    # for project_index, project in enumerate(projects):
    #     project_name = project.name
    #     dst_projects_path = os.path.join(dst_projects_dir, project_name)
    #     num_of_lines = source_code_counter(project)
    #     ret[project_name] = num_of_lines
    #     with open('db.txt', 'a') as f:
    #         f.write("""{project_name},{num_of_lines}{linesep}""".format(
    #             project_name=project_name,
    #             num_of_lines=num_of_lines,
    #             linesep=os.linesep,
    #         ))
