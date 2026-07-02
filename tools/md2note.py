# -*- coding: utf-8 -*-
# md2note — 将 markdown 文件同步到 Joplin 笔记
#
# 用法:
#   python -m func.tools.md2note <file.md> [--notebook NAME] [--data-dir DIR]
#   python -m func.tools.md2note --find-files [--notebook NAME]
#
# md2note.ini 映射文件存储在 data-dir/data/md2note.ini 中，
# 由 func.configpr 自动管理，每个项目独立，互不干扰。

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

from func.configpr import getcfp, getcfpoptionvalue, removesection, setcfpoptionvalue
from func.first import getdirmain
from func.jpfuncs import (
    createnote,
    jpapi,
    searchnotebook,
    searchnotes,
    updatenote_body,
    updatenote_title,
)
from func.logme import log
from func.sysfunc import not_IPython

CFG_NAME = "md2note"
DEFAULT_NOTEBOOK = "ewmobile"


def _resolve(filepath: str) -> Path:
    return Path(filepath).resolve()


def _strip_frontmatter(text: str) -> tuple:
    """剥离YAML frontmatter，返回 (body, frontmatter_dict)"""
    fm = {}
    if text.startswith("---"):
        idx = text.find("---", 3)
        if idx != -1:
            try:
                fm = yaml.safe_load(text[3:idx]) or {}
            except yaml.YAMLError:
                pass
            text = text[idx + 3:].lstrip("\n")
    return text, fm


def _extract_heading(text: str) -> str:
    """从文本首行提取一级或二级标题，无则返回None"""
    m = re.match(r"^#{1,2}\s+(.+)", text.lstrip())
    return m.group(1).strip() if m else None


def _stored_title(fpath: Path) -> str:
    return getcfpoptionvalue(CFG_NAME, str(fpath), "title")


def _note_id(fpath: Path) -> str:
    return getcfpoptionvalue(CFG_NAME, str(fpath), "note_id")


def _last_mtime(fpath: Path):
    return getcfpoptionvalue(CFG_NAME, str(fpath), "last_mtime")


def _save(fpath: Path, note_id: str, title: str, mtime: float) -> None:
    setcfpoptionvalue(CFG_NAME, str(fpath), "note_id", note_id)
    setcfpoptionvalue(CFG_NAME, str(fpath), "title", title)
    setcfpoptionvalue(CFG_NAME, str(fpath), "last_mtime", str(mtime))


def _make_title(fpath: Path, base: str) -> str:
    """追加父目录路径以区分同名文件"""
    try:
        rel = fpath.parent.relative_to(Path.home())
        return f"{base} (~/{rel})"
    except ValueError:
        return f"{base} ({fpath.parent})"


def sync_file(
    filepath: str,
    title: str = None,
    notebook: str = None,
    force: bool = False,
    dry_run: bool = False,
    quiet: bool = False,
    attachments: list = None,
) -> bool:
    fpath = _resolve(filepath)

    if fpath.suffix.lower() != ".md":
        if not quiet:
            print(f"跳过非md文件：{fpath}")
        return False

    if not fpath.is_file():
        if not quiet:
            print(f"文件不存在：{fpath}")
        return False

    # mtime变化检测
    current_mtime = fpath.stat().st_mtime
    last = _last_mtime(fpath)
    if not force and last is not None and current_mtime == last:
        if not quiet:
            print(f"文件未变化，跳过：{fpath.name}")
        return True

    raw = fpath.read_text(encoding="utf-8")
    body, fm = _strip_frontmatter(raw)

    # 确定标题：--title > frontmatter.title > md首行标题 > 已存储 > 文件名stem
    if title is None:
        title = fm.get("title")
    if title is None:
        title = _extract_heading(body)
    if title is None:
        title = _stored_title(fpath)
    if title is None:
        title = fpath.stem
    title = _make_title(fpath, title)

    note_id = _note_id(fpath)
    is_new = note_id is None

    if dry_run:
        action = "将创建" if is_new else "将更新"
        print(f"[dry-run] {action}《{title}》← {fpath}")
        return True

    parent_id = searchnotebook(notebook or DEFAULT_NOTEBOOK)

    if is_new:
        results = searchnotes(title)
        hit = next((r for r in results if r.title == title), None)
        if hit:
            note_id = hit.id
            updatenote_body(note_id, body)
            _save(fpath, note_id, title, current_mtime)
            log.info(f"标题《{title}》精确匹配已有笔记{note_id}，补录映射+更新内容")
        else:
            note_id = createnote(title, body, parent_id=parent_id)
            log.info(f"新建笔记《{title}》（{note_id}）")
            _save(fpath, note_id, title, current_mtime)
            if not quiet:
                print(f"已创建笔记《{title}》← {fpath}")
    else:
        updatenote_body(note_id, body)

        stored = _stored_title(fpath)
        if title != stored:
            updatenote_title(note_id, title)
            log.info(f"标题更新：《{stored}》→《{title}》")

        _save(fpath, note_id, title, current_mtime)
        if not quiet:
            print(f"已更新笔记《{title}》← {fpath}")

    if attachments:
        for f in attachments:
            res_id = jpapi.add_resource(str(f), title=Path(f).name)
            jpapi.add_resource_to_note(res_id, note_id)
            log.info(f"附件《{Path(f).name}》→ 笔记《{title}》（{res_id}）")
            if not quiet:
                print(f"  已上传附件：{Path(f).name}")

    return True


