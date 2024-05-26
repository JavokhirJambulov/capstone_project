import cv2
import compare_functions
import telegram_messenger
import time
import sqlite3
from datetime import datetime

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Connect to SQLite database
conn = sqlite3.connect('face_capture.db')
c = conn.cursor()

# Clear the table
c.execute("DELETE FROM face_captures")
conn.commit()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS face_captures
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, capture_time TEXT)''')

# To capture video from webcam.
cap = cv2.VideoCapture(0)
last_person = 'Not recognized'
count_same_person = 0
# To execute the code continuously
while True:
    # Read the frame
    _, img = cap.read()
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    cropped_image = gray

    # Draw the rectangle around each face and crop the image
    for (x, y, w, h) in faces:
        cropped_image = gray[y:y + h + 30, x:x + w + 30]

    # Save the image
    if len(faces) >= 1:
        status = cv2.imwrite('images/test.jpeg', cropped_image)
        print("image saved " + str(len(faces)))
        # To detect faces of the people
        person_name = compare_functions.compare_images('images/test.jpeg')
        # Get current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # To check if the face and emotion of the person  is the same
        if last_person == person_name and person_name != 'Unknown':
            # Used to count the same person
            count_same_person += 1
        else:
            count_same_person = 0
        print(count_same_person)



        if last_person != person_name and person_name != 'Unknown':  # (last_person != person_name or last_emotion != current_emotion) and current_emotion != "None":

            # Insert data into database
            c.execute("INSERT INTO face_captures (name, capture_time) VALUES (?, ?)", (person_name, current_time))
            conn.commit()
            # If the face and emotion changes, it will send it to owner via Telegram
            if count_same_person <= 3:
                time.sleep(1)
                telegram_messenger.send_attendance(person_name)
                # telegram_messenger.send_emotion_and_person_on_door(person_name, current_emotion)
                telegram_messenger.send_image('images/test.jpeg')
            # To save the person's last known face and emotion
            last_person = person_name
            # last_emotion = current_emotion
        time.sleep(1)
    else:
        print('no face recognized')


    # execute the command to fetch all the data from the table emp
    c.execute("SELECT * FROM face_captures")

    # store all the fetched data in the ans variable
    ans = c.fetchall()
    for i in ans:
        print(i)
    # Stop if escape key is pressed
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break




# Release the VideoCapture object
cap.release()
cv2.destroyAllWindows()

# Close database connection
conn.close()
