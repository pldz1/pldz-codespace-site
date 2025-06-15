import threading

if __name__ == '__main__':
    # 初始化 core 内的配置和日志
    from core import ProjectConfig, Logger
    ProjectConfig.load_env()
    Logger.init_logger()
    Logger.info("Project configuration and logger initialized.")

    # 直接调用 start_watch() 会阻塞主线程，使用线程可以避免这个问题
    from scripts.filesystem import start_watch
    threading.Thread(target=start_watch, args=(True,), daemon=True).start()

    # 创建管理员账户
    from scripts.mongodb import AuthorizedHandler
    AuthorizedHandler.init_admin()

    # 启动 fastapi 应用
    from routes import run_dev
    run_dev()
