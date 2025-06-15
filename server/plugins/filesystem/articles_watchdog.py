# -*- coding: utf-8 -*-
"""
@file   : articles_watchdog.py
@time   : 2025/06/08
@desc   : 监听指定目录下的 Markdown 文件变动，自动同步到 MongoDB 数据库。
"""

import os
import sys
import uuid
import time
import datetime
import frontmatter
from pymongo.errors import PyMongoError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 导入 MongoDB 连接函数
from plugins.mongodb import get_article_mongo_collection


# 导入项目的配置
from scripts.libs import LOGGER, CONF

# ---------- 配置部分 ----------
# 根据实际情况调整目录层级
ARTICLES_DIR = CONF.get_abs_path('articles')


# ---------- 公共函数 ----------


def normalize_meta(obj):
    """递归将 metadata 中的 date/datetime 转为 ISO，防止 BSON 序列化错误"""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: normalize_meta(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_meta(v) for v in obj]
    return obj


def sync_file(file_path, coll):
    """将单个 Markdown 文件同步到 MongoDB"""
    try:
        post = frontmatter.load(file_path)
    except Exception as e:
        LOGGER.info(f"❗ 无法读取 {file_path}: {e}")
        return

    rel = os.path.relpath(file_path, ARTICLES_DIR)
    pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]

    # 处理 metadata，确保日期格式正确
    meta = normalize_meta(post.metadata)

    # 写入mongodb的文档格式
    # 这里的 id 是基于文件相对路径生成的 UUID，确保唯一性
    doc = {'id': pid, 'path': rel, 'meta': meta, 'content': post.content}
    try:
        res = coll.update_one({'id': pid}, {'$set': doc}, upsert=True)
        action = '插入' if res.upserted_id else '更新'
        LOGGER.info(f"✔ {action} 文件: {rel}")
    except PyMongoError as e:
        LOGGER.info(f"❗ 写入失败 {rel}: {e}")


# ---------- 监控处理器 ----------
class MarkdownEventHandler(FileSystemEventHandler):
    def __init__(self, collection):
        self.coll = collection

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            LOGGER.info(f"检测到新文件: {event.src_path}")
            sync_file(event.src_path, self.coll)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            LOGGER.info(f"检测到修改: {event.src_path}")
            sync_file(event.src_path, self.coll)

    def on_deleted(self, event):
        # 可选：同步删除操作
        if not event.is_directory and event.src_path.lower().endswith('.md'):
            rel = os.path.relpath(event.src_path, ARTICLES_DIR)
            pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]
            try:
                self.coll.delete_one({'id': pid})
                LOGGER.info(f"✖ 删除记录: {rel}")
            except PyMongoError as e:
                LOGGER.info(f"❗ 删除失败 {rel}: {e}")


# ---------- 主逻辑 ----------
def initial_sync(coll):
    """首次启动时将已有文件全部同步"""
    LOGGER.info("开始初次全量同步...")
    count = 0
    for root, _, files in os.walk(ARTICLES_DIR):
        for f in files:
            if f.lower().endswith('.md'):
                fp = os.path.join(root, f)
                sync_file(fp, coll)
                count += 1
    LOGGER.info(f"初次同步完成，共同步 {count} 个文件。")


def start_watch(isWatch: bool = True):
    """启动文件监控服务
    Args:
        isWatch (bool): 是否启用监控模式
    """
    if not os.path.isdir(ARTICLES_DIR):
        LOGGER.info(f"目录不存在: {ARTICLES_DIR}")
        sys.exit(1)
    coll = get_article_mongo_collection()
    # 全量同步
    initial_sync(coll)

    if not isWatch:
        LOGGER.info("非监控模式，已完成初次同步。")
        return

    # 开始监控
    LOGGER.info("开始监控目录变动，按 Ctrl+C 停止")
    event_handler = MarkdownEventHandler(coll)
    observer = Observer()
    observer.schedule(event_handler, ARTICLES_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOGGER.info("监控停止，退出中...")
        observer.stop()
    observer.join()
    LOGGER.info("Bye!")
