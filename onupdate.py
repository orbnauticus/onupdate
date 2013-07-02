#!/usr/bin/env python

import argparse
import os
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent
from subprocess import Popen,PIPE
import time

parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('command', nargs='+')
parser.add_argument('-v', '--verbose', action='store_true', help='Show all information, equivalent to -ctx')
parser.add_argument('-c', '--show-cmd', action='store_true')
parser.add_argument('-t', '--show-time', action='store_true')
parser.add_argument('-x', '--show-exit', action='store_true')
parser.add_argument('-s', '--sensitivity', type=float, help='Time in seconds to wait before refreshing again', default=1.0)
parser.add_argument('-r', '--recursive', action='store_true')
parser.add_argument('-1', '--first-run', action='store_true', help='Run command when onupdate is invoked')
args = parser.parse_args()
args.path = os.path.abspath(args.path)
if args.verbose:
	args.show_cmd = \
	args.show_time = \
	args.show_exit = True
args.show_count = True

mask = EventsCodes.ALL_FLAGS['ALL_EVENTS']

class PTmp(ProcessEvent):
	def __init__(self):
		self.last_run = 0

	def process_default(self, event):
		now = time.time()
		if (event.pathname == args.path or (args.recursive and not os.path.isdir(event.pathname))) and event.mask in (
			EventsCodes.ALL_FLAGS['IN_CLOSE_WRITE'],
			EventsCodes.ALL_FLAGS['IN_MODIFY'],
		) and now - self.last_run > args.sensitivity:
			self.run_cmd()

	def run_cmd(self):
		if args.show_time:
			print time.strftime('[%Y-%m-%d %H:%M:%S]'),
		if args.show_cmd:
			print ' '.join(args.command),
		proc = Popen(args.command)
		proc.communicate()
		self.last_run = time.time()
		if args.show_exit:
			print '-> %i' % proc.returncode,
		print
	

wm = WatchManager()
pe = PTmp()
notifier = Notifier(wm, pe)

folder = args.path
if not os.path.isdir(folder):
	folder,_ = os.path.split(folder)

wdd = wm.add_watch(folder, mask, rec=args.recursive)
if args.show_count:
	print 'Watching', len(wdd), 'folders'

if args.first_run:
	pe.run_cmd()

while True:
	try:
		notifier.process_events()
		if notifier.check_events():
			notifier.read_events()
	except KeyboardInterrupt:
		notifier.stop()
		break
