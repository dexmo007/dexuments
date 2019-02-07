import sys
import time
import pickle
import os
import json
import uuid
import face_recognition

from pathutils import iterfiles


class FaceManager:
    def __init__(self, dex_dir, db_mgr):
        self.db_path = os.path.join(dex_dir, 'faces.dat')
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, mode='rb') as f:
                    self.db = pickle.load(f)
            except Exception as e:
                print('error loading faces: ' + e)
                self.db = {}
        else:
            self.db = {}
        self.db_mgr = db_mgr

    def is_known_face(self, encoding):
        """returned the face id if the face is recognized otherwise None"""
        for face_id, person in self.db.items():
            results = face_recognition.compare_faces(person, encoding)
            if any(results):
                return face_id
        return None

    def submit(self, img_paths):
        any_changes = False
        for f in img_paths:
            self.db_mgr.clear_face_mappings(f)
            image = face_recognition.load_image_file(f)
            face_locations = face_recognition.face_locations(image)
            encodings = face_recognition.face_encodings(image, face_locations)
            for encoding, (top, right, bottom, left) in zip(encodings, face_locations):
                face_id = self.is_known_face(encoding)
                if face_id is not None:
                    self.db[face_id].append(encoding)
                else:
                    face_id = str(uuid.uuid4())
                    self.db[face_id] = [encoding]
                self.db_mgr.save_face_mapping(
                    face_id, f, top, right, bottom, left)
                any_changes = True
        if any_changes:
            self.persist()

    def persist(self):
        with open(self.db_path, mode='wb') as f:
            pickle.dump(self.db, f)
