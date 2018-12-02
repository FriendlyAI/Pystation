from threading import Thread


def thread(f):
    def run(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
        return t

    return run
