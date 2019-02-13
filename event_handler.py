import os
import logging
from watchdog.events import FileSystemEventHandler
from textract.exceptions import ExtensionNotSupported


class RelativeFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, watched_folder):
        self.watched_folder = watched_folder

    def _normalize_path(self, file):
        return os.path.relpath(file, start=self.watched_folder)

    def on_any_event(self, event):
        event._src_path = self._normalize_path(event.src_path)
        if hasattr(event, 'dest_path'):
            event.dest_path = self._normalize_path(event.dest_path)


class UpdateEventHandler(RelativeFileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, db, watched_folder, file_processor):
        super(UpdateEventHandler, self).__init__(watched_folder)
        self.db = db
        self.file_processor = file_processor
        self.last_path = None

    def _on_possibly_new_content(self, filePath):
        """handles a file change"""
        filePath = os.path.join(self.watched_folder, filePath)
        try:
            text_content, classification = self.file_processor.read_text(
                filePath)
            self.db.save(filePath, text_content, classification)
        except ExtensionNotSupported:
            pass

    def on_moved(self, event):
        if not event.is_directory:
            self.db.update_path(event.src_path, event.dest_path)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        if self.last_path == event.src_path:
            return
        self.last_path = event.src_path

        if event.is_directory:
            return
        logging.info("Created file: %s", event.src_path)
        self._on_possibly_new_content(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            with_trailing_slash = event.src_path if event.src_path.endswith(
                '/') else event.src_path + '/'
            self.db.remove_directory(with_trailing_slash)
        else:
            self.db.remove(event.src_path)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        if self.last_path == event.src_path:
            return
        self.last_path = event.src_path

        if event.is_directory:
            # todo check rename
            return
        self._on_possibly_new_content(event.src_path)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)
