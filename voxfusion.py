from voice_assistant import VoiceAssistant
from volume_controller import VolumeController
from command_executor import CommandExecutor

if __name__ == "__main__":
    # Initialize components
    volume_controller = VolumeController()
    command_executor = CommandExecutor()
    voice_assistant = VoiceAssistant(volume_controller, command_executor)

    # Start the voice assistant
    voice_assistant.run()