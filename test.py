import sys
import face_recognition
import cv2

image = face_recognition.load_image_file(sys.argv[1])

face_locations = face_recognition.face_locations(image)

encodings = face_recognition.face_encodings(image, face_locations)
print(len(encodings))
for top, right, bottom, left in face_locations:
    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
    print(top, right, bottom, left)

    # Draw a box around the face
    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

cv2.imwrite('henni_and_ali_faced.jpg', image)
