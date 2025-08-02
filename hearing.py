import tkinter as tk
from tkinter import messagebox
import webbrowser
import json

# Set the path to the JSON file
JSON_FILE_PATH = "project R/hearing.json"

# Load course data from the JSON file
try:
    with open(JSON_FILE_PATH, 'r') as file:
        course_data = json.load(file)
    print("Course data loaded successfully from", JSON_FILE_PATH)
except FileNotFoundError:
    print(f"Error: The file {JSON_FILE_PATH} was not found.")
    messagebox.showerror("Error", f"The file {JSON_FILE_PATH} was not found.")
    course_data = {}  # Fallback to empty dict if file not found
except json.JSONDecodeError:
    print(f"Error: The file {JSON_FILE_PATH} contains invalid JSON.")
    messagebox.showerror("Error", f"The file {JSON_FILE_PATH} contains invalid JSON.")
    course_data = {}  # Fallback to empty dict if JSON is invalid

class SignLanguageCourseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Language Course Reader")
        self.root.geometry("600x400")

        self.current_course = ""
        self.current_video_index = 0
        self.video_list = []

        # Course selection
        tk.Label(root, text="Select Course:").pack(pady=5)
        self.course_var = tk.StringVar(root)
        if course_data:  # Check if course_data is not empty
            self.course_var.set(list(course_data.keys())[0])  # Default to first course
            tk.OptionMenu(root, self.course_var, *course_data.keys(), command=self.load_course).pack()
        else:
            self.course_var.set("No courses available")
            tk.OptionMenu(root, self.course_var, "No courses available").pack()

        # Video title display
        self.video_label = tk.Label(root, text="No video selected", font=("Arial", 14))
        self.video_label.pack(pady=10)

        # Navigation buttons
        self.prev_button = tk.Button(root, text="Previous", command=self.previous_video, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(root, text="Next", command=self.next_video, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_course)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Initialize with default course if data exists
        if course_data:
            self.load_course(self.course_var.get())

    def load_course(self, course):
        self.current_course = course
        self.current_video_index = 0
        self.video_list = course_data.get(self.current_course, [])
        self.update_video_display()
        self.update_buttons()

    def update_video_display(self):
        if self.video_list:
            video = self.video_list[self.current_video_index]
            self.video_label.config(text=video["title"])
            webbrowser.open(video["url"])  # Opens video in default browser
        else:
            self.video_label.config(text="No videos available")

    def next_video(self):
        if self.current_video_index < len(self.video_list) - 1:
            self.current_video_index += 1
            self.update_video_display()
            self.update_buttons()
        else:
            messagebox.showinfo("End", "No more videos in this course.")

    def previous_video(self):
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.update_video_display()
            self.update_buttons()

    def stop_course(self):
        self.root.quit()

    def update_buttons(self):
        self.prev_button.config(state=tk.NORMAL if self.current_video_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_video_index < len(self.video_list) - 1 else tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SignLanguageCourseApp(root)
    root.mainloop()