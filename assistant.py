import streamlit as st
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import os
import random
import pyautogui
import pyjokes
import pyttsx3
import threading
import requests
import pyaudio

# API Key for OpenWeatherMap
API_KEY = "4d2a1e33954136ca5018f6bf7f526ad9"

# Configure Streamlit page
st.set_page_config(page_title="AI Voice Assistant", page_icon="🤖", layout="centered")

# Animation CSS
st.markdown("""
    <style>
        @keyframes pop-up {
            0% { opacity: 0; transform: scale(0.5); }
            50% { opacity: 0.5; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
    </style>
""", unsafe_allow_html=True)

# Text-to-speech function
def speak(text):
    def run():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run).start()

# Greeting on first load
if 'greeted' not in st.session_state:
    st.markdown('<h3 style="animation: pop-up 2s forwards;">Hello Sir! How can I assist you today?</h3>', unsafe_allow_html=True)
    speak("Hello Sir! How can I assist you today?")
    st.session_state.greeted = True

# Get weather info
def get_weather(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            weather_info = f"The weather in {location} is {description} with a temperature of {temp}°C."
            speak(weather_info)
            st.info(weather_info)
        else:
            speak("City not found. Please try again.")
            st.error("City not found.")
    except Exception as e:
        speak("Unable to fetch weather information.")
        st.error(f"Error: {str(e)}")

# Get time
def get_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {current_time}")
    st.info(f"The current time is {current_time}")

# Get date
def get_date():
    today = datetime.datetime.now()
    date_str = f"{today.day} {today.strftime('%B')} {today.year}"
    speak(f"Today's date is {date_str}")
    st.info(f"Today's date is {date_str}")

# Take screenshot
def take_screenshot():
    folder = r"C:\Users\hardi\OneDrive\Pictures\Screenshots"
    os.makedirs(folder, exist_ok=True)
    i = 1
    while True:
        img_path = os.path.join(folder, f"screenshot_{i}.png")
        if not os.path.exists(img_path):
            break
        i += 1
    try:
        img = pyautogui.screenshot()
        img.save(img_path)
        speak(f"Screenshot saved as screenshot_{i}.png")
        st.success(f"Screenshot saved as screenshot_{i}.png")
    except Exception as e:
        speak("Error taking screenshot.")
        st.error(f"Error: {str(e)}")

# Tell a joke
def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)
    st.info(joke)

# Play random music
def play_random_music():
    queries = ["lofi music", "pop hits", "rock songs", "jazz music"]
    query = random.choice(queries)
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    speak(f"Playing {query} on YouTube")
    wb.open(search_url)

# Wikipedia search
def search_wikipedia(query):
    try:
        result = wikipedia.summary(query, sentences=2)
        page_url = wikipedia.page(query).url
        wb.open(page_url)
        speak(result)
        st.success(result)
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options[:5]
        speak("Multiple results found. Here are a few options.")
        st.warning("Multiple results found. Please be more specific.")
        for option in options:
            st.write(option)
    except wikipedia.exceptions.PageError:
        speak("No page found for that topic.")
        st.error("No Wikipedia page found.")
    except Exception as e:
        speak("An error occurred while searching.")
        st.error(f"Error: {str(e)}")

# Take voice command
def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio, language="en-in").lower()
            st.success(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            speak("Listening timed out.")
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
        except sr.RequestError:
            speak("No internet connection.")
    return None

# UI Components
st.title("AI Voice Assistant")
col1, col2 = st.columns(2)

with col1:
    if st.button("🕒 Tell Time"):
        get_time()

    if st.button("📅 Tell Date"):
        get_date()

    if st.button("📸 Take Screenshot"):
        take_screenshot()

with col2:
    if st.button("🤣 Tell a Joke"):
        tell_joke()

    if st.button("🎵 Play Random Music"):
        play_random_music()

# Wikipedia text input
wiki_query = st.text_input("🔍 Search Wikipedia:")
if st.button("Search") and wiki_query:
    search_wikipedia(wiki_query)

# Voice command processing
if st.button("🎤 Voice Command"):
    command = take_command()
    if command:
        if "open google" in command:
            speak("Opening Google")
            wb.open("https://www.google.com")

        elif "open youtube" in command:
            speak("Opening YouTube")
            wb.open("https://www.youtube.com")
        
        elif "open wikipedia" in command:
            speak("Opening Wikipedia")
            wb.open("https://www.wikipedia.org/")
            

        elif "time" in command:
            get_time()

        elif "date" in command:
            get_date()

        elif "screenshot" in command:
            take_screenshot()

        elif "joke" in command:
            tell_joke()

        elif "play music" in command:
            play_random_music()

        elif "weather of" in command:
            location = command.split("weather of", 1)[1].strip()
            if location:
                get_weather(location)
            else:
                speak("Please specify a location.")

        elif "search for" in command and ("on wikipedia" in command or "in wikipedia" in command):
            if "on wikipedia" in command:
                query = command.split("search for", 1)[1].split("on wikipedia")[0].strip()
            elif "in wikipedia" in command:
                query = command.split("search for", 1)[1].split("in wikipedia")[0].strip()
            else:
                query = ""
            if query:
                search_wikipedia(query)
            else:
                speak("Please specify a topic.")

        elif "exit" in command or "offline" in command:
            speak("Going offline. Goodbye!")
            st.stop()

        else:
            speak("Command not recognized. Please try again.")
