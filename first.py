# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %% [markdown]
# # 首函

# %% [markdown]
# 首函，用于定位相对目录，丰富工作目录路径，还有构建路径的基本函数，配置中文字体支持matplotlib

# %% [markdown]
# ## 重要库导入

# %%
import os
import sys
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as pltpp

# %% [markdown]
# ## 函数库

# %% [markdown]
# ### touchfilepath2depth(filepath: Path)

# %%
def touchfilepath2depth(filepath: Path) -> Path:
    filep = Path(filepath)
    filep.parent.mkdir(parents=True, exist_ok=True)

    return filep

# %% [markdown]
# ### getdirmain()


# %%
def getdirmain() -> Path:
    first_path = Path(__file__).parent
    if Path(first_path / ".." / "rootfile").exists():
        return first_path.parent.resolve()
    else:
        return first_path.resolve()


# %% [markdown]
# ## 定义全局变量

# %%
# 缓存根目录，避免重复文件系统检查
_dirmain = getdirmain()
dirmainpath = _dirmain
dirmain = str(_dirmain)
dirlog = str(_dirmain / "log" / "happyjoplin.log")
dbpathworkplan = str(_dirmain / "data" / "workplan.db")
dbpathquandan = str(_dirmain / "data" / "quandan.db")
dbpathdingdanmingxi = str(_dirmain / "data" / "dingdanmingxi.db")
ywananchor = 50000  # 纵轴标识万化锚点


# %%
# sys.path 注入：新项目推荐使用 pathmagic.context() 替代。
# 此处保留以兼容旧项目，重复路径由 if ... not in sys.path 兜底。
path2include = ["etc", "func", "work", "life", "study"]
for p2i in path2include:
    combinepath = str((dirmainpath / p2i).resolve())
    if combinepath not in sys.path:
        sys.path.append(combinepath)

# %% [markdown]
# ## 主函数，main()

# %%
if __name__ == "__main__":
    print(f"项目根目录\t{getdirmain()}")
    print(f"当前工作目录\t{os.getcwd()}")
    for dr in sys.path:
        print(dr)
    print("Done.")
