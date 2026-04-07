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
# # txt数据文件操作函数集
# 部分文件功能函数

# %% [markdown]
# # 引入重要库

# %%
import binascii
import hashlib
import os
import sqlite3 as lite

# %%
import pathmagic

with pathmagic.context():
    from func.first import (
        dbpathdingdanmingxi,
        dbpathquandan,
        dbpathworkplan,
        touchfilepath2depth,
    )
    from func.logme import log
    # from func.wrapfuncs import timethis

# %% [markdown]
# # 函数集

# %% [markdown]
# print(f"{__file__} is loading now...")


# %% [markdown]
# ## compute_content_hash(title: str, body: str) -> str
# %%
def compute_content_hash(content: str) -> str:
    """计算文本内容哈希唯一值"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


# %% [markdown]
# ## tr2hex(string)

# %%
def str2hex(string):
    """转换字符串为hex字符串（大写）"""
    str_bin = string.encode("utf-8")

    return binascii.hexlify(str_bin).decode("utf-8").upper()


# %% [markdown]
# ## getfilepathnameext(tfile)

# %%
def getfilepathnameext(tfile):
    tfile = os.path.abspath(tfile)
    (filepath, tmpfilename) = os.path.split(tfile)
    (shotename, fileext) = os.path.splitext(tmpfilename)

    return filepath, tmpfilename, shotename, fileext


# %% [markdown]
# ## write2txt(weathertxtfilename, inputitemlist)

# %%
def write2txt(weathertxtfilename, inputitemlist):
    # print(inputitemlist)
    fileobject = open(weathertxtfilename, "w", encoding="utf-8")
    # fileobject = open(weathertxtfilename, 'w', encoding='ISO8859-1')
    if inputitemlist is not None:
        for item in inputitemlist:
            # print(item)
            fileobject.write(str(item) + "\n")
    fileobject.close()


# %% [markdown]
# ## readfromtxt(weathertxtfilename)

# %%
def readfromtxt(weathertxtfilename):
    if not os.path.exists(weathertxtfilename):
        touchfilepath2depth(weathertxtfilename)
        write2txt(weathertxtfilename, None)
    items = []
    # with open(weathertxtfilename, 'r', encoding='ISO8859-1') as ftxt:
    with open(weathertxtfilename, "r", encoding="utf-8") as ftxt:
        items = [line.strip() for line in ftxt]  # strip()，去除行首行尾的空格
        # for line in ftxt:
        # try:
        # items.append(line.strip())
        # except UnicodeDecodeError as ude:
        # log.error(f"{line}\n{ude}")
    return items


# %% [markdown]
# ## get_filesize(filepath)

# %%
def get_filesize(filepath):
    fsize = os.path.getsize(filepath)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


# %% [markdown]
# ## compact_sqlite3_db(dbpath)

# %%
# @timethis
def compact_sqlite3_db(dbpath):
    sizebefore = get_filesize(dbpath)
    conn = lite.connect(dbpath)
    conn.execute("VACUUM")
    conn.close()
    log.info(f"{dbpath}数据库压缩前大小为{sizebefore}MB，压缩之后为{get_filesize(dbpath)}MB。")


# %% [markdown]
# # 主函数

# %%
if __name__ == "__main__":
    log.info(f"运行文件\t{__file__}")
    # print(get_filesize(dbpathquandan))
    # compact_sqlite3_db(dbpathquandan)
    # compact_sqlite3_db(dbpathworkplan)
    # compact_sqlite3_db(dbpathdingdanmingxi)
    (*aaa, ext) = getfilepathnameext(__file__)
    print(ext)

    outputstr = str2hex("天富 1  29")
    print(outputstr)
    log.info(f"文件\t{__file__}\t运行结束。")
