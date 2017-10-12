from queue import Queue
from threading import Thread


def multiplex(n, q, **kwargs):
    """ Convert one queue into several equivalent Queues

    >>> q1, q2, q3 = multiplex(3, in_q)
    """
    out_queues = [Queue(**kwargs) for i in range(n)]

    def f():
        while True:
            x = q.get()
            for out_q in out_queues:
                out_q.put(x)

    t = Thread(target=f)
    t.daemon = True
    t.start()
    return out_queues


def push(in_q, out_q):
    while True:
        x = in_q.get()
        out_q.put(x)


def merge(*in_qs, **kwargs):
    """ Merge multiple queues together

    >>> out_q = merge(q1, q2, q3)
    """
    out_q = Queue(**kwargs)
    threads = [Thread(target=push, args=(q, out_q)) for q in in_qs]
    for t in threads:
        t.daemon = True
        t.start()
    return out_q
