# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     split_at_heading: true
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
import re
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
    from func.jpfuncs import getinivaluefromcloud

# %% [markdown]
# # 函数集

# %% [markdown]
# print(f"{__file__} is loading now...")


# %% [markdown]
# ## getkeysfromcloud() -> dict

# %%
def getkeysfromcloud() -> dict:
    secure_keys = getinivaluefromcloud("joplinai", "secure_keys")
    s_keys = {}
    for pair in [son.split(":") for son in secure_keys.split(",")]:
        s_keys[pair[0]] = pair[1]

    return s_keys


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
def _fix_utf8_tail(raw):
    """截掉文件尾部不完整的 UTF-8 字节序列（进程被杀时写坏的尾巴）"""
    for cut in range(0, 4):
        candidate = raw if cut == 0 else raw[:-cut]
        try:
            candidate.decode("utf-8")
            if cut:
                return candidate, True
            return raw, False
        except UnicodeDecodeError as e:
            if e.reason != "unexpected end of data":
                break
    return raw, False


# %%
def readfromtxt(weathertxtfilename):
    if not os.path.exists(weathertxtfilename):
        touchfilepath2depth(weathertxtfilename)
        write2txt(weathertxtfilename, None)
    with open(weathertxtfilename, "rb") as ftxt:
        raw = ftxt.read()
    fixed = False

    # 1) 截掉尾部不完整字节（写文件时进程被杀导致）
    raw, cut = _fix_utf8_tail(raw)
    if cut:
        fixed = True

    # 2) 整体 UTF-8 解码；失败按历史拉丁编码问题转回 UTF-8
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("latin-1").encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            text = raw.decode("utf-8", errors="replace")
        fixed = True

    # 3) 双重编码 mojibake 行修复：UTF-8 被当作 latin-1 再编码过的行转回
    lines = text.split("\n")
    out_lines = []
    for ln in lines:
        try:
            restored = ln.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            restored = None
        if restored and re.search(r"[\u4e00-\u9fff]", restored):
            ln = restored
            fixed = True
        out_lines.append(ln)

    if fixed:
        write2txt(weathertxtfilename, out_lines)
        log.info(f"编码自动修复：{weathertxtfilename}")

    return [line.strip() for line in out_lines]  # strip()，去除行首行尾的空格


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
# ## normalize_collection_name(model_name: str) -> str

# %%
def normalize_collection_name(model_name: str) -> str:
    """将模型名规范化为 ChromaDB 集合名，替换特殊字符为下划线。"""
    return model_name.replace(":", "_").replace("/", "_").replace("-", "_")


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
