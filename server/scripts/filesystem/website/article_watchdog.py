import os
import sys
import uuid
import time
from pymongo.errors import PyMongoError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# 导入项目的配置
from core import Logger, ProjectConfig

# 导入 MongoDB 连接函数
from scripts.mongodb import get_article_mongo_collection
from .article_crud import ArticleCrudHandler, ArticleDocument


# ---------- 配置部分 ----------
# 根据实际情况调整目录层级
ARTICLES_DIR = ProjectConfig.get_articles_path()


def sync_file(file_path, coll):
    """同步单个 Markdown 文件到 MongoDB
    Args:
        file_path (str): 文件的绝对路径
        coll: MongoDB 集合对象
    """
    doc: ArticleDocument = ArticleCrudHandler.get_file_doc(file_path)
    if not doc:
        Logger.info(f"❗ 无法处理文件: {file_path}")
        return
    try:
        res = coll.update_one({'id': doc['id']}, {'$set': doc}, upsert=True)
        action = '插入' if res.upserted_id else '更新'
        Logger.info(f"✔ {action} 文件: {doc['path']}")
    except PyMongoError as e:
        Logger.info(f"❗ 写入失败 {doc['path']}: {e}")


# ---------- 监控处理器 ----------
class MarkdownEventHandler(FileSystemEventHandler):
    def __init__(self, collection):
        self.coll = collection

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            Logger.info(f"检测到新文件: {event.src_path}")
            sync_file(event.src_path, self.coll)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            Logger.info(f"检测到修改: {event.src_path}")
            sync_file(event.src_path, self.coll)

    def on_deleted(self, event):
        # 可选：同步删除操作
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            rel = os.path.relpath(event.src_path, ARTICLES_DIR)
            pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]
            try:
                self.coll.delete_one({'id': pid})
                Logger.info(f"✖ 删除记录: {rel}")
            except PyMongoError as e:
                Logger.info(f"❗ 删除失败 {rel}: {e}")


# ---------- 主逻辑 ----------
def initial_sync(coll):
    """首次启动时将已有文件全部同步"""
    Logger.info("开始初次全量同步...")
    count = 0
    for root, _, files in os.walk(ARTICLES_DIR):
        for f in files:
            if f.lower().endswith('.md'):
                fp = os.path.join(root, f)
                sync_file(fp, coll)
                count += 1
    Logger.info(f"初次同步完成，共同步 {count} 个文件。")


def start_watch(isWatch: bool = True):
    """启动文件监控服务
    Args:
        isWatch (bool): 是否启用监控模式
    """
    if not os.path.isdir(ARTICLES_DIR):
        Logger.info(f"目录不存在: {ARTICLES_DIR}")
        sys.exit(1)
    coll = get_article_mongo_collection()
    # 全量同步
    initial_sync(coll)

    if not isWatch:
        Logger.info("非监控模式，已完成初次同步。")
        return

    # 开始监控
    Logger.info("开始监控目录变动，按 Ctrl+C 停止")
    event_handler = MarkdownEventHandler(coll)
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