def list_mappings():
    cfp, _ = getcfp(CFG_NAME)
    sections = cfp.sections()
    if not sections:
        print("暂无映射")
        return
    for sec in sections:
        nid = cfp.get(sec, "note_id", fallback="?")
        ttl = cfp.get(sec, "title", fallback="?")
        print(f"{sec}\n  标题: {ttl}  笔记id: {nid}")


def remove_mapping(filepath: str):
    fpath = str(_resolve(filepath))
    removesection(CFG_NAME, fpath)
    print(f"已移除映射：{fpath}")


def _find_project_md_files(project_root: str) -> list:
    """扫描项目中的 docs/*.md 和 *.md 文件"""
    files = []
    root = Path(project_root)

    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for f in sorted(docs_dir.glob("*.md")):
            if f.is_file():
                files.append(str(f))

    for f in sorted(root.glob("*.md")):
        if f.is_file():
            files.append(str(f))

    return files


def main():
    parser = argparse.ArgumentParser(
        description="将 markdown 文件同步到 Joplin 笔记（func 通用版）"
    )
    parser.add_argument("files", nargs="*", help="要同步的md文件路径（可多个）")
    parser.add_argument("--title", "-t", help="自定义笔记标题（默认：frontmatter > md首行标题 > 文件名）")
    parser.add_argument("--notebook", "-n", help="目标笔记本名称（默认：ewmobile）")
    parser.add_argument("--dry-run", "-d", action="store_true", help="预览模式，不执行实际操作")
    parser.add_argument("--force", "-f", action="store_true", help="强制重新同步（跳过mtime检查）")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式，仅输出错误")
    parser.add_argument("--attach", "-a", nargs="+", help="上传附件到笔记（可多个）")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有已映射文件")
    parser.add_argument("--remove", "-r", action="store_true", help="移除指定文件的映射（不删笔记）")
    parser.add_argument(
        "--find-files", action="store_true",
        help="自动扫描项目目录下的 docs/*.md 和 *.md"
    )

    args = parser.parse_args()

    if args.list:
        list_mappings()
        return

    if args.remove:
        if not args.files:
            print("请指定要移除映射的文件")
            sys.exit(1)
        for f in args.files:
            remove_mapping(f)
        return

    # 确定待同步文件列表
    files_to_sync: list = args.files
    if args.find_files:
        files_to_sync = _find_project_md_files(str(getdirmain()))

    if not files_to_sync:
        if not args.find_files:
            parser.print_help()
        sys.exit(1)

    for f in files_to_sync:
        sync_file(
            f,
            title=args.title,
            notebook=args.notebook,
            force=args.force,
            dry_run=args.dry_run,
            quiet=args.quiet,
            attachments=args.attach,
        )


if __name__ == "__main__":
    if not_IPython():
        log.info(f"开始运行文件\t{__file__}")

    main()

    if not_IPython():
        log.info(f"Done.结束执行文件\t{__file__}")
