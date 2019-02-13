#!/usr/bin/python3
import sys
import time
import logging
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import reader
from db import DbManager
import os.path
import re
from event_handler import UpdateEventHandler
from faces import FaceManager
from reader import FileProcessor

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='sub-command help', dest='sub')

watch_parser = subparsers.add_parser('watch')
watch_parser.add_argument('path', metavar='PATH')
watch_parser.add_argument('--resync', action='store_true',
                          help='If true the whole PATH is resynced')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    args = parser.parse_args()
    if args.sub == 'watch':
        path = args.path
        # todo resync option
        if args.resync:
            print('SHould resync')
        db_manager = DbManager('/home/dexmo/.dexuments/index.db', path)
        face_manager = FaceManager('/home/dexmo/.dexuments', db_manager)
        event_handler = UpdateEventHandler(
            db_manager, path, FileProcessor(face_manager))
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            db_manager.close()
        observer.join()
    elif args.sub == 'query':
        pass
