import json
import asyncio
import subprocess
import typing
from typing import AsyncGenerator, Any


from core import ProjectConfig, Logger


GIT_REPO_PATH = ProjectConfig.get_git_repo_path()


class GitSyncReturn(typing.TypedDict):
    """
    Git同步返回类型
    """
    flag: bool
    message: str


class GitHandler:
    @classmethod
    def git_pull(cls) -> GitSyncReturn:
        """
        从远程Git仓库拉取最新代码
        """
        try:
            result = subprocess.run(['git', '-C', GIT_REPO_PATH, 'pull'], capture_output=True, text=True, check=True)
            return {'flag': True, 'message': result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            Logger.error(f"Git pull error: {e.stderr.strip()}")
            return {'flag': False, 'message': "Error pulling from git " + e.stderr.strip()}

    @classmethod
    def git_status(cls) -> GitSyncReturn:
        """
        获取Git仓库的状态
        """
        try:
            result = subprocess.run(['git', '-C', GIT_REPO_PATH, 'status'], capture_output=True, text=True, check=True)
            return {'flag': True, 'message': result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            Logger.error(f"Git status error: {e.stderr.strip()}")
            return {'flag': False, 'message': "Error retrieving git status " + e.stderr.strip()}

    @classmethod
    def git_add_all(cls) -> GitSyncReturn:
        """
        添加文件到Git暂存区
        """
        try:
            result = subprocess.run(['git', '-C', GIT_REPO_PATH, 'add', '.'], capture_output=True, text=True, check=True)
            return {'flag': True, 'message': result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            Logger.error(f"Git add error: {e.stderr.strip()}")
            return {'flag': False, 'message': "Error adding file to git " + e.stderr.strip()}

    @classmethod
    def git_commit(cls, message: str) -> GitSyncReturn:
        """
        提交更改到Git仓库
        """
        try:
            result = subprocess.run(['git', '-C', GIT_REPO_PATH, 'commit', '-am', message], capture_output=True, text=True, check=True)
            return {'flag': True, 'message': result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            Logger.error(f"Git commit error: {e.stderr.strip()}")
            return {'flag': False, 'message': "Error committing changes" + e.stderr.strip()}

    @classmethod
    def git_push(cls) -> GitSyncReturn:
        """
        推送更改到远程Git仓库
        """
        try:
            result = subprocess.run(['git', '-C', GIT_REPO_PATH, 'push'], capture_output=True, text=True, check=True)
            return {'flag': True, 'message': result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            Logger.error(f"Git push error: {e.stderr.strip()}")
            return {'flag': False, 'message': "Error pushing changes" + e.stderr.strip()}

    @classmethod
    async def git_sync(cls, commit_message: str) -> AsyncGenerator[str, Any]:
        """
        同步Git仓库
        Args:
            commit_message (str): 提交信息
        Yields:
            str: 包含同步状态的JSON字符串
        """
        try:
            # 先拉取最新代码
            pull_data: GitSyncReturn = cls.git_pull()
            if not pull_data['flag']:
                # 如果拉取失败，不再继续执行
                err_payload = {
                    'status': 'error',
                    'message': f'Error pulling from git: {pull_data["message"]}'
                }
                yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
                return
            else:
                payload = {
                    'status': 'in_progress',
                    'message': f'Git pull completed successfully.\n{pull_data["message"]}'
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            await asyncio.sleep(2)
            status_data: GitSyncReturn = cls.git_status()

            if not status_data['flag']:
                # 如果获取状态失败，不再继续执行
                err_payload = {
                    'status': 'error',
                    'message': f'Error retrieving git status: {status_data["message"]}'
                }
                yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
                return
            else:
                # 现在才 yield，这个方法就成了 async-generator
                payload = {
                    'status': 'in_progress',
                    'message': f'Starting git sync...\n{status_data["message"]}'
                }
                # 把 ensure_ascii=False 放到 json.dumps 里，而不是 payload dict 里
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            # 模拟一些异步准备工作
            await asyncio.sleep(1)

            # 1️⃣ 添加所有更改到暂存区
            add_data: GitSyncReturn = cls.git_add_all()
            if not add_data['flag']:
                err_payload = {
                    'status': 'error',
                    'message': f'Error adding files to git: {add_data["message"]}'
                }
                yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
                return
            else:
                payload = {
                    'status': 'in_progress',
                    'message': f'Files added to git successfully.\n{add_data["message"]}'
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            await asyncio.sleep(3)
            # 2️⃣ 提交更改
            commit_data: GitSyncReturn = cls.git_commit(commit_message)
            if not commit_data['flag']:
                err_payload = {
                    'status': 'error',
                    'message': f'Error committing changes: {commit_data["message"]}'
                }
                yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
                return
            else:
                payload = {
                    'status': 'in_progress',
                    'message': f'Changes committed successfully.\n{commit_data["message"]}'
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(5)
            # 3️⃣ 推送更改
            push_data: GitSyncReturn = cls.git_push()
            if not push_data['flag']:
                err_payload = {
                    'status': 'error',
                    'message': f'Error pushing changes: {push_data["message"]}'
                }
                yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
                return
            else:
                payload = {
                    'status': 'done',
                    'message': f'Git sync completed successfully.\n{push_data["message"]}'
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except Exception as e:
            # 捕获异常，也可以继续 yield 一条错误 event
            Logger.error(f"Git sync error: {e}")
            err_payload = {
                'status': 'error',
                'message': f'Error during git sync\n{e}'
            }
            yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"

    @classmethod
    async def get_pull_async(cls) -> AsyncGenerator[str, Any]:
        """
        异步获取Git仓库的最新代码
        Yields:
            str: 包含拉取状态的JSON字符串
        """
        pull_data = cls.git_pull()
        if not pull_data['flag']:
            err_payload = {
                'status': 'error',
                'message': f'Error pulling from git: {pull_data["message"]}'
            }
            yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
        else:
            payload = {
                'status': 'done',
                'message': f'Git pull completed successfully.\n{pull_data["message"]}'
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
