import os
import sys
import time
import wave
from threading import Event, Thread
import sounddevice as sd
import numpy as np

# Import your custom configuration
from kosmos_config import *

class KosmosHydro(Thread):
    """
    Thread class for handling audio recording using sounddevice
    """
    def __init__(self, aConf: KosmosConfig):
        super().__init__()
        self._Conf = aConf

        # Events for controlling thread state
        self._start_event = Event()
        self._pause_event = Event()
        self._continue_event = Event()

        # Flags
        self.stop_recording = False

        # Audio recording parameters
        self._samplerate = 48000 #44100  # Hz
        self._channels = 1
        self._chunk = 1024
        self._dtype = 'int16'
        self._frames = []      # recorded frames

    def set_start_event(self, event):
        self._start_event = event
        
    def save_audio(self, outputfile):
        """
        Save recorded audio to a .wav file
        """
        with wave.open(outputfile, 'wb') as wf:
            wf.setnchannels(self._channels)
            wf.setsampwidth(2)  # 16-bit PCM = 2 bytes
            wf.setframerate(self._samplerate)
            wf.writeframes(b''.join(self._frames))
        self._frames.clear()

    def _callback(self, indata, frames, time, status):
        """
        Callback function used by InputStream to receive audio
        """
        if self._pause_event.is_set():
            return  # Don't record during pause

        # Store audio bytes
        self._frames.append(indata.copy().tobytes())

    def run(self):
        """
        Main thread logic: continuously record audio using callback
        """
        self._start_event.wait() 
        with sd.InputStream(samplerate=self._samplerate,
                            channels=self._channels,
                            dtype=self._dtype,
                            callback=self._callback,
                            blocksize=self._chunk):
            while not self.stop_recording:
                if self._pause_event.is_set():
                    self._continue_event.wait()
                    time.sleep(0.001)#   Avoid busy-waiting

    def stop_thread(self):
        """
        Stop recording and terminate the thread
        """
        self.stop_recording = True
        self._continue_event.set()
        self._pause_event.set()
        self._frames.clear()

    def pause(self):
        """
        Pause audio recording
        """
        self._continue_event.clear()
        self._pause_event.set()

    def restart(self):
        """
        Resume or start audio recording
        """
        if self.is_alive():
            self._pause_event.clear()
            self._continue_event.set()
        else:
            self.start()
