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
# # 时间日期相关函数集

# %% [markdown]
# # 引入库

# %%
import re
import time
from datetime import datetime, timedelta
from typing import Union

import arrow
from tzlocal import get_localzone

# from tzlocal import get_localzone
# from dateutil import tz

# %%
import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.sysfunc import not_IPython
# print(f"{__file__} is loading now...")

# %% [markdown]
# # 功能函数集

# %% [markdown]
# ## datecn2utc(datestr: str) -> datetime


# %%
def datecn2utc(datestr: str) -> datetime:
    # datestr = '2023年9月22日'
    datestr = re.sub("[年月日]", "-", datestr).strip("-")
    return arrow.get(datestr, tzinfo="local").datetime


# %% [markdown]
# ## timestamp2str(timestamp: int) -> str


# %%
def timestamp2str(timestamp: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


# %% [markdown]
# ## normalize_timestamp(ts: Union[str, int]) -> Union[datetime, int, str]


# %%
def normalize_timestamp(ts: Union[str, int]) -> Union[datetime, int, str]:
    # 将时间戳标准化为本地时区的 datetime 对象
    if isinstance(ts, str):
        try:
            # 尝试使用 arrow 解析带有时区的 ISO 格式
            return arrow.get(ts).to(get_localzone()).datetime
        except arrow.parser.ParserError:
            try:
                # 如果不是 ISO 格式，尝试使用默认格式解析
                return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # 如果解析失败，抛出异常
                raise ValueError("无法解析的时间戳格式")
    elif isinstance(ts, int):
        # 处理整数类型的时间戳（假设是秒数）
        return datetime.fromtimestamp(ts)
    else:
        # 如果输入不是字符串或整数，直接返回
        return ts


# %% [markdown]
# ## getstartdate(period: str, thedatetime: datetime) -> datetime


# %%
def getstartdate(period: str, thedatetime: datetime) -> datetime:
    """根据输入的日期时间返回指定周期的开始日期。

    参数:
    period (str): 周期标识，可选值为 ['日', '周', '旬', '月', '年', '全部']
    thedatetime (datetime): 输入的日期时间

    返回:
    datetime: 指定周期的开始日期

    周期列表:
    - '日': 返回当天的开始日期
    - '周': 返回当天所在周的周一的开始日期
    - '旬': 返回当天所在旬的第一天的开始日期
    - '月': 返回当天所在月的第一天的开始日期
    - '年': 返回当天所在年的第一天的开始日期
    - '全部': 返回输入的日期时间不变
    """
    if period == "日":
        zuijindatestart = arrow.get(thedatetime.date()).naive
    elif period == "周":
        weekstarttime = thedatetime - timedelta(days=thedatetime.weekday())  # Monday
        zuijindatestart = arrow.get(weekstarttime.date()).naive
    elif period == "旬":
        # 连用两次三元操作，减缩代码行数
        frtday = 1 if thedatetime.day < 10 else (10 if thedatetime.day < 20 else 20)
        tmpdt = thedatetime.replace(day=frtday)
        zuijindatestart = arrow.get(tmpdt.date()).naive
    elif period == "月":
        zuijindatestart = arrow.get(thedatetime.replace(day=1).date()).naive
    elif period == "年":
        zuijindatestart = arrow.get(thedatetime.replace(month=1, day=1).date()).naive
    else:
        zuijindatestart = thedatetime

    return zuijindatestart


# %% [markdown]
# ## test_getstartdate() -> None


# %%
def test_getstartdate() -> None:
    periodlst = ["日", "周", "旬", "月", "年", "全部"]
    for pr in periodlst:
        tned = getstartdate(pr, datetime.now())
        print(f"{datetime.now()}\t{pr}:\t{tned}\t{type(tned)}")


# %% [markdown]
# ### gethumantimedelay(inputlocaltime: str, intervalseconds: int=120) -> Union[str, bool]


# %%
def gethumantimedelay(inputlocaltime: str, intervalseconds: int=120) -> Union[str, bool]:
    """输入时间和当前时间差值超过120秒（两分钟）时，返回人类可读字符串，否则返回False

    输入参数：
    inputlocaltime: 输入的本地时间字符串，格式为YYYY-MM-DD HH:mm:ss
    intervalseconds: 时间差值秒数，默认120秒
    默认对超过120秒（两分钟）的差值有效，否则返回False
    """
    # 默认用当地时间运算
    intime = arrow.get(inputlocaltime, tzinfo="local")
    if (elasptime := arrow.now() - intime) and (elasptime.seconds > intervalseconds):
        # print(elasptime, elasptime.seconds)
        return intime.humanize(locale="zh_cn")
    else:
        return False


# %% [markdown]
# ## test_gethumantimedelay() -> None


# %%
def test_gethumantimedelay() -> None:
    hmtimetestlst = [
        "20210227 01:04:23",
        arrow.get("20210227 02:04:23", tzinfo="local"),
        "19761006",
    ]
    for htt in hmtimetestlst:
        hmstr = gethumantimedelay(htt)
        print(hmstr)


# %% [markdown]
# # 运行主函数main

# %%
if __name__ == "__main__":
    if not_IPython():
        log.info(f"运行文件\t{__file__}")

    test_gethumantimedelay()
    test_getstartdate()

    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")
