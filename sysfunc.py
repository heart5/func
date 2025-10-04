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
# # 系统函数

# %% [markdown]
# ## 引入库

# %%
import datetime

# import inspect
import logging
import os
import platform
import re
import signal

# import subprocess
# import sys
import time
import traceback
import uuid
from collections import deque
from hashlib import sha256
from typing import Callable

import matplotlib
from IPython import get_ipython

# import wmi_client_wrapper as wmi
from matplotlib.font_manager import FontManager



# %%
import pathmagic

with pathmagic.context():
    from func.logme import log


# %% [markdown]
# ## 功能函数集

# %% [markdown]
# ### nooutput2false(output: str) -> bool | str


# %%
def nooutput2false(output: str) -> bool | str:
    """Convert output of a command to boolean or string."""
    if output is None or output == "null" or len(output) == 0:
        return False
    elif output == "true":
        return True
    elif output == "false":
        return False
    else:
        return output


# %% [markdown]
# ### extract_traceback4exception(tbtuple: tuple, func_name: str, sleeptime : int=None) -> str


# %%
def extract_traceback4exception(tbtuple: tuple, func_name: str, sleeptime : int=None) -> str:
    """格式化指定异常的详细信息（tuple）并返回（字符串），默认只返回堆栈的首位各两个元素，除非显性指定显示全部"""
    # by pass the recyle import, nit recommendded
    from func.jpfuncs import getinivaluefromcloud

    # 通sys函数获取eee的相关信息
    eee_type, eee_value, tblst = tbtuple
    if not (brief := getinivaluefromcloud("nettools", "brief")):
        brief = False
    if not (shownums := getinivaluefromcloud("nettools", "shownums")):
        shownums = 3
    if not (
        alltraceback := getinivaluefromcloud("nettools", "tracebackall")
    ):
        alltraceback = True
    if alltraceback:
        rsttb = tblst
    else:
        rsttb = [x for x in tblst[:shownums]]
        rsttb.append("\t...\t")
        rsttb.extend([x for x in tblst[(-1 * shownums) :]])
    if brief:
        rsttb = [x.replace("/data/data/com.termux/files", "/d/d/c/f") for x in rsttb]
    nowstr = datetime.datetime.strftime(datetime.datetime.now(), "%F %T")
    rststr = f"&&&\t{sleeptime}\t&&& in [{func_name}] at {nowstr},\t"
    rststr += f"type is\t[{eee_type}]\t, value is \t[{eee_value}],\t"
    tbstr = "\t".join(rsttb)
    rststr += f"traceback is \t{tbstr}"

    return rststr


# %% [markdown]
# ### not_IPython() -> bool


# %%
def not_IPython() -> bool:  # noqa: N802
    """判断是否在IPython环境下运行"""
    return get_ipython() is None


# %% [markdown]
# ### convertframe2dic(frame: any) -> tuple


# %%
def convertframe2dic(frame: any) -> tuple:
    framestr = str(frame)
    filename = re.findall(r"filename=(.+)\s", framestr)[0].strip()
    lineno = re.findall(r"lineno=(.+)\s", framestr)[0].strip()
    code_context = [
        line.strip()
        for line in eval(re.findall(r"code_context=(.+)\s", framestr)[0].strip())
    ]

    return filename, lineno, code_context


# %% [markdown]
# ### set_timeout(num, callback)


# %%
def set_timeout(num: int, callback: Callable[[], None]) -> Callable[..., any]:
    """设定运行时间的装饰器。如果函数在指定时间内没有完成，则通过回调函数处理。

    参数:
    num (int): 函数运行的最大时间（秒）。
    callback (Callable[[], None]): 当函数超时时调用的回调函数。

    返回:
    Callable[..., Any]: 包装后的函数，带有超时处理机制。
    """

    def wrap(func: Callable[..., any]) -> any:
        def handle(signum: int, frame: any) -> None:
            # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是中断的堆栈帧。
            raise RuntimeError("函数执行超时")

        def to_do(*args: any, **kwargs: any) -> any:
            try:
                start_time = time.time()  # 记录开始时间
                if (sysstr := platform.system()) == "Linux":
                    signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                    signal.alarm(num)  # 设置 num 秒的闹钟
                    log.info(f'函数{func.__name__}设置{num}秒的运行时间限制。')
                    r = func(*args, **kwargs)
                    signal.alarm(0)  # 关闭闹钟
                    end_time = time.time()  # 记录结束时间
                    execution_time = end_time - start_time
                    log.info(f"函数{func.__name__}运行完毕。执行时长: {time.strftime('%H:%M:%S', time.gmtime(execution_time))}")
                    return r

                else:
                    r = func(*args, **kwargs)
                    logstr = f"{sysstr}\t非Linux系统，啥也没做。"
                    log.warning(logstr)
                    end_time = time.time()  # 记录结束时间
                    execution_time = end_time - start_time
                    log.info(f"函数{func.__name__}运行完毕。执行时长: {time.strftime('%H:%M:%S', time.gmtime(execution_time))}")
                    return r

            except RuntimeError as e123:
                logstr = f"{func.__name__}出现错误。\t{e123}"
                log.warning(logstr)
                callback()

        return to_do

    return wrap



