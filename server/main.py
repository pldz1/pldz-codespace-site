import threading

if __name__ == '__main__':
    # 直接调用 start_watch() 会阻塞主线程，使用线程可以避免这个问题
    from plugins.filesystem import start_watch
    threading.Thread(target=start_watch, args=(False,), daemon=True).start()

    from plugins.mongodb.authenticated import AuthorizedHandler
    AuthorizedHandler.init_admin()

    from scripts.apis import run_dev
    run_dev()
