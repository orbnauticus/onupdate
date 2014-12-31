
import os
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent
from subprocess import Popen,PIPE
import time

import logging
logger = logging.getLogger('onupdate')


def shell_function(command):
    proc = Popen(command)
    proc.communicate()
    return proc.returncode


class Event(ProcessEvent):
    def __init__(self, watcher):
        self.last_run = 0
        self.watcher = watcher

    def process_default(self, event):
        now = time.time()
        if event.mask in (EventsCodes.ALL_FLAGS['IN_CLOSE_WRITE'],
                          EventsCodes.ALL_FLAGS['IN_MODIFY']):
            if event.pathname == self.watcher.path:
                pass
            elif self.watcher.recursive and event.pathname.startswith(self.watcher.folder):
                pass
            else:
                return
            if now - self.last_run > self.watcher.sensitivity:
                self.run_cmd()

    def run_cmd(self, immediate=False):
        if not immediate:
            time.sleep(self.watcher.delay)
        result = self.watcher.function()
        self.last_run = time.time()


class Watcher(object):
    def __init__(self, path, recursive=False, first_run=True, delay=0.1,
                 sensitivity=1, function=None):
        self.path = os.path.abspath(path)
        self.folder = (self.path if os.path.isdir(self.path)
                       else os.path.dirname(self.path))
        self.recursive = recursive
        self.first_run = first_run
        self.delay = delay
        self.sensitivity = sensitivity
        
        self.function = function

        self.watchmanager = WatchManager()
        self.event = Event(self)

    def __call__(self, function):
        self.function = function
        return self

    def interrupt(self):
        self.function = None

    def run(self):
        notifier = Notifier(self.watchmanager, self.event)
        descriptor = self.watchmanager.add_watch(
            self.folder, EventsCodes.ALL_FLAGS['ALL_EVENTS'],
            rec=self.recursive)
        logging.info('Watching %i folders', len(descriptor))
        if self.first_run:
            self.event.run_cmd(True)
        while True:
            try:
                notifier.process_events()
                if notifier.check_events():
                    notifier.read_events()
            except KeyboardInterrupt:
                notifier.stop()
                break

