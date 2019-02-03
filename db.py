import sqlite3
import os

class DbManager:
    def __init__(self, db_file, root):
        self.db_file = db_file
        self.root = root
        self.connection = None
    
    def connect(self):
        if self.connection is not None:
            return
        self.connection = sqlite3.connect(self.db_file)
        self.c = self.connection.cursor()
        self.c.execute('CREATE VIRTUAL TABLE IF NOT EXISTS docs USING FTS5(path,text,classification)')
        self.c.execute('''CREATE TABLE IF NOT EXISTS face_mapping (
            face_id varchar(36) not null,
            img_path varchar(255) not null,
            x integer not null,
            y integer not null,
            width integer not null,
            height integer not null
        )
        ''')

    def save(self, path, text, classification=None):
        self.connect()
        self.c.execute('DELETE FROM docs WHERE path = ?', (path,))
        if classification is not None:
            self.c.execute('INSERT INTO docs VALUES (?,?,?)',(path,text,classification,))
        else:
            self.c.execute('INSERT INTO docs VALUES(?, ?)', (path, text, ))
        self.connection.commit()

    def save_face_mapping(self, face_id, path, x, y, width, height):
        self.connect()
        normalized_path = os.path.relpath(path, start=self.root)
        self.c.execute('INSERT INTO face_mapping VALUES (?,?,?,?,?,?)',(face_id, normalized_path,x,y,width,height,))
        self.connection.commit()

    def clear_face_mappings(self, path):
        normalized_path = os.path.relpath(path, start=self.root)
        self.connect()
        self.c.execute('DELETE FROM face_mapping WHERE img_path = ?', (normalized_path, ))
        self.connection.commit()

    def remove(self, path):
        self.connect()
        self.c.execute('DELETE FROM docs WHERE path = ?', (path,))
        self.connection.commit()

    def remove_directory(self, directory):
        self.connect()
        self.c.execute('DELETE FROM docs WHERE path like ?', (directory+'%', ))
        self.connection.commit()

    def update_path(self, old_path, new_path):
        self.connect()
        self.c.execute('UPDATE docs SET path = ? WHERE path = ?',(new_path, old_path, ))
        self.connection.commit()

    def update_directory(self, old_directory, new_directory):
        self.connect()
        
        self.c.execute('')
        self.connection.commit()

    def close(self):
        self.connection.close()
