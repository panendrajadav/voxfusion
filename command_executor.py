import os
import re
import subprocess
import webbrowser
import pygetwindow as gw
import pyautogui
import time
import urllib.parse
from typing import Dict, Any, TYPE_CHECKING
import ollama
import tkinter as tk
import psutil

if TYPE_CHECKING:
    from voice_assistant import VoiceAssistant

class CommandExecutor:
    # ...existing code from CommandExecutor class...
    def __init__(self):
        self.applications = {
            'notepad': {'command': 'notepad.exe', 'window_title': 'Notepad'},
            'calculator': {'command': 'calc.exe', 'window_title': 'Calculator'},
            'cmd': {'command': 'cmd.exe', 'window_title': 'Command Prompt'},
            'chrome': {'command': r'C:\Program Files\Google\Chrome\Application\chrome.exe', 'window_title': 'Google Chrome'},
            'edge': {'command': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', 'window_title': 'Microsoft Edge'},
            'paint': {'command': 'mspaint.exe', 'window_title': 'Paint'},
            'file explorer': {'command': 'explorer.exe', 'window_title': 'File Explorer'},
            'explorer': {'command': 'explorer.exe', 'window_title': 'File Explorer'},
            'control panel': {'command': 'control.exe', 'window_title': 'Control Panel'},
            'settings': {'command': 'ms-settings:', 'window_title': 'Settings'},
            'vs code': {'command': r'C:\Users\panen\AppData\Local\Programs\Microsoft VS Code\Code.exe', 'window_title': 'Visual Studio Code'},
            'vs': {'command': r'C:\Users\panen\AppData\Local\Programs\Microsoft VS Code\Code.exe', 'window_title': 'Visual Studio Code'},
            'excel': {'command': r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE', 'window_title': 'Microsoft Excel'},
            'word': {'command': r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE', 'window_title': 'Microsoft Word'},    
            'ppt': {'command':  r'C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE', 'window_title': 'Microsoft PowerPoint', 'alternative_command': 'start powerpnt'},
            'mail': {'command': r'C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE', 'window_title': 'Outlook', 'alternative_command': 'start outlook'}
        }

        self.websites = {
            'chatgpt': 'https://chat.openai.com',
            'kaggle': 'https://www.kaggle.com',
            'leetcode': 'https://leetcode.com',
            'youtube': 'https://youtube.com',
            'github': 'https://github.com',
            'google': 'https://google.com',
            'linkedin': 'https://linkedin.com',
            'facebook': 'https://facebook.com',
            'twitter': 'https://twitter.com',
            'instagram': 'https://instagram.com',
            'netflix': 'https://netflix.com',
            'amazon': 'https://amazon.com',
            'reddit': 'https://reddit.com',
            'wikipedia': 'https://wikipedia.org',
            'gmail': 'https://mail.google.com',
            'whatsapp': 'https://web.whatsapp.com',
            'discord': 'https://discord.com',
            'spotify': 'https://spotify.com',
            'insta': 'https://instagram.com',
        }

        self.special_folders = {
            'documents': os.path.expanduser('~/Documents'),
            'downloads': os.path.expanduser('~/Downloads'),
            'desktop': os.path.expanduser('~/Desktop'),
            'pictures': os.path.expanduser('~/Pictures'),
            'music': os.path.expanduser('~/Music'),
            'videos': os.path.expanduser('~/Videos'),
            'd drive': 'D:\\',
            'c drive': 'C:\\'
        }

    def try_execute_command(self, command: str, assistant: "VoiceAssistant") -> bool:
        """
        Try to execute the command, return True if it was a recognized command,
        False if it should be handled as a conversation
        """
        command_lower = command.lower()
        
        # Check for basic commands that shouldn't trigger conversation
        basic_commands = [
            'increase volume', 'volume up', 'decrease volume', 'volume down',
            'mute', 'unmute', 'volume level', 'battery', 'power', 'shutdown',
            'restart', 'reboot', 'sleep', 'lock'
        ]
        
        if any(cmd in command_lower for cmd in basic_commands):
            self.execute_command(command, assistant)
            return True
            
        # New feature: detect "write a program on" command
        write_program_match = re.match(r'write a program on (.+)', command_lower)
        if write_program_match:
            topic = write_program_match.group(1).strip()
            self.open_code_development_window(topic, assistant)
            return True
            
        # Check for alarm and reminder commands
        alarm_match = re.match(r'set alarm for (.+)', command_lower)
        if alarm_match:
            alarm_time = alarm_match.group(1).strip()
            assistant.set_alarm(alarm_time)
            return True
        
        reminder_match = re.match(r'remind me to (.+) at (.+)', command_lower)
        if reminder_match:
            reminder_text = reminder_match.group(1).strip()
            reminder_time = reminder_match.group(2).strip()
            assistant.set_reminder(reminder_text, reminder_time)
            return True
        
        # Check for more complex commands
        understood = self.understand_command(command)
        print(f"Understood: {understood}")

        intent = understood.get('intent', '').lower()
        target = understood.get('target', '')
        query = understood.get('query', '')
        problem_num = understood.get('problem_num', '')

        if intent in ['open', 'close', 'search', 'youtube_search', 'leetcode_problem']:
            self.execute_command(command, assistant)
            return True
        
        return False

    def execute_command(self, command: str, assistant: "VoiceAssistant"):
        command_lower = command.lower()
        
        # Volume control commands
        if 'increase volume' in command_lower or 'volume up' in command_lower:
            new_volume = assistant.volume_controller.increase_volume()
            assistant.speak(f"Volume increased to {int(new_volume * 100)} percent")
            return
        elif 'decrease volume' in command_lower or 'volume down' in command_lower:
            new_volume = assistant.volume_controller.decrease_volume()
            assistant.speak(f"Volume decreased to {int(new_volume * 100)} percent")
            return
        elif 'mute' in command_lower:
            assistant.volume_controller.mute()
            assistant.speak("Volume muted")
            return
        elif 'unmute' in command_lower:
            assistant.volume_controller.unmute()
            assistant.speak("Volume unmuted")
            return
        elif 'volume' in command_lower and 'level' in command_lower:
            current_volume = assistant.volume_controller.get_volume()
            assistant.speak(f"Current volume is at {int(current_volume * 100)} percent")
            return
        
        # Battery status
        elif 'battery' in command_lower or 'power' in command_lower:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                status = "plugged in" if battery.power_plugged else "not plugged in"
                assistant.speak(f"Battery is at {percent} percent and {status}")
            else:
                assistant.speak("Could not check battery status")
            return
        
        # System commands
        elif 'shutdown' in command_lower:
            assistant.speak("Shutting down the computer")
            os.system("shutdown /s /t 1")
            return
        elif 'restart' in command_lower or 'reboot' in command_lower:
            assistant.speak("Restarting the computer")
            os.system("shutdown /r /t 1")
            return
        elif 'sleep' in command_lower:
            assistant.speak("Putting the computer to sleep")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return
        elif 'lock' in command_lower:
            assistant.speak("Locking the computer")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return
        
        # Application and website commands
        understood = self.understand_command(command)
        print(f"Understood: {understood}")

        intent = understood.get('intent', '').lower()
        target = understood.get('target', '')
        query = understood.get('query', '')
        problem_num = understood.get('problem_num', '')

        try:
            if intent == 'open':
                self.open_target(target, assistant)
            elif intent == 'close':
                self.close_target(target, assistant)
            elif intent == 'search':
                self.search_target(query, assistant)
            elif intent == 'youtube_search':
                self.youtube_search(query, assistant)
            elif intent == 'leetcode_problem':
                self.open_leetcode_problem(problem_num, assistant)
        except Exception as e:
            print(f"Error executing command: {e}")
            if assistant.is_active:
                assistant.speak("Sorry, I couldn't execute that command.")

    def understand_command(self, command: str) -> Dict[str, Any]:
        command_lower = command.lower()

        leetcode_match = re.match(
            r'(?:leetcode|leet code|lead code) problem (?:number )?(\d+)',
            command_lower
        )
        if leetcode_match:
            return {
                'intent': 'leetcode_problem',
                'problem_num': leetcode_match.group(1)
            }

        youtube_search_match = re.match(
            r'(?:search|find) (.+?) (?:in|on) youtube', 
            command_lower
        )
        if youtube_search_match:
            return {
                'intent': 'youtube_search',
                'query': youtube_search_match.group(1)
            }

        search_match = re.match(
            r'(?:search|find) (.+?) (?:in|on) (.+)',
            command_lower
        )
        if search_match:
            return {
                'intent': 'search',
                'query': search_match.group(1),
                'target': search_match.group(2)
            }

        open_match = re.match(
            r'(?:open|start|launch) (.+)',
            command_lower
        )
        if open_match:
            return {
                'intent': 'open',
                'target': open_match.group(1)
            }

        close_match = re.match(
            r'(?:close|exit|quit) (.+)',
            command_lower
        )
        if close_match:
            return {
                'intent': 'close',
                'target': close_match.group(1)
            }

        return {'intent': 'unknown', 'target': command}

    def open_target(self, target: str, assistant: "VoiceAssistant"):
        target_lower = target.lower()

        for folder_name, path in self.special_folders.items():
            if folder_name in target_lower:
                if os.path.exists(path):
                    os.startfile(path)
                    assistant.speak(f"Opening {folder_name}")
                    return
                else:
                    assistant.speak(f"Sorry, I couldn't find the {folder_name} folder.")
                    return

        for site_name, url in self.websites.items():
            if site_name in target_lower:
                webbrowser.open(url)
                assistant.speak(f"Opening {site_name}")
                return

        for app_name, app_info in self.applications.items():
            if app_name in target_lower:
                try:
                    subprocess.Popen(app_info['command'])
                    assistant.speak(f"Opening {app_name}")
                    return
                except Exception as e:
                    print(f"Error opening {app_name}: {e}")
                    if app_info['command'].startswith('ms-'):
                        try:
                            os.system(f'start {app_info["command"]}')
                            assistant.speak(f"Opening {app_name}")
                            return
                        except:
                            pass
                    assistant.speak(f"Sorry, I couldn't open {app_name}. It may not be installed.")
                    return

        if '.' in target and ' ' not in target:
            if not target.startswith(('http://', 'https://')):
                target = 'https://' + target
            webbrowser.open(target)
            assistant.speak(f"Opening website")
        else:
            assistant.speak(f"Sorry, I don't know how to open {target}.")

    def close_target(self, target: str, assistant: "VoiceAssistant"):
        target_lower = target.lower()

        for site_name, url in self.websites.items():
            if site_name in target_lower:
                browsers = {
                    'chrome': {'name': 'Google Chrome', 'shortcut': 'chrome'},
                    'firefox': {'name': 'Mozilla Firefox', 'shortcut': 'firefox'},
                    'edge': {'name': 'Microsoft Edge', 'shortcut': 'msedge'}
                }
                
                for browser_key, browser_info in browsers.items():
                    try:
                        windows = gw.getWindowsWithTitle(browser_info['name'])
                        if not windows:
                            continue

                        for window in windows:
                            win_title = window.title.lower()
                            site_url = url.replace('https://', '').replace('www.', '')
                            
                            tab_patterns = [
                                f"{site_name}",
                                f"{site_url}",
                                f"{site_name.replace(' ', '')}",
                                f"{site_url.split('.')[0]}",
                                f"{site_name.split()[0]}"
                            ]
                            tab_patterns = [p for p in tab_patterns if p]
                            
                            if any(pattern in win_title for pattern in tab_patterns):
                                try:
                                    current_active = gw.getActiveWindow()
                                    window.activate()
                                    time.sleep(0.5)
                                    
                                    window.restore()
                                    window.maximize()
                                    time.sleep(0.3)
                                    
                                    try:
                                        left, top, width, height = window.left, window.top, window.width, window.height
                                        tab_count = len(window.title.split(' - ')) - 1
                                        tab_width = width / max(1, tab_count)
                                        
                                        for i in range(tab_count):
                                            tab_x = left + (i * tab_width) + 50
                                            tab_y = top + 10
                                            pyautogui.click(tab_x, tab_y)
                                            time.sleep(0.2)
                                            
                                            current_title = gw.getActiveWindow().title.lower()
                                            if any(pattern in current_title for pattern in tab_patterns):
                                                break
                                    except Exception as e:
                                        print(f"Error focusing tab: {e}")
                                    
                                    pyautogui.hotkey('ctrl', 'w')
                                    time.sleep(0.5)
                                    
                                    new_title = window.title.lower()
                                    if not any(pattern in new_title for pattern in tab_patterns):
                                        assistant.speak(f"Closed {site_name}")
                                        if current_active:
                                            try:
                                                current_active.activate()
                                            except:
                                                pass
                                        return
                                    
                                    pyautogui.hotkey('alt', 'f4')
                                    time.sleep(0.5)
                                    assistant.speak(f"Closed {site_name} window")
                                    if current_active:
                                        try:
                                            current_active.activate()
                                        except:
                                            pass
                                    return
                                    
                                except Exception as e:
                                    print(f"Error closing {site_name}: {e}")
                                    continue
                        
                        assistant.speak(f"Couldn't find an open {site_name} tab to close")
                        return

                    except Exception as e:
                        print(f"Error checking {browser_info['name']} windows: {e}")
                        continue
    
        for app_name, app_info in self.applications.items():
            if app_name in target_lower:
                try:
                    windows = gw.getWindowsWithTitle(app_info['window_title'])
                    if windows:
                        for window in windows:
                            if (target_lower in window.title.lower() or 
                                app_name in window.title.lower()):
                                try:
                                    window.close()
                                    assistant.speak(f"Closed {app_name}")
                                    return
                                except Exception as e:
                                    print(f"Error closing window {window.title}: {e}")

                    if app_info['command'].endswith('.exe'):
                        try:
                            process_name = os.path.basename(app_info['command'])
                            subprocess.call(f'taskkill /f /im {process_name}', shell=True)
                            assistant.speak(f"Closed {app_name}")
                            return
                        except Exception as e:
                            print(f"Error killing process {app_name}: {e}")
                            if 'alternative_command' in app_info:
                                try:
                                    os.system(app_info['alternative_command'])
                                    assistant.speak(f"Closed {app_name}")
                                    return
                                except Exception as e:
                                    print(f"Error with alternative close: {e}")
                            
                            assistant.speak(f"Sorry, I couldn't close {app_name}.")
                            return
                except Exception as e:
                    print(f"Error closing {app_name}: {e}")
                    assistant.speak(f"Sorry, I couldn't close {app_name}.")
                    return

        try:
            windows = gw.getWindowsWithTitle(target)
            if windows:
                for window in windows:
                    if target_lower in window.title.lower():
                        try:
                            window.close()
                            assistant.speak(f"Closed {target}")
                            return
                        except Exception as e:
                            print(f"Error closing window {window.title}: {e}")
                            assistant.speak(f"Sorry, I couldn't close {target}.")
                            return
        except Exception as e:
            print(f"Error closing window {target}: {e}")

        assistant.speak(f"Sorry, I couldn't find {target} to close it.")

    def search_target(self, query: str, assistant: "VoiceAssistant"):
        webbrowser.open(f'https://www.google.com/search?q={query}')
        assistant.speak(f"Searching for {query}")

    def youtube_search(self, query: str, assistant: "VoiceAssistant"):
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        assistant.speak(f"Searching YouTube for {query}")

    def open_leetcode_problem(self, problem_num: str, assistant: "VoiceAssistant"):
        if problem_num:
            webbrowser.open(f'https://leetcode.com/problemset/all/?search={problem_num}')
            assistant.speak(f"Opening LeetCode problem {problem_num}")

    def open_code_development_window(self, topic: str, assistant: "VoiceAssistant"):
        """
        Generates code for the given topic using ollama.
        Displays the generated code in a Tkinter window.
        Removes unwanted characters like backticks from the generated code.
        """
        import threading

        def clean_code(raw_code: str) -> str:
            # Remove unwanted backticks and trim whitespace
            cleaned = raw_code.replace('```', '').strip()
            return cleaned

        def generate_code():
            status_label.config(text=f"Generating code for {topic}...")
            try:
                instruction = "Write a complete, well-commented Python program on the following topic:"
                prompt = f"{instruction} {topic}"
                response = ollama.generate(
                    model='gemma:2b',
                    prompt=prompt,
                    options={'temperature': 0.3, 'max_tokens': 500}
                )
                raw_code = response.get('response', '').strip()
                code = clean_code(raw_code)
                status_label.config(text="Code generation completed.")
            except Exception as e:
                code = f"Error generating code: {e}"
                status_label.config(text="Error during code generation.")

            # Insert code in chunks to improve UI responsiveness
            text_widget.config(state='normal')
            text_widget.delete('1.0', tk.END)
            chunk_size = 500
            for i in range(0, len(code), chunk_size):
                text_widget.insert(tk.END, code[i:i+chunk_size])
                text_widget.update()
            text_widget.config(state='disabled')

        def run_window():
            window = tk.Tk()
            window.title(f"Code Development: {topic}")
            window.geometry("800x600")

            label = tk.Label(window, text=f"Generated Program on: {topic}", font=("Arial", 14))
            label.pack(pady=10)

            global status_label
            status_label = tk.Label(window, text="", font=("Arial", 10), fg="blue")
            status_label.pack(pady=5)

            scrollbar = tk.Scrollbar(window)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            global text_widget
            text_widget = tk.Text(window, wrap=tk.NONE, yscrollcommand=scrollbar.set, font=("Consolas", 12))
            text_widget.pack(expand=True, fill=tk.BOTH)
            text_widget.config(state='disabled')

            scrollbar.config(command=text_widget.yview)

            # Automatically generate code on window open
            generate_code()

            window.mainloop()

        # Run the Tkinter window in a separate thread to avoid blocking
        threading.Thread(target=run_window, daemon=True).start()
    pass