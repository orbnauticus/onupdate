#!/usr/bin/env python3

import argparse
import logging
import os
import time

from .watch import Watcher, shell_function

parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('command', nargs='+')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Show all information, equivalent to -ctx')
parser.add_argument('-c', '--show-cmd', action='store_true')
parser.add_argument('-t', '--show-time', action='store_true')
parser.add_argument('-x', '--show-exit', action='store_true')
parser.add_argument('-s', '--sensitivity', type=float, default=1.0,
                    help='Time in seconds to wait before refreshing again')
parser.add_argument('-r', '--recursive', action='store_true')
parser.add_argument('-1', '--first-run', action='store_true',
                    help='Also run command once when onupdate is invoked')
args = parser.parse_args()

args.path = os.path.abspath(args.path)

if args.verbose:
    args.show_cmd = \
    args.show_time = \
    args.show_exit = True

args.show_count = True

args.delay = 0.1

logger = logging.getLogger('onupdate')
logging.basicConfig(level=logging.INFO)

@Watcher(args.path, args.recursive, args.first_run, delay=args.delay,
         sensitivity=args.sensitivity)
def watcher():
    if args.show_cmd:
        logger.info("Running %s", ' '.join(args.command))
    if args.show_time:
        logger.info("Execution began at %s",
            time.strftime('[%Y-%m-%d %H:%M:%S]'))
    result = shell_function(args.command)
    if args.show_exit:
        logger.info("Command exited with status %i", result)

watcher.run()