# %% [markdown]
# ### after_timeout()


# %%
def after_timeout() -> None:
    """超时后的处理函数"""
    log.critical(("运行超出预设时间，强制退出!", traceback.extract_stack()))


# %% [markdown]
# ### uuid3hexstr(iniputo: object)


# %%
def uuid3hexstr(inputo: str) -> str:
    """Generate a UUID3 hex string from a given input string."""
    inputstr = str(inputo)

    return hex(hash(uuid.uuid3(uuid.NAMESPACE_URL, inputstr)))[2:].upper()


# %% [markdown]
# ### sha2hexstr(inputo: object)


# %%
def sha2hexstr(inputo: any) -> str:
    """Convert input to SHA256 hex string"""
    if type(inputo) is bytes:
        targetb = inputo
    else:
        targetb = str(inputo).encode("utf-8")
    hhh = sha256(targetb)

    return hhh.hexdigest().upper()


# %% [markdown]
# ### is_tool_valid(name)


# %%
def is_tool_valid(name: str) -> bool:
    """检查传入的命令是否在系统路径中并且是可执行状态"""
    # from whichcraft import which
    from shutil import which

    return which(name) is not None


# %% [markdown]
# ### execcmd(cmd)


# %%
def execcmd(cmd: str) -> str:
    """执行命令行命令并输出运行结果

    Args:
        cmd (str): 命令行命令

    Returns:
        str: 命令行命令的运行结果
    """
    try:
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text.strip("\n")
    except Exception as e:
        log.critical(f"执行命令 {cmd} 时出现错误，返回空字符串。{e}")
        return ""


# %% [markdown]
# ### showfonts()


# %%
def showfonts() -> None:
    """查询当前系统所有中文字体"""
    fname = matplotlib.matplotlib_fname()
    print(fname)
    fclistzh = execcmd("fc-list :lang=zh family")
    print(fclistzh)

    mpl_fonts = set(f.name for f in FontManager().ttflist)
    print("all font list get from matplotlib.font_manager:")
    for f in sorted(mpl_fonts):
        print("\t" + f)


# %% [markdown]
# ### testdeque()


# %%
def testdeque() -> None:
    myque = deque(maxlen=4)
    msgcontainer = {}
    numstr = ["one", "two", "three", "four", "five", "six", "seven"]
    for i in range(len(numstr)):
        msgcontainer[i] = {i + 1: numstr[i]}
        myque.append(msgcontainer[i])
    print(msgcontainer)
    print(myque)

    from func.nettools import get_host_ip

    try:
        testerror = 5 / 0
        print(testerror)
    except Exception:
        extra_d = {"hostip": f"{get_host_ip()}", "user": f"{execcmd('whoami')}"}
        print(extra_d)
        # log.critical('测试stack_info参数 %s', "with extra info", stack_info=True)
        log.critical("出错拉，这里->", exc_info=True)

    myque.append(msgcontainer[5])
    print(myque)
    print(list(myque))
    mydict = {}
    for item in myque:
        mydict.update(item)
    print(mydict)


# %% [markdown]
# ### listallloghandler()


# %%
def listallloghander() -> None:
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # print(all_loggers.get('hjer'))

    # 列出所有现有的日志记录器
    all_loggers = logging.Logger.manager.loggerDict
    all_loggers.get("hjer").addHandler(console)
    for k, v in all_loggers.items():
        try:
            if hasattr(v, "handlers"):
                print(f"{k}\t{v}\t{v.handlers}")
            else:
                print(f"{k}\t{v}")
                continue
        except AttributeError as e:
            log.critical(e, exc_info=True)
    # 打印所有现有的日志记录器
    # for logger_name in all_loggers:
    #     logger_inner = logging.getLogger(logger_name)
    #     print(f"{logger_inner}\t{list(logger_inner.handlers)}")


# %% [markdown]
# ## main主函数

# %%
if __name__ == "__main__":
    if not_IPython():
        log.info(f"运行文件\t{__file__}")
    # outgetstr = execcmd("uname -a")
    # listallloghander()
    testdeque()
    # print(execcmd("whoami"))
    # # showfonts()
    # outgetstr = execcmd("echo $PATH")
    # print(outgetstr.strip("\n"))
    # print(uuid3hexstr(outgetstr))
    # print(sha2hexstr(outgetstr))
    # log.critical(outgetstr)
    # print(execcmd("joplin config api.port"))
    if not_IPython():
        log.info(f"文件\t{__file__}\t测试完毕。")
