from threading import Thread


def thread(f):
    def run(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t

    return run
