import face_recognition
import cv2
import numpy as np
import os
import json

# import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Path to save user profiles
USER_DATA_PATH = "user_profiles.json"

# Load user profiles from a JSON file
def load_user_profiles():
    if os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, "r") as f:
            return json.load(f)
    return {}

# Save user profiles to a JSON file
def save_user_profiles(profiles):
    with open(USER_DATA_PATH, "w") as f:
        json.dump(profiles, f, indent=4)

# Add a new user profile
def add_user_profile(name, encoding):
    profiles = load_user_profiles()
    profiles[name] = encoding.tolist()
    save_user_profiles(profiles)
    print(f"User {name} added successfully.")

# Authenticate a user based on face recognition
def authenticate_user(frame, known_face_encodings, known_face_names):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            return known_face_names[best_match_index]
    return None

# Capture a face and encode it for a new user
def capture_user_face(name):
    cap = cv2.VideoCapture(0)
    print("Capturing face. Please look at the camera.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):  # Press 'c' to capture
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            if len(face_locations) == 1:
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                add_user_profile(name, face_encoding)
                break
            else:
                print("No face or multiple faces detected. Try again.")
        elif key == ord("q"):  # Press 'q' to quit
            break
    cap.release()
    cv2.destroyAllWindows()

# Main function to run the system
def main():
    print("Loading user profiles...")
    user_profiles = load_user_profiles()
    known_face_names = list(user_profiles.keys())
    known_face_encodings = [np.array(enc) for enc in user_profiles.values()]

    print("Options:\n1. Add New User\n2. Authenticate User\n3. Exit")
    choice = input("Enter your choice: ").strip()

    if choice == "1":
        name = input("Enter the name of the new user: ").strip()
        capture_user_face(name)
    elif choice == "2":
        print("Starting authentication. Press 'q' to quit.")
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame.")
                break
            user = authenticate_user(frame, known_face_encodings, known_face_names)
            if user:
                print(f"Authentication Successful! Welcome, {user}.")
                break
            cv2.imshow("Authentication", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()
    elif choice == "3":
        print("Exiting system.")
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
