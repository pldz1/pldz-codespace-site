import os
import sys
import uuid
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core import Logger, ProjectConfig
from scripts.db.connection import _lock, _read_json, _write_json, get_articles_db_path
from .article_crud import ArticleCrudHandler, ArticleDocument

ARTICLES_DIR = ProjectConfig.get_articles_path()


def sync_file(file_path: str):
    """同步单个 Markdown 文件的元数据到 JSON 索引（不存 content）"""
    doc: ArticleDocument = ArticleCrudHandler.get_file_doc(file_path)
    if not doc:
        Logger.info(f"❗ 无法处理文件: {file_path}")
        return
    db = get_articles_db_path()
    with _lock:
        data = _read_json(db)
        existing = data.get(doc['id'])
        entry = {
            'id': doc['id'],
            'path': doc['path'],
            'meta': doc['meta'],
            'views': existing.get('views', 0) if existing else 0,
        }
        action = '更新' if existing else '插入'
        data[doc['id']] = entry
        _write_json(db, data)
    Logger.info(f"✔ {action} 文件: {doc['path']}")


class MarkdownEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            Logger.info(f"检测到新文件: {event.src_path}")
            sync_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            Logger.info(f"检测到修改: {event.src_path}")
            sync_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            Logger.info(f"检测到重命名: {event.src_path} -> {event.dest_path}")
            sync_file(event.dest_path)
            rel = os.path.relpath(event.src_path, ARTICLES_DIR)
            pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]
            db = get_articles_db_path()
            with _lock:
                data = _read_json(db)
                if pid in data:
                    del data[pid]
                    _write_json(db, data)
                    Logger.info(f"✖ 删除旧记录: {rel}")

    def on_deleted(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            rel = os.path.relpath(event.src_path, ARTICLES_DIR)
            pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]
            db = get_articles_db_path()
            with _lock:
                data = _read_json(db)
                if pid in data:
                    del data[pid]
                    _write_json(db, data)
                    Logger.info(f"✖ 删除记录: {rel}")


def initial_sync():
    """首次启动时将已有文件全部同步"""
    Logger.info("开始初次全量同步...")
    count = 0
    for root, _, files in os.walk(ARTICLES_DIR):
        for f in files:
            if f.lower().endswith('.md'):
                sync_file(os.path.join(root, f))
                count += 1
    Logger.info(f"初次同步完成，共同步 {count} 个文件。")


def start_watch(isWatch: bool = True):
    """启动文件监控服务"""
    if not os.path.isdir(ARTICLES_DIR):
        Logger.info(f"目录不存在: {ARTICLES_DIR}")
        sys.exit(1)

    initial_sync()

    if not isWatch:
        Logger.info("非监控模式，已完成初次同步。")
        return

    Logger.info("开始监控目录变动，按 Ctrl+C 停止")
    event_handler = MarkdownEventHandler()
    observer = Observer()
    observer.schedule(event_handler, ARTICLES_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        Logger.info("监控停止，退出中...")
        observer.stop()
    observer.join()
    Logger.info("Bye!")
