"""
1. 同步 gitlab 上的所有项目
2. 计算 gitlab 上的代码行数

pip install --upgrade python-gitlab
ref: https://python-gitlab.readthedocs.io/en/stable/

"""
import json
import os
import subprocess
from gitlab_project_pull import pull_projects

ignore_dirs = ['public/', 'bin/', 'libs/', 'lib/', 'dist/', 'plugins/', 'static/', 'assets/']

ignore_file_ext = ['.log', '.txt', '.min.js', '.zip', '.tar', '.gz', '.png', '.jpg', 'ico', '.svg', '.swf', '^\\.']

cmd_counter = 'git ls-files | grep -v -e "public/" -e "bin/" -e "libs/" -e "lib/" -e "dist/" -e "plugins/" -e "static/" -e "assets/" -e ".log$" -e ".txt$" -e "min.js" -e ".zip$" -e ".jar$" -e ".gz$" -e ".tar$" -e ".png$" -e ".jpg$" -e ".ico$" -e ".svg$"  -e ".swf$" -e "^\."'


def read_local_config(json_file):
    """读本本地配置文件"""
    with open(json_file) as f:
        _config = json.load(f)
    return _config


def _source_code_counter(path):
    if not os.path.exists(path):
        return 0
    r = subprocess.getoutput("""
        cd {dst_projects_path} && {cmd_counter} | xargs cat | wc -l
    """.format(dst_projects_path=path,
               cmd_counter=cmd_counter))
    count_of_line = int(r.strip().split()[-1])
    return count_of_line


if __name__ == '__main__':
    config = read_local_config('config.json')
    _local_project_dir = config['local_project_dir']
    pull_projects(git_lab_url=config['git_lab_url'], git_lab_private_token=config['git_lab_private_token'], git_lab_version=config['git_lab_version'], local_project_dir=config['local_project_dir'])
    lines_total = 0

    with os.scandir(_local_project_dir) as _groups:
        for _group in _groups:
            if _group.is_dir():
                print(_group.name)
                with os.scandir(_group.path) as _projects:
                    for _project in _projects:
                        if _project.is_dir():
                            print(_project.path)
                            print("count {group_name},{project_name}".format(group_name=_group.name, project_name=_project.name))
                            _lines_of_project = _source_code_counter(_project.path)
                            lines_total += _lines_of_project
                            with open('ret.csv', 'a') as f:
                                f.write("""{group_name},{project_name},{num_of_lines}{linesep}""".format(
                                    group_name=_group,
                                    project_name=_project,
                                    num_of_lines=_lines_of_project,
                                    linesep=os.linesep,
                                ))
    print("total lines: {total_lines}".format(total_lines=lines_total))
