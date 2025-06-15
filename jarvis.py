import tkinter as tk
import threading
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import pyjokes
import os
import psutil
import pyautogui
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
import cv2
from PIL import Image
from PyPDF2 import PdfReader
import requests
import wikipedia
import shutil

# Initialize GUI root early so it's available everywhere
root = tk.Tk()
root.title("Jarvis AI")
root.geometry("650x450")
root.configure(bg="#1a1a1a")

# Global flags
stop_speaking = threading.Event()
stop_listening = threading.Event()

# Text-to-speech setup
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("voice", engine.getProperty('voices')[0].id)

# Speak function
def speak(text):
    def run():
        stop_speaking.clear()
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

# Stop speaking
def stop_speaking_now():
    stop_speaking.set()
    stop_listening.set()
    engine.stop()
    speak("Jarvis has stopped listening.")
    response_box.insert("end", "🔴 Jarvis is Paused\n\n")
    response_box.see("end")
    root.configure(bg="#4d0000")  # red background to indicate pause

# resume listening
def resume_listening():
    stop_listening.clear()
    speak("Resuming listening.")
    response_box.insert("end", "🟢 Jarvis is Resumed\n\n")
    response_box.see("end")
    root.configure(bg="#1a1a1a")  # restore original background

# voice command Recognition
def take_command():
    if stop_listening.is_set():
        return ""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            return ""

    if stop_listening.is_set():
        return ""

    try:
        print("🧠 Recognizing...")
        query = r.recognize_google(audio)
        print("You said:", query)
        return query.lower()
    except sr.UnknownValueError:
        speak("I didn't catch that.")
    except sr.RequestError:
        speak("Check your internet connection.")
    return ""

 # weather function
def get_weather(city="Hoshiarpur"):
    api_key = os.getenv("WEATHER_API_KEY", "edeb312f1328a7f3d633a8191481dee4")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") == 200:
            main = res["main"]
            weather_desc = res["weather"][0]["description"]
            temp = main["temp"]
            humidity = main["humidity"]
            wind = res["wind"]["speed"]
            return f"{city} weather: {weather_desc}, {temp}°C, humidity {humidity}%, wind {wind} m/s"
        return f"Couldn't get weather for {city}."
    except Exception as e:
        return f"Weather service error: {str(e)}"
    
# wikipedia function    
def search_wikipedia(topic):
    try:
        return wikipedia.summary(topic, sentences=2)
    except:
        return "Couldn't find anything on Wikipedia."

# joke function
def tell_joke():
    return pyjokes.get_joke()

# remember note function
def remember_note(note):
    os.makedirs("notes", exist_ok=True)
    with open("notes/data.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: {note}\n")
    return f"Noted: {note}"

# read notes function
def read_notes():
    try:
        with open("notes/data.txt", "r") as f:
            return f.read()
    except:
        return "No notes yet."

# battery function
def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        plugged = "Plugged in" if battery.power_plugged else "Not plugged"
        return f"Battery at {battery.percent}%, {plugged}"
    return "Battery info not available"

# screenshot function
def take_screenshot():
    folder = "Screenshots"
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(folder, f"screenshot_{timestamp}.png")
    pyautogui.screenshot().save(file_path)
    return f"Screenshot saved"

# open application function
def open_application(name):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe", 
        "paint": "mspaint.exe",
        "chrome": "chrome.exe",
        "word": "winword.exe"
    }
    try:
        os.startfile(apps.get(name.lower(), name))
        return f"Opening {name}"
    except:
        return f"Couldn't open {name}"

# path function
def normalize_path(raw_path):
    replacements = {
        "colon": ":",
        "backslash": "\\",
        "slash": "/",
        "dot": ".",
        "space": " "
    }
    for k, v in replacements.items():
        raw_path = raw_path.replace(k, v)
    return os.path.normpath(raw_path)

# image text function
def read_image_text(path="C:/jarvisfiles/image.png"):
    try:
        return pytesseract.image_to_string(Image.open(normalize_path(path)))
    except Exception as e:
        return f"Image error: {str(e)}"
    

# read pdf function
def read_pdf_text(path="C:/jarvisfiles/Resume_Shivam_Jerath.pdf"):
    try:
        reader = PdfReader(normalize_path(path))
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        return f"PDF error: {str(e)}"


# Command processing and functionality
def process_command(response_box):
    query = take_command()
    if not query:
        return

    response = ""
    query = query.lower()

    if "your name" in query:
        response = "My name is Jarvis."
    elif "old are you" in query:
        response = "I was created recently."
    elif "time" in query:
        response = datetime.datetime.now().strftime("%I:%M %p")
    elif "date" in query:
        response = datetime.datetime.now().strftime("%B %d, %Y")
    elif "weather" in query:
        speak("Which city should I check?")
        city = take_command()
        response = get_weather(city) if city else "No city specified"
    elif "wikipedia" in query:
        speak("What should I search?")
        topic = take_command()
        response = search_wikipedia(topic) if topic else "No topic specified"
    elif "joke" in query:
        response = tell_joke()
    elif "remember" in query:
        speak("What should I remember?")
        note = take_command()
        response = remember_note(note) if note else "Nothing to remember"
    elif "do you know" in query:
        response = read_notes()
    elif "battery" in query:
        response = battery_status()
    elif "screenshot" in query:
        response = take_screenshot()
    elif any(cmd in query for cmd in ["open", "launch"]):
        app = query.replace("open", "").replace("launch", "").strip()
        if "youtube" in query:
            webbrowser.open("https://youtube.com")
            response = "Opening YouTube"
        elif any(site in query for site in ["facebook", "google", "gmail"]):
            sites = {
                "facebook": "https://facebook.com",
                "google": "https://google.com",
                "gmail": "https://mail.google.com"
            }
            site = next((s for s in sites if s in query), "google")
            webbrowser.open(sites[site])
            response = f"Opening {site.capitalize()}"
        else:
            response = open_application(app)
    elif "read image" in query:
        response = read_image_text()
    elif "read pdf" in query:
        response = read_pdf_text()
    elif any(cmd in query for cmd in ["exit", "stop", "goodbye"]):
        speak("Goodbye!")
        root.after(1000, root.destroy)
        return
    else:
        response = "I'm not sure how to help with that."

    response_box.insert("end", f"You: {query}\nJarvis: {response}\n\n")
    response_box.see("end")
    speak(response)

 # running jarvis
def run_jarvis():
    response_box.insert("end", "🟢 Jarvis Activated...\n\n")
    response_box.see("end")
    while True:
        if not stop_listening.is_set():
            process_command(response_box)

# start jarvis
def start_jarvis():
    threading.Thread(target=run_jarvis, daemon=True).start()

# GUI Setup
title = tk.Label(root, text="Jarvis - Your AI Assistant", 
                font=("Helvetica", 20, "bold"), fg="cyan", bg="#1a1a1a")
title.pack(pady=10)

btn_frame = tk.Frame(root, bg="#1a1a1a")
btn_frame.pack(pady=10)

activate_btn = tk.Button(btn_frame, text="🎙️ Activate Jarvis", 
                        command=start_jarvis, font=("Helvetica", 14),
                        bg="green", fg="white")
activate_btn.pack(side="left", padx=10)

stop_btn = tk.Button(btn_frame, text="🔇 Stop Speaking", 
                    command=stop_speaking_now, font=("Helvetica", 12),
                    bg="red", fg="white")
stop_btn.pack(side="left", padx=10)

resume_btn = tk.Button(btn_frame, text="▶️ Resume Listening", 
                    command=resume_listening, font=("Helvetica", 12),
                    bg="blue", fg="white")
resume_btn.pack(side="left", padx=10)

response_box = tk.Text(root, font=("Consolas", 12), 
                      bg="#262626", fg="white", wrap="word")
response_box.pack(expand=True, fill="both", padx=10, pady=10)

scrollbar = tk.Scrollbar(response_box)
scrollbar.pack(side="right", fill="y")
response_box.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=response_box.yview)

root.mainloop()