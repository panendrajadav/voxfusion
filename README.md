# VoxFusion Voice Assistant

VoxFusion is a Python-based voice assistant designed to perform various tasks such as executing commands, controlling system volume, taking screenshots, and interacting with users through conversational AI.

## Features

- Voice Commands: Execute system commands like opening applications, searching the web, and controlling system settings.
- Volume Control: Adjust system volume, mute, or unmute.
- Screenshot Capture: Take screenshots and save them to specified locations.
- Conversational AI: Interact with the assistant using natural language, powered by the Ollama Gemma model.
- GIF Animation: Display a GIF animation when the assistant is active.
- Reminders and Alarms: Set reminders and alarms for specific times.

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you have Python 3.8 or higher installed on your system.

## Usage

1. Run the `voxfusion.py` script to start the assistant:
   ```bash
   python voxfusion.py
   ```
2. Use voice commands to interact with the assistant. For example:
   - "What is your name?"
   - "Take a screenshot and save it in the documents."
   - "Set an alarm for 7:30 AM."

## File Structure

- `voxfusion.py`: Main entry point for the application.
- `voice_assistant.py`: Core logic for the voice assistant.
- `command_executor.py`: Handles command execution and system interactions.
- `volume_controller.py`: Manages system volume control.
- `voice.gif`: Animation displayed when the assistant is active.

## Requirements

- Python 3.8 or higher
- Required Python libraries:
  - `speechrecognition`
  - `pyttsx3`
  - `pyautogui`
  - `ollama`
  - `pillow`
  - `pycaw`
  - `psutil`

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Developed by the VoxFusion team.
- Panendra Rao .J
- Shaik Asad Ahmed
- Umar Fathima Kulsum
- Vijay Kumar Reddy. N