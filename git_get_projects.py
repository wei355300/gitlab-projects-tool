#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 更新本地git仓库代码
# 接收根目录, 能够通过入参指定是否更新子目录, 以及子目录的层级
#
# https://code.petkit.com/help/api/README.md
#

import requests
import pprint

base_dir       =''
private_token  =''
url_groups     = "https://code.petkit.com/api/v4/groups"
url_projects   = "https://code.petkit.com/api/v4/groups/{group_id}/projects"

# 获取所有的 Group
def _get_all_groups(url_group):
    headers = {
        'PRIVATE-TOKEN':private_token
    }
    r = requests.get(url_group, headers=headers)
    #print(r.status_code)
    #print(r.headers)
    #print(r.reason)
    #print(r.content)
    pprint(r.content)
    return r.content
    # 返回 group 的 id 及 url

def _get_projects(url_projects_of_group):
    # todo
    # 获取 group 下的项目
    # 返回项目 id 及 url
    headers = {
        'PRIVATE-TOKEN':private_token
    }
    r = requests.get(url_projects_of_group, headers=headers)
    return r.content

def _update_project(project_name, branch_name):
    # todo
    # 项目存在, 更新分支内容: pull
    pprint('_update_project');

def _clone_project(url):
    # todo
    # 项目不存在, clone 项目: clone
    pprint('_clone_project');

def _is_exist_project_on_local(project_name):
    # todo
    # 判断项目是否存在, 如果存在则更新, 否则clone
    return False

def _count_lines():
    # git ls-files | xargs cat | wc -l
    pprint('_count_lines');

def do():
    group_list = _get_all_groups(url_groups)
    for group in group_list:
        url_projects_of_group = url_projects.format(group_id=group['id'])
        project_list = _get_projects(url_projects_of_group)
        for project in project_list:
            project_name = project['name']
            TorF = _is_exist_project_on_local(project_name)
            if TorF:
                _update_project(project_name, 'master')
            else:
                _clone_project(project_name, 'master')


if __name__ == '__main__':
    do()