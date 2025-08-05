import speech_recognition as sr
import pyttsx3
import time
import json
import os
import queue
import threading
try:
    from AppKit import NSSpeechSynthesizer  # macOS native TTS
    use_nsspeech = True
except ImportError:
    use_nsspeech = False
    print("NSSpeechSynthesizer not available, falling back to pyttsx3")

# Load course data
with open("/Users/prasannas/Desktop/vs/project R/visual.json", "r") as f:
    course_data = json.load(f)
print("Course data loaded successfully from /Users/prasannas/Desktop/vs/project R/visual.json")

# Initialize speech recognition
recognizer = sr.Recognizer()
# Speech queue for thread-safe TTS
speech_queue = queue.Queue()
speech_thread = None

def init_tts():
    """
    Initialize a thread to handle speech synthesis using NSSpeechSynthesizer or pyttsx3.
    """
    global speech_thread
    def speech_worker():
        if use_nsspeech:
            synthesizer = NSSpeechSynthesizer.alloc().init()
            synthesizer.setRate_(180)  # Normal speed (180 wpm)
            synthesizer.setVolume_(1.0)  # Max volume
        else:
            synthesizer = pyttsx3.init()
            synthesizer.setProperty('rate', 140)  # Slower for clarity
            synthesizer.setProperty('volume', 1.0)  # Max volume
        
        while True:
            try:
                text, post_delay = speech_queue.get()
                if text is None:
                    break
                print(f"Speaking: '{text}'")
                start_time = time.time()
                if use_nsspeech:
                    synthesizer.startSpeakingString_(text)
                    while synthesizer.isSpeaking():
                        time.sleep(0.1)
                else:
                    synthesizer.say(text)
                    synthesizer.runAndWait()
                end_time = time.time()
                print(f"Audio playback took {end_time - start_time:.2f} seconds")
                time.sleep(post_delay)
                speech_queue.task_done()
            except Exception as e:
                print(f"Error in speech_worker: {str(e)}")
    
    speech_thread = threading.Thread(target=speech_worker, daemon=True)
    speech_thread.start()
    print(f"Text-to-speech engine initialized ({'NSSpeechSynthesizer' if use_nsspeech else 'pyttsx3'})")

init_tts()

def speak_text(text, post_delay=0.5):
    """
    Add text to the speech queue for thread-safe playback.
    """
    try:
        speech_queue.put((text, post_delay))
        # Wait briefly to ensure queue processing starts
        time.sleep(0.1)
    except Exception as e:
        print(f"Error in speak_text: {str(e)}")

def recognize_command(prompt, is_course_selection=False):
    """
    Recognize voice commands with improved reliability and debugging.
    """
    with sr.Microphone() as source:
        # Extended ambient noise calibration
        print("Calibrating microphone... Please remain silent for 5 seconds.")
        speak_text("Calibrating microphone. Please remain silent for five seconds.", post_delay=0.5)
        time.sleep(3.0)  # Wait for calibration prompt to finish
        recognizer.adjust_for_ambient_noise(source, duration=5.0)
        recognizer.energy_threshold = 4  # Balanced sensitivity
        recognizer.dynamic_energy_threshold = True
        
        phrase_limit = 7  # Extended for all commands
        max_attempts = 3
        attempt = 1
        
        while attempt <= max_attempts:
            try:
                speak_text(prompt, post_delay=0.5)
                print(f"Listening for: '{prompt}' (Attempt {attempt}/{max_attempts})")
                time.sleep(3.0)  # Ensure prompt is fully spoken
                speak_text("Microphone is active. Please speak now.", post_delay=0.5)
                time.sleep(1.0)  # Wait for mic prompt
                start_time = time.time()
                audio = recognizer.listen(source, timeout=20, phrase_time_limit=phrase_limit)
                end_time = time.time()
                print(f"Microphone listen took {end_time - start_time:.2f} seconds")
                
                # Save audio for debugging
                debug_file = f"debug_audio_{int(time.time())}.wav"
                with open(debug_file, "wb") as f:
                    f.write(audio.get_wav_data())
                print(f"Saved audio to {debug_file} for debugging")
                audio_duration = (end_time - start_time)
                print(f"Audio duration: {audio_duration:.2f} seconds")
                
                # Log energy level for debugging
                try:
                    energy = recognizer.energy_threshold
                    print(f"Current energy threshold: {energy}")
                except:
                    print("Could not retrieve energy threshold")
                
                # Recognize speech
                print("Sending audio to Google Speech Recognition API...")
                command = recognizer.recognize_google(audio, show_all=True)
                
                if isinstance(command, list):
                    if not command:
                        print("Recognition failed: No results returned")
                        raise sr.UnknownValueError("No results returned")
                    best_result = command[0]
                    recognized_text = best_result.get('transcript', '')
                    confidence = best_result.get('confidence', 0.0)
                    print(f"Recognized: '{recognized_text}' (Confidence: {confidence:.2f})")
                    return recognized_text
                else:
                    print(f"Recognized: '{command}'")
                    return command
            
            except sr.UnknownValueError as e:
                print(f"Recognition failed: Could not understand audio. Error: {str(e)}")
                speak_text("I didn’t hear you clearly. Please speak louder and try again.", post_delay=0.5)
                attempt += 1
            except sr.RequestError as e:
                print(f"Speech recognition request failed: {str(e)}")
                speak_text("I’m having trouble with the speech service. Please check your internet and try again.", post_delay=0.5)
                attempt += 1
                time.sleep(attempt * 5)
            except Exception as e:
                print(f"Unexpected error in recognize_command: {str(e)}")
                speak_text("An error occurred. Please try again.", post_delay=0.5)
                attempt += 1
            
            if attempt > max_attempts:
                print(f"Max attempts ({max_attempts}) reached. Recognition failed.")
                speak_text("I couldn’t understand after several tries. Please restart the app.", post_delay=0.5)
                break
        
        return ""