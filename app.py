from flask import Flask, render_template, request, jsonify, redirect
import webbrowser
import speech_recognition as sr
import visually  # Import visually.py
import hearing  # Import hearing.py
import threading
import time
import random

app = Flask(__name__)

# State for visually impaired navigation
current_course = None
current_index = 0
topics_content = []

# Global flag to stop voice prompt
stop_voice_prompt = False

def ask_user_type():
    """
    Function to determine user type via voice or text input.
    Returns 'visually' for visually impaired, 'hearing' for hearing-impaired, 'none' for others.
    """
    global stop_voice_prompt
    visually.speak_text("Hello! Are you visually impaired? Please say yes or no. Hearing-impaired users, wait for text instructions.", post_delay=0.5)
    print("Asking user type via voice and text...")
    
    time.sleep(6.0)  # Ensure prompt is fully spoken
    
    response = visually.recognize_command("Say yes or no.", is_course_selection=False).lower().strip()
    print(f"Final user type recognition result: '{response}'")
    
    if stop_voice_prompt:
        print("Voice prompt interrupted by form submission")
        return "interrupted"
    
    words = response.split()
    for word in words:
        if word == "yes":
            visually.speak_text("Got it, you said yes.", post_delay=0.5)
            print("User confirmed visually impaired.")
            return "visually"
        elif word == "no":
            visually.speak_text("Understood, you said no.", post_delay=0.5)
            print("User is not visually impaired.")
            return "none"
    
    print("Speech recognition failed after all attempts. Assuming visually impaired for accessibility.")
    visually.speak_text("I couldn’t hear you clearly. I’ll assume you’re visually impaired and proceed.", post_delay=0.5)
    return "visually"

@app.route('/')
def index():
    print("Redirecting to /accessibility")
    return redirect('/accessibility')

@app.route('/accessibility', methods=['GET', 'POST'])
def accessibility():
    global stop_voice_prompt
    stop_voice_prompt = False
    
    if request.method == 'POST':
        stop_voice_prompt = True
        user_type = request.form.get('user_type', '').lower()
        print(f"Received user type from form: {user_type}")
        if user_type in ["hearing", "none"]:
            print("Rendering index.html for hearing-impaired or normal user")
            return redirect('/homepage')
        print("Invalid user type, rendering accessibility.html")
        return render_template('accessibility.html')
    
    print("Rendering accessibility.html")
    return render_template('accessibility.html')

@app.route('/start_voice_prompt', methods=['GET'])
def start_voice_prompt():
    global stop_voice_prompt
    if stop_voice_prompt:
        return jsonify({'status': 'interrupted'})
    
    user_type_result = ["none"]
    def run_ask_user_type():
        result = ask_user_type()
        user_type_result[0] = result
    
    voice_thread = threading.Thread(target=run_ask_user_type, daemon=True)
    voice_thread.start()
    
    voice_thread.join()
    
    user_type = user_type_result[0]
    if user_type == "visually":
        print("Redirecting to /visually")
        return jsonify({'redirect': '/visually'})
    elif user_type == "interrupted":
        return jsonify({'status': 'interrupted'})
    
    return jsonify({'status': 'no_redirect'})

@app.route('/set_user_type', methods=['POST'])
def set_user_type():
    global stop_voice_prompt
    stop_voice_prompt = True
    user_type = request.form.get('user_type', '').lower()
    print(f"Received user type from form: {user_type}")
    if user_type in ["hearing", "none"]:
        print("Rendering index.html for hearing-impaired or normal user")
        return redirect('/homepage')
    print("Invalid user type, rendering accessibility.html")
    return redirect('/accessibility')

@app.route('/homepage')
def homepage():
    print("Rendering index.html (homepage)")
    return render_template('index.html')

@app.route('/visually', methods=['GET'])
def visually_impaired():
    global current_course, current_index, topics_content
    print("Entered /visually route, rendering visual.html")
    current_course = None
    current_index = 0
    topics_content = []
    
    voice_thread = threading.Thread(target=voice_navigation, daemon=True)
    voice_thread.start()
    
    initial_content = {"title": "Please select a course", "summary": "Say Python or Java to begin.", "example": ""}
    return render_template('visual.html', courses=visually.course_data, current_course=current_course, current_index=current_index, content=initial_content)

def voice_navigation():
    global current_course, current_index, topics_content
    available_courses = ["Python", "Java"]
    
    course_prompts = [
        "Welcome! To start, please choose a course: Python or Java.",
        "I’m listening, go ahead and choose Python or Java.",
        "Let’s begin. Which course would you like? Python or Java?"
    ]
    retry_course_prompts = [
        "I didn’t hear you clearly. Please choose Python or Java.",
        "Let’s try that again. Say Python or Java, please.",
        "I’m sorry, I didn’t catch that. Which course: Python or Java?"
    ]
    
    visually.speak_text(course_prompts[0], post_delay=0.5)
    
    attempt = 1
    max_course_attempts = 4  # Reduced to prevent runaway
    while attempt <= max_course_attempts:
        time.sleep(6.0)
        course_command = visually.recognize_command("Say Python or Java.", is_course_selection=True).lower()
        print(f"Course selection attempt {attempt}: Recognized course: '{course_command}'")
        words = course_command.split()
        for word in words:
            if word == "python":
                course_command = "Python"
                break
            elif word == "java":
                course_command = "Java"
                break
            else:
                course_command = ""
        
        if course_command in available_courses:
            visually.speak_text(f"Got it, starting the {course_command} course.", post_delay=0.5)
            current_course = course_command
            topics_content = visually.course_data[current_course]
            current_index = 0
            break
        else:
            print("Invalid course detected.")
            retry_prompt = retry_course_prompts[attempt % len(retry_course_prompts)]
            visually.speak_text(retry_prompt, post_delay=0.5)
            attempt += 1
            time.sleep(5.0)
        time.sleep(0.5)
    
    if not current_course:
        visually.speak_text("Couldn’t recognize a course after several tries. Please restart the app.", post_delay=0.5)
        return

    while current_course and current_index < len(topics_content):
        topic = topics_content[current_index]
        content = f"Topic: {topic['title']}. Summary: {topic['summary']}"
        if "example" in topic:
            content += f" Example: {topic['example']}"
        visually.speak_text(content, post_delay=0.5)
        
        navigation_prompts = [
            "What would you like to do next? Say repeat, next, previous, or stop.",
            "I’m listening. You can say repeat, next, previous, or stop.",
            "What’s your next step? Say repeat, next, previous, or stop."
        ]
        retry_navigation_prompts = [
            "I didn’t hear that clearly. Please say repeat, next, previous, or stop.",
            "Let’s try again. Say repeat, next, previous, or stop."
        ]
        
        max_attempts = 3
        attempt = 1
        while attempt <= max_attempts:
            time.sleep(6.0)
            navigation_prompt = navigation_prompts[(current_index + attempt - 1) % len(navigation_prompts)]
            command = visually.recognize_command(navigation_prompt, is_course_selection=False).lower()
            print(f"Navigation attempt {attempt}/{max_attempts}: Recognized command: '{command}'")
            words = command.split()
            for word in words:
                if word in ["repeat", "next", "previous", "stop"]:
                    command = word
                    break
                else:
                    command = ""
            
            if command == "repeat":
                visually.speak_text("Repeating the topic.", post_delay=0.5)
                visually.speak_text(content, post_delay=0.5)
                attempt = 1
            elif command == "next":
                if current_index < len(topics_content) - 1:
                    visually.speak_text("Moving to the next topic.", post_delay=0.5)
                    current_index += 1
                    break
                else:
                    visually.speak_text("You’ve reached the last topic. You can say repeat, previous, or stop.", post_delay=0.5)
                attempt = 1
            elif command == "previous":
                if current_index > 0:
                    visually.speak_text("Going back to the previous topic.", post_delay=0.5)
                    current_index -= 1
                    break
                else:
                    visually.speak_text("You’re at the first topic. You can say repeat, next, or stop.", post_delay=0.5)
                attempt = 1
            elif command == "stop":
                visually.speak_text("Stopping the course. Goodbye.", post_delay=0.5)
                current_course = None
                current_index = 0
                topics_content = []
                return
            else:
                retry_prompt = retry_navigation_prompts[attempt - 1]
                visually.speak_text(retry_prompt, post_delay=0.5)
                attempt += 1
                if attempt > max_attempts:
                    visually.speak_text("I couldn’t understand after a few tries. Let’s try again.", post_delay=0.5)
                time.sleep(5.0)
            time.sleep(0.5)
    if current_course:
        visually.speak_text("You’ve completed all topics. Goodbye.", post_delay=0.5)
        current_course = None
        current_index = 0
        topics_content = []

@app.route('/api/state', methods=['GET'])
def get_state():
    global current_course, current_index, topics_content
    content = topics_content[current_index] if current_course and topics_content and current_index < len(topics_content) else None
    return jsonify({
        'course': current_course,
        'index': current_index,
        'total': len(topics_content),
        'content': content if content else {"title": "No content", "summary": "Please navigate using voice.", "example": ""}
    })

@app.route('/api/navigate', methods=['POST'])
def navigate():
    global current_course, current_index, topics_content
    command = request.json.get('command', '').lower()
    
    if not current_course or not topics_content:
        return jsonify({'error': 'No course selected'})

    if command == "repeat":
        topic = topics_content[current_index]
    elif command == "next":
        if current_index < len(topics_content) - 1:
            current_index += 1
    elif command == "previous":
        if current_index > 0:
            current_index -= 1
    elif command == "stop":
        current_course = None
        current_index = 0
        topics_content = []
        return jsonify({'command': 'stop'})
    
    topic = topics_content[current_index]
    return jsonify({
        'course': current_course,
        'index': current_index,
        'total': len(topics_content),
        'content': {"title": topic["title"], "summary": topic["summary"] or "No summary available", "example": topic.get("example", "")}
    })

@app.route('/api/course/<course_name>')
def get_course_content(course_name):
    if course_name in visually.course_data:
        return jsonify(visually.course_data[course_name])
    elif course_name in hearing.course_data:
        return jsonify(hearing.course_data[course_name])
    return jsonify({"error": "Course not found"}), 404

@app.route('/hearing')
def hearing_impaired():
    courses = {
        "Learn Sign Language": hearing.course_data["Learn Sign Language"],
        "Indian sign language with Tamil words": hearing.course_data["Indian sign language with Tamil words"],
        "English Grammar": hearing.course_data["English Grammar"]
    }
    return render_template('hearing.html', courses=courses)

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)