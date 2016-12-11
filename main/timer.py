# -*- coding: cp1252 -*-
import threading
import time


class Timer:
    def __init__(self, tempo, target, args=[], kwargs={}):
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._tempo = tempo
        self._timer = threading.Timer(self._tempo, self._run)

    def _run(self):
        while True:
            self._timer.start()
            self._target(*self._args, **self._kwargs)

    def start(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()

    def stop(self):
        self._timer.cancel()
