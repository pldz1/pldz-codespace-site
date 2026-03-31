import asyncio
import json
import os
import textwrap
from datetime import datetime
from typing import Any, AsyncGenerator, Optional
import uuid

from core import Logger, ProjectConfig
from scripts.db.connection import _lock, _read_json, _write_json, get_articles_db_path

ARTICLES_DIR = ProjectConfig.get_articles_path()
IMAGES_DIR = ProjectConfig.get_images_path()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@pldz1.com")


def get_article_id_by_path(path: str) -> Optional[str]:
    rel: str = os.path.relpath(path, ARTICLES_DIR)
    return uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]


def rename_article_file(article_id: str, filename: str) -> str:
    db = get_articles_db_path()
    with _lock:
        data = _read_json(db)
        doc = data.get(article_id)
        if not doc:
            Logger.warning(f"没有找到文章 ID: {article_id}")
            return ""
        path = doc['path']
        base_path = os.path.dirname(path)
        _, ext = os.path.splitext(os.path.basename(path))
        old_path = os.path.join(ARTICLES_DIR, path)
        new_rel = os.path.join(base_path, filename + ext)
        new_path = os.path.join(ARTICLES_DIR, new_rel)
        try:
            os.rename(old_path, new_path)
            Logger.info(f"文件重命名成功")
        except Exception as e:
            Logger.error(f"重命名文件失败: {e}")
            return ""
        pid = get_article_id_by_path(new_path)
        del data[article_id]
        doc['id'] = pid
        doc['path'] = new_rel
        data[pid] = doc
        _write_json(db, data)
    return pid


def create_category(category_name: str) -> bool:
    try:
        new_category_path = os.path.join(ARTICLES_DIR, category_name)
        new_image_path = os.path.join(IMAGES_DIR, category_name)
        os.makedirs(new_category_path, exist_ok=True)
        os.makedirs(new_image_path, exist_ok=True)

        Logger.info(f"创建新的分类目录: {new_category_path}")
        Logger.info(f"创建新的图像目录: {new_image_path}")

        about_file_path = os.path.join(new_category_path, 'ABOUT.md')
        datestr = datetime.now().strftime('%Y-%m-%d')
        md = f"""
        ---
        author: {ADMIN_USERNAME}
        category: {category_name}
        date: '{datestr}'
        serialNo: 0
        status: publish
        summary: {category_name}的随笔
        tags: []
        thumbnail:
        title: ABOUT
        ---

        # 🎉 前言

        创建 {category_name} 专栏
        """
        md = textwrap.dedent(md).lstrip("\n")
        with open(about_file_path, 'w', encoding='utf-8') as f:
            f.write(md)
        return True
    except Exception as e:
        Logger.error(f"创建分类目录失败: {e}")
        return False


def create_article_file(category: str, filename: str, username: str) -> str:
    try:
        new_file_path: str = os.path.join(ARTICLES_DIR, category, f"{filename}.md")
        datestr = datetime.now().strftime('%Y-%m-%d')
        md = f"""
        ---
        author: {username}
        category: {category}
        date: {datestr}
        serialNo: 99999
        status: publish
        summary:
        tags: []
        thumbnail:
        title: {filename}
        ---

        # {filename} !
        """
        md = textwrap.dedent(md).lstrip("\n")
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(md)
        Logger.info(f"文件创建成功: {new_file_path}")
        return get_article_id_by_path(new_file_path)
    except Exception as e:
        Logger.error(f"创建文件失败: {e}")
        return ""


def write_article_to_file(article_id: str) -> bool:
    """将 JSON 索引中的 meta 与 .md 文件中的 content 合并后写回 .md 文件"""
    with _lock:
        data = _read_json(get_articles_db_path())
    article = data.get(article_id)
    if not article:
        Logger.warning(f"没有找到文章 ID: {article_id}")
        return False
    try:
        from scripts.filesystem import ArticleCrudHandler
        full_path = os.path.join(ARTICLES_DIR, article['path'])
        file_doc = ArticleCrudHandler.get_file_doc(full_path)
        content = file_doc['content'] if file_doc else ''
        return ArticleCrudHandler.save_file(article['path'], article['meta'], content)
    except Exception as e:
        Logger.error(f"✖ 保存文章失败: {e}")
        return False


async def write_all_article() -> AsyncGenerator[str, Any]:
    with _lock:
        data = _read_json(get_articles_db_path())
    articles = list(data.values())
    if not articles:
        yield f"data: {json.dumps({'status': 'error', 'message': '没有找到文章'})}\n\n"
        return

    for idx, art in enumerate(articles, start=1):
        aid: str = art['id']
        title: str = art.get('meta', {}).get('title', '')
        try:
            write_article_to_file(aid)
            log = 'synced'
        except Exception as e:
            log = str(e)
        payload = f"index: {idx}, 'title': {title}, {log}."
        await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'status': 'in_process', 'message': payload})}\n\n"

    yield f"data: {json.dumps({'status': 'in_process', 'message': '全部文章同步完成.'})}\n\n"
