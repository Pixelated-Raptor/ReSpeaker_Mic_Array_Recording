from tuning import Tuning

import pyaudio
import signal
import wave
import usb.core
import usb.util
import sys


class Record:
    
    # Recording Parameters
    RESPEAKER_RATE = 16000
    RESPEAKER_CHANNELS = 1
    RESPEAKER_WIDTH = 2
    RESPEAKER_INDEX = 11
    CHUNK = 2048
    MIC_ARRAY_NAME = "ReSpeaker 4 Mic Array (UAC1.0)"
    #RECORD_SECONDS = 10
    
    # Used for Recording
    p = None
    micIndex = None
    stream = None
    dev = None
    voiceActivity = None

    # File Output Settings
    OUTPUT_DIR = "./Recs/"
    WAVE_OUTPUT_FILENAME = "recording"


    CONTINUERECORDING = True

    def __init__(self):
        self.p = pyaudio.PyAudio()
        
        self.micIndex = self.getMic()
        
        self.stream = self.p.open(
            rate=self.RESPEAKER_RATE,
            format=self.p.get_format_from_width(self.RESPEAKER_WIDTH),
            channels=self.RESPEAKER_CHANNELS,
            input=True,
            input_device_index=self.micIndex
        ) 

        try:
            self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        except:
            print("Couldn't find Mic for Voice Activity Detection!")
            sys.exit(1)

        self.voiceActivity = Tuning(self.dev)

    
    def getMic(self):
        numberDevices = self.p.get_host_api_info_by_index(0).get("deviceCount")

        for i in range(0, numberDevices):
            if(self.p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")) > 0:
                if(self.MIC_ARRAY_NAME in self.p.get_device_info_by_host_api_device_index(0, i).get("name")):
                    return i


    def recordWithVoiceActivity(self):
        fileIndexName = 0
        frames = []

        while self.CONTINUERECORDING:
            if self.voiceActivity.is_voice():
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        self.writeFile(frames, fileIndexName)

        fileIndexName += 1


    def recordOnlyDuringVoiceActivity(self):
        fileIndexName = 0
        frames = []

        while self.CONTINUERECORDING:
            if self.voiceActivity.is_voice():
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
            elif len(frames) > 0:
                self.writeFile(frames, fileIndexName)
                fileIndexName += 1

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
        
    def recordTillInterrupt(self):
        fileIndexName = 0
        frames = []

        while self.CONTINUERECORDING:
            data = self.stream.read(self.CHUNK)
            frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        self.writeFile(frames, fileIndexName)

        fileIndexName += 1


    def writeFile(self, frames, fileIndexName):
        wf = wave.open(self.OUTPUT_DIR + self.WAVE_OUTPUT_FILENAME + str(fileIndexName) + ".wav", "wb")
        wf.setnchannels(self.RESPEAKER_CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(self.RESPEAKER_WIDTH)))
        wf.setframerate(self.RESPEAKER_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        

    def stopRecording(self):
        self.CONTINUERECORDING = False
