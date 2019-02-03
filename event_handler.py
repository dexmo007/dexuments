import os
import logging
from watchdog.events import FileSystemEventHandler
from textract.exceptions import ExtensionNotSupported

class UpdateEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""
    def __init__(self, db, watched_folder, file_processor):
        self.db = db
        self.watched_folder = watched_folder
        self.file_processor = file_processor

    def _normalize_path(self, file):
        return os.path.relpath(file, start=self.watched_folder)

    def _on_possibly_new_content(self, file):
        """handles a file change"""
        try:
            text_content, classification = self.file_processor.read_text(file)
            self.db.save(self._normalize_path(file), text_content, classification)
        except ExtensionNotSupported:
            pass

    def on_moved(self, event):
        super(UpdateEventHandler, self).on_moved(event)

        normalized_src_path = self._normalize_path(event.src_path)
        normalized_dest_path = self._normalize_path(event.dest_path)
        if not event.is_directory:
            self.db.update_path(normalized_src_path, normalized_dest_path)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, normalized_src_path,
                     normalized_dest_path)

    def on_created(self, event):
        super(UpdateEventHandler, self).on_created(event)

        normalized_src_path = self._normalize_path(event.src_path)
        if event.is_directory:
            return
        logging.info("Created file: %s", normalized_src_path)
        self._on_possibly_new_content(event.src_path)

    def on_deleted(self, event):
        super(UpdateEventHandler, self).on_deleted(event)
        normalized_path = self._normalize_path(event.src_path)
        if event.is_directory:
            with_trailing_slash = normalized_path if normalized_path.endswith('/') else normalized_path + '/'
            self.db.remove_directory(with_trailing_slash)
        else:
            self.db.remove(normalized_path)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, normalized_path)

    def on_modified(self, event):
        super(UpdateEventHandler, self).on_modified(event)
        if event.is_directory:
            # todo check rename
            return
        self._on_possibly_new_content(event.src_path)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)