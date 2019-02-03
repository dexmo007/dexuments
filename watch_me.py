import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import reader
from db import DbManager
import os.path
import re
from event_handler import UpdateEventHandler
from faces import FaceManager
from reader import FileProcessor

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    # todo resync option 
    db_manager = DbManager('.dexuments/dex.db', path)
    face_manager = FaceManager('.dexuments', db_manager)
    event_handler = UpdateEventHandler(db_manager, path, FileProcessor(face_manager))
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