from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VolumeController:
    # ...existing code from VolumeController class...
    def __init__(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
    
    def get_volume(self):
        return self.volume.GetMasterVolumeLevelScalar()
    
    def set_volume(self, level):
        self.volume.SetMasterVolumeLevelScalar(level, None)
    
    def increase_volume(self, amount=0.1):
        current = self.get_volume()
        new_level = min(1.0, current + amount)
        self.set_volume(new_level)
        return new_level
    
    def decrease_volume(self, amount=0.1):
        current = self.get_volume()
        new_level = max(0.0, current - amount)
        self.set_volume(new_level)
        return new_level
    
    def mute(self):
        self.volume.SetMute(1, None)
    
    def unmute(self):
        self.volume.SetMute(0, None)
    pass