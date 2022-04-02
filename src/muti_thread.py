import threading
import math


def fun(params):
    for param in params:
        print(param)


task = [
    (fun, 123,),
]
task_index: int = 0
lock: threading.Lock = threading.Lock()


def proc():
    while True:
        execute = get_task()
        if execute is None:
            break
        else:
            func = execute[0]
            params = execute[1:]
            func(params)


def get_task():
    lock.acquire()
    global task_index
    if task_index == len(task):
        lock.release()
        return None
    else:
        func = task[task_index]
        task_index = task_index + 1
        lock.release()
        return func


class MutiThreadExecute(threading.Thread):
    def __init__(self, thread_id: int):
        threading.Thread.__init__(self)
        self.thread_id = thread_id

    def run(self):
        print("Thread {} start...".format(self.thread_id))
        proc()
        print("Thread {} end!".format(self.thread_id))


def muti_thread_execute(thread_count: int):
    for i in range(0, thread_count):
        MutiThreadExecute(i).start()


def split(func, begin_page: int, end_page: int, divide_count: int):
    task_list = []
    base: int = math.ceil((end_page - begin_page) / divide_count)
    task_begin: int = begin_page
    task_end: int
    while True:
        task_end = task_begin + base
        if task_end > end_page:
            task_end = end_page
            if task_begin != task_end:
                task_list.append((func, task_begin, task_end))
            return task_list
        else:
            task_list.append((func, task_begin, task_end))
            task_begin = task_end
