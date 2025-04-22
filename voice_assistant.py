from volume_controller import VolumeController
from command_executor import CommandExecutor
import speech_recognition as sr
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
import ollama
import pyttsx3
import re
class VoiceAssistant:
    def __init__(self, volume_controller: VolumeController, command_executor: CommandExecutor):
        self.recognizer = sr.Recognizer()
        self.volume_controller = volume_controller
        self.executor = command_executor
        self.wake_word = "maya"
        self.is_active = False
        self.last_command_time = time.time()
        self.sleep_timeout = 300  # 5 minutes timeout before going back to sleep
        self.gif_root = None
        self.gif_thread = None
        self.gif_active = False
        self.conversation_history = []  
        self.max_history = 1  
        self.alarms = []  
        self.reminders = []  
        self.last_joke = None  
        
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 1.0)
        except Exception as e:
            print(f"Error initializing pyttsx3 engine: {e}")
            self.engine = None

    def get_gemma_response(self, prompt):
        """Get response from Gemma model through Ollama"""
        if prompt.strip().lower() in ["what is your name", "who are you"]:
            return "My name is Maya, and I was created and developed by the VoxFusion team."

        try:
            # Instruction for concise answers
            instruction = "Provide a concise and clear answer in 2-3 sentences."
            
            # If prompt is to get another joke, add context to avoid repetition
            if prompt.strip().lower() in ['another', 'another joke', 'tell me another joke']:
                if self.last_joke:
                    prompt = f"Tell me a new joke different from this one: {self.last_joke}"
                else:
                    prompt = "Tell me a joke"
            
            full_prompt = f"{instruction}\nUser: {prompt}\nAssistant:"
            
            response = ollama.generate(
                model='gemma:2b',
                prompt=full_prompt,
                options={'temperature': 0.5, 'max_tokens': 100}  # Reduced temperature and limited tokens for faster, shorter responses
            )
            
            # Clean up the response
            reply = response['response'].strip()
            reply = reply.split("User:")[0].strip()  # Remove any accidental continuation
            
            # Remove unwanted '*' characters from reply
            reply = reply.replace('*', '')
            
            # Truncate reply to 2 or 3 sentences
            sentences = re.split(r'(?<=[.!?]) +', reply)
            if len(sentences) > 3:
                reply = ' '.join(sentences[:3])
            
            # Update conversation history
            self.conversation_history.append({
                'user': prompt,
                'assistant': reply
            })

            # Update last joke if the prompt was a joke request
            if any(kw in prompt.lower() for kw in ['joke', 'another joke', 'new joke']):
                self.last_joke = reply
            
            return reply
        except Exception as e:
            print(f"Error getting Gemma response: {e}")
            return "I'm sorry, I couldn't process that right now."

    def show_gif(self):
        if self.gif_root is not None:
            try:
                self.gif_root.deiconify()
                self.gif_active = True
                return
            except:
                self.gif_root = None

        def run_gif():
            self.gif_root = tk.Tk()
            self.gif_root.overrideredirect(True)
            self.gif_root.wm_attributes("-topmost", True)
            self.gif_root.wm_attributes("-transparentcolor", "white")
            self.gif_root.config(bg='white')

            screen_width = self.gif_root.winfo_screenwidth()
            screen_height = self.gif_root.winfo_screenheight()

            gif = Image.open("voice.gif")
            frames = []
            try:
                while True:
                    frames.append(ImageTk.PhotoImage(gif.copy()))
                    gif.seek(len(frames))
            except EOFError:
                pass

            self.label = tk.Label(self.gif_root, bg='white')
            self.label.pack()

            x = (screen_width - gif.width) // 2
            y = screen_height - gif.height - 50
            self.gif_root.geometry(f"{gif.width}x{gif.height}+{x}+{y}")

            def update(index=0):
                if not hasattr(self, 'gif_root') or not self.gif_root.winfo_exists():
                    return
                if not self.gif_active:
                    return
                self.label.config(image=frames[index])
                self.gif_root.after(100, update, (index + 1) % len(frames))

            self.gif_active = True
            update()
            self.gif_root.mainloop()

        self.gif_thread = threading.Thread(target=run_gif, daemon=True)
        self.gif_thread.start()

    def hide_gif(self):
        self.gif_active = False
        if self.gif_root is not None and self.gif_root.winfo_exists():
            try:
                self.gif_root.withdraw()
            except:
                pass

    def speak(self, text):
        if self.engine:
            print(f"Assistant: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print(f"Assistant (No TTS Engine): {text}")

    def listen(self):
        """Continuous listening with silent operation when not active"""
        with sr.Microphone() as source:
            print("Listening... (silent mode)")
            while True:
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                    
                    try:
                        command = self.recognizer.recognize_google(audio).lower()
                        print(f"You said: {command}")
                        return command
                    except sr.UnknownValueError:
                        return None
                    except sr.RequestError:
                        try:
                            command = self.recognizer.recognize_sphinx(audio).lower()
                            print(f"You said (offline): {command}")
                            return command
                        except sr.UnknownValueError:
                            return None

                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Listening error: {e}")
                    return None

    def set_alarm(self, alarm_time_str: str):
        """
        Set an alarm for the specified time string in format HH:MM (24-hour or 12-hour with am/pm).
        """
        try:
            alarm_time = self.parse_time(alarm_time_str)
            now = time.localtime()
            alarm_seconds = alarm_time.tm_hour * 3600 + alarm_time.tm_min * 60
            now_seconds = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
            delay = alarm_seconds - now_seconds
            if delay < 0:
                delay += 24 * 3600  # Alarm for next day

            if delay < 1:
                self.speak("The specified time is in the past or too close. Please specify a future time.")
                return

            timer = threading.Timer(delay, self.alarm_triggered)
            timer.daemon = True
            timer.start()
            self.alarms.append(timer)
            self.speak(f"Alarm set for {alarm_time_str}")
        except Exception as e:
            self.speak(f"Sorry, I couldn't set the alarm for {alarm_time_str}")

    def alarm_triggered(self):
        self.speak("Alarm ringing!")

    def set_reminder(self, reminder_text: str, reminder_time_str: str):
        """
        Set a reminder with text and time string.
        """
        try:
            reminder_time = self.parse_time(reminder_time_str)
            now = time.localtime()
            reminder_seconds = reminder_time.tm_hour * 3600 + reminder_time.tm_min * 60
            now_seconds = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
            delay = reminder_seconds - now_seconds
            if delay < 0:
                delay += 24 * 3600  # Reminder for next day

            if delay < 1:
                self.speak("The specified time is in the past or too close. Please specify a future time.")
                return

            timer = threading.Timer(delay, self.reminder_triggered, args=(reminder_text,))
            timer.daemon = True
            timer.start()
            self.reminders.append(timer)
            self.speak(f"Reminder set for {reminder_time_str}: {reminder_text}")
        except Exception as e:
            self.speak(f"Sorry, I couldn't set the reminder for {reminder_time_str}")

    def reminder_triggered(self, reminder_text: str):
        self.speak(f"Reminder: {reminder_text}")

    def parse_time(self, time_str: str):
        """
        Parse time string in formats like '7:30 am', '19:45', '7 pm' into time.struct_time with today's date.
        """
        from datetime import datetime, timedelta
        import re

        now = datetime.now()
        time_str_clean = time_str.strip().lower()
        # Remove dots in am/pm if present (e.g., "5:00 p.m." -> "5:00 pm")
        time_str_clean = re.sub(r'\.(?=[ap]m)', '', time_str_clean)

        try:
            # Try 12-hour format with am/pm
            dt = datetime.strptime(time_str_clean, '%I:%M %p')
        except ValueError:
            try:
                # Try 12-hour format without minutes
                dt = datetime.strptime(time_str_clean, '%I %p')
            except ValueError:
                try:
                    # Try 24-hour format
                    dt = datetime.strptime(time_str_clean, '%H:%M')
                except ValueError:
                    # If all fail, raise error
                    raise ValueError(f"Invalid time format: {time_str}")

        # If the parsed time is earlier than now, assume it's for the next day
        parsed_time = now.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)
        if parsed_time <= now:
            parsed_time += timedelta(days=1)

        return parsed_time.timetuple()

    def run(self):
        self.speak(f"Voice Assistant activated. Say '{self.wake_word}' to wake me up.")
        while True:
            try:
                command = self.listen()

                if not command:
                    if self.is_active and time.time() - self.last_command_time > self.sleep_timeout:
                        self.is_active = False
                        self.hide_gif()
                        self.speak("Going back to sleep. Say 'alexa' to wake me up.")
                        self.conversation_history = []
                    continue

                if not self.is_active and self.wake_word in command:
                    self.is_active = True
                    self.last_command_time = time.time()
                    self.show_gif()
                    self.speak("Yes, how can I help you?")
                    continue

                if self.is_active:
                    if command.lower() in ['exit', 'quit', 'bye', 'stop', 'go to sleep']:
                        self.speak("Goodbye!")
                        self.is_active = False
                        self.hide_gif()
                        self.conversation_history = []
                        continue

                    self.last_command_time = time.time()
                    
                    if command.strip().lower() not in ['another', 'another joke', 'tell me another joke']:
                        self.last_joke = None
                    
                    # First try to execute as a command
                    command_executed = self.executor.try_execute_command(command, self)
                    
                    # If not a command, use Gemma for conversational response
                    if not command_executed:
                        response = self.get_gemma_response(command)
                        self.speak(response)

            except KeyboardInterrupt:
                self.speak("Goodbye!")
                self.hide_gif()
                if self.gif_root is not None:
                    self.gif_root.destroy()
                break
            except Exception as e:
                print(f"Error: {e}")
                continue
    pass