import os
import time
import wave
from threading import Event, Thread

import pyaudio
# Importation des fichiers
from kosmos_config import *


class KosmosHydro(Thread):
    """
    Classe dérivée de Thread qui gère l'enregistrement audio
    """
    def __init__(self, aConf: KosmosConfig):
        """
        Description
        """
        Thread.__init__(self)
        
        self._Conf = aConf

        # Booléens pour les évènements
        self._stopevent = Event()
        self._pause_event = Event()
        self._continue_event = Event()
        
        # Initialisation de PyAudio
        self._FORMAT = pyaudio.paInt16
        self._CHANNELS = 1
        self._RATE = 44100
        self._CHUNK = 1024 
        self._audio = pyaudio.PyAudio()
        
        self.stop_recording = False        
        self._stream = self._audio.open(format=self._FORMAT,
        channels=self._CHANNELS,
        rate=self._RATE,
        input=True,
        frames_per_buffer=self._CHUNK)
        
        
    def save_audio(self,outputfile):
        with wave.open(outputfile, 'wb') as wf:
            wf.setnchannels(self._CHANNELS)
            wf.setsampwidth(self._audio.get_sample_size(self._FORMAT))
            wf.setframerate(self._RATE)
            wf.writeframes(b''.join(self._frames))
            wf.close()
            
                  
    def run(self): 
            while not self.stop_recording:
                
                
                self._frames = []
                              
                while not self._pause_event.isSet():
                    data = self._stream.read(self._CHUNK, exception_on_overflow = False) # la perte de quelques frames n'altère pas la qualité de l'enregistrement
                    self._frames.append(data)
                else:
                    self._continue_event.wait()
            logging.info("Thread Audio terminé")
            self._stream.stop_stream()
            self._stream.close()
            self._audio.terminate()

    
    def stop_thread(self):
        self.stop_recording = True
        self._continue_event.set()
        self._pause_event.set()

    def pause(self):
        """suspend le thread pour pouvoir le redémarrer."""
        self._continue_event.clear()
        self._pause_event.set()

    def restart(self):
        """démarre ou redémarre le thread audio"""
        if self.is_alive():
            self._pause_event.clear()
            self._continue_event.set()
        else:
            self.start()
            