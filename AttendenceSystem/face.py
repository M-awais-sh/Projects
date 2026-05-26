import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
import csv
import pandas as pd


class AttendanceSystem:
    def __init__(self, images_path, attendance_dir):
        self.path = images_path
        self.attendance_dir = attendance_dir 
        self.images = []                 # All images in dataset
        self.classNames = []             # names of all images in dataset
        self.encoded_face_train = []     # numeral values of all faces of images in dataset
        self.attendance_records = set()

        # Create attendance directory if it doesn't exist
        if not os.path.exists(self.attendance_dir):
            os.makedirs(self.attendance_dir)

        self.attendance_file = self.get_daily_attendance_file()
        self.load_images()
        self.initialize_attendance_file()

    def get_daily_attendance_file(self):
        # Create a new file name with current date
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.attendance_dir, f'Attendance_{today}.csv')

    def load_images(self):
        mylist = os.listdir(self.path)
        for cl in mylist:
            curImg = cv2.imread(f'{self.path}/{cl}')
            if curImg is not None:
                self.images.append(curImg)
                self.classNames.append(os.path.splitext(cl)[0])
            else:
                print(f"Warning: Could not load image {cl}")

        print("Loaded names:", self.classNames)
        self.encoded_face_train = self.findEncodings(self.images)

    def initialize_attendance_file(self):
        # Create new file with headers
        if not os.path.exists(self.attendance_file) or os.path.getsize(self.attendance_file) == 0:
            with open(self.attendance_file, 'w', newline='') as f:
                writer = csv.writer(f)
                # Adding column width specifications
                writer.writerow(['Name', 'Time', 'Status'])

        # Load today's records
        try:
            df = pd.read_csv(self.attendance_file)    # data frame(table form) of data in csv attendance file
            self.attendance_records = set(df['Name'].values)
        except Exception as e:
            print(f"Starting fresh attendance record for today. Error: {str(e)}")
            with open(self.attendance_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Time', 'Status'])

    def findEncodings(self, images):
        encodeList = []
        for i, img in enumerate(images): # 
            try:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)   # convert BGR image to RGB 
                encoded_face = face_recognition.face_encodings(img)[0]
                encodeList.append(encoded_face)
            except IndexError:
                print(f"Warning: No face found in image {self.classNames[i]}")
            except Exception as e:
                print(f"Error processing image {self.classNames[i]}: {str(e)}")
        return encodeList

    def markAttendance(self, name):
        if name not in self.attendance_records:
            current_time = datetime.now().strftime('%I:%M %p')  # Changed time format

            with open(self.attendance_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([name, current_time, "Present"])

            self.attendance_records.add(name)
            print(f"Marked attendance for {name} at {current_time}")
            return True
        return False

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return

        last_detection_time = {}
        detection_cooldown = 5

        try:
            while True:
                success, img = cap.read()
                if not success:
                    print("Error: Could not read from webcam")
                    break

                imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                faces_in_frame = face_recognition.face_locations(imgS)
                encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)

                for encode_face, faceloc in zip(encoded_faces, faces_in_frame):
                    matches = face_recognition.compare_faces(self.encoded_face_train, encode_face, tolerance=0.6) #array of matched faces
                    faceDist = face_recognition.face_distance(self.encoded_face_train, encode_face)

                    if len(faceDist) > 0:
                        matchIndex = np.argmin(faceDist)
                        if matches[matchIndex]:
                            name = self.classNames[matchIndex].upper()
                            current_time = datetime.now()

                            if (name not in last_detection_time or
                                    (current_time - last_detection_time[name]).total_seconds() > detection_cooldown):

                                if self.markAttendance(name):
                                    last_detection_time[name] = current_time

                            y1, x2, y2, x1 = faceloc
                            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, name, (x1 + 6, y2 - 5),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                cv2.imshow('Webcam', img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    attendance_system = AttendanceSystem(
        images_path='D:/images_data',
        attendance_dir='D:/Attendance2'  # Changed to directory instead of single file
    )
    attendance_system.run()