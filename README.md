[TOC]

# 用法

## 切换git分支[git_branch_switch.py] 

```python
# 将本地分支切换为 production 分支
```
python3 git_branch_switch.py -u ~/workspace/petkit-chain/com-petkit-food production
```

# 将目录及子目录(-i 参数)都切换为 production 分支
```
python3 git_branch_switch.py -u -i ~/workspace/petkit-chain/com-petkit-food production
```

## 拉取 gitlab 上所有代码

```python
python3 GitlabSourceCodeCounter.py
```


# 安装依赖

## Gitlab

ref: https://python-gitlab.readthedocs.io/en/stable/

```
pip install --upgrade python-gitlab
```

