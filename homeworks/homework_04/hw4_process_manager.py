#!/usr/bin/env python
# coding: utf-8

from multiprocessing import Process, Manager
from time import time, sleep


class Task:

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def perform(self):
        return self.func(*self.args, **self.kwargs)


class TaskProcessor:

    def __init__(self, tasks_queue, time_create):
        self.tasks_queue = tasks_queue
        self.time_create = time_create

    def run(self):
        while not self.tasks_queue.empty():
            target = self.tasks_queue.get()
            job = Process(target=target.perform)
            job.start()
            job.join()


class TaskManager:

    def __init__(self, tasks_queue, n_workers, timeout):
        self.tasks_queue = tasks_queue
        self.number_of_workers = n_workers
        self.timeout = timeout
        self.workers = []

    def run(self):
        for id in range(self.number_of_workers):
            self.workers.append(TaskProcessor(self.tasks_queue, time()))
            self.workers[id].run()

        while not self.tasks_queue.empty():
            for id, worker in enumerate(self.workers):
                if not worker.is_alive():
                    worker.terminate()
                    del worker[id]
                    self.workers[id] = TaskProcessor(self.tasks_queue, time())
                    self.workers[id].run()

                if time() - worker.time_create > self.timeout:
                    worker.terminate()
                    del worker[id]
                    self.workers[id] = TaskProcessor(self.tasks_queue, time())
                    self.workers[id].run()
