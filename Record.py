from tuning import Tuning

import pyaudio
import signal
import wave
import usb.core
import usb.util
import sys
import time
import subprocess


class Record:
    """Class for recording audio with a ReSpeaker Mic Array from Seeed Studio

    Using tuning.py provided by Seeed Studio this class allows to record audio
    continously until CONTINUERECORDING is set to false.
    A signal handler can call stop_Recording() to stop the recording.
    """
    
    # Recording Parameters
    FACTOR = 2
    RESPEAKER_RATE = 16000
    RESPEAKER_CHANNELS = 1
    RESPEAKER_WIDTH = 2
    RESPEAKER_INDEX = 11
    CHUNK = 1024 * FACTOR
    millisecondsChunk = 64 * FACTOR 
    MIC_ARRAY_NAME = "ReSpeaker 4 Mic Array (UAC1.0)"
    #RECORD_SECONDS = 10
    
    # Used for Recording
    p = None
    mic_index = None
    stream = None
    dev = None
    voice_activity = None
    voice_direction = None

    # File Output Settings
    OUTPUT_DIR = "./Recs/"
    WAVE_OUTPUT_FILENAME = "recording"


    CONTINUERECORDING = True


    def __init__(self):
        self.p = pyaudio.PyAudio()
        
        self.mic_index = self.get_Mic()
        
        try:
            self.stream = self.p.open(
                rate=self.RESPEAKER_RATE,
                format=self.p.get_format_from_width(self.RESPEAKER_WIDTH),
                channels=self.RESPEAKER_CHANNELS,
                input=True,
                input_device_index=self.mic_index
            ) 
        except:
            print("Couldn't open audio stream. Check if Microphone properly connected.")
            sys.exit(1)

        try:
            self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        except:
            print("Couldn't find mic for voice activity and angle detection.")
            sys.exit(1)

        self.voice_activity = Tuning(self.dev)

    
    def get_Mic(self):
        numberDevices = self.p.get_host_api_info_by_index(0).get("deviceCount")

        for i in range(0, numberDevices):
            if(self.p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")) > 0:
                if(self.MIC_ARRAY_NAME in self.p.get_device_info_by_host_api_device_index(0, i).get("name")):
                    return i


    def record_With_Voice_Activity(self):
        """Record only when mic detected voice activity."""

        fileIndexName = 0
        frames = []
        duration = 0

        while self.CONTINUERECORDING:
            if self.voice_activity.is_voice():
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
                duration += self.millisecondsChunk
                print("Duration: " + str(duration))

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        self.write_File(frames, fileIndexName)

        fileIndexName += 1


    #def record_only_during_Voice_Activity(self):
    #    fileIndexName = 0
    #    frames = []

    #    while self.CONTINUERECORDING:
    #        if self.voice_activity.is_voice():
    #            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
    #            frames.append(data)
    #        elif len(frames) > 0:
    #            self.write_File(frames, fileIndexName)
    #            fileIndexName += 1

    #    self.stream.stop_stream()
    #    self.stream.close()
    #    self.p.terminate()
        
        
    def record_till_Interrupt(self):
        """Record continously."""

        fileIndexName = 0
        frames = []

        while self.CONTINUERECORDING:
            data = self.stream.read(self.CHUNK)
            frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        self.write_File(frames, fileIndexName)

        fileIndexName += 1


    def write_File(self, frames, fileIndexName):
        """Write recording to a file with an index."""

        wf = wave.open(self.OUTPUT_DIR + self.WAVE_OUTPUT_FILENAME + str(fileIndexName) + ".wav", "wb")
        wf.setnchannels(self.RESPEAKER_CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(self.RESPEAKER_WIDTH)))
        wf.setframerate(self.RESPEAKER_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        

    def stop_Recording(self):
        self.CONTINUERECORDING = False


    def angle_Detection(self):
        self.voice_direction = self.voice_activity.direction
        #print("DOA: " + str(self.voice_activity.direction))
        return self.voice_activity.direction


    def write_Angle(self):
        timer = 0
        f = open("./Recs/angle.txt", "w")

        while self.CONTINUERECORDING:
            angle = self.angle_Detection()
            f.write(str(timer) + " " + str(angle) + "\n")
            time.sleep(1)
            timer += 1

        f.close()
            


    def split_Audio(self):
        split_intervall_seconds = 10

        commands = [
            "ffmpeg",
            "-i", "./Recs/recording0.wav",
            "-acodec", "copy",
            "-f", "segment",
            "-segment_time", "10",
            "-reset_timestamps", "1",
            "-map", "0",
            "./Recs/chunk%03d.wav"
            ]

        if subprocess.run(commands).returncode == 0:
            print("Split erfolgreich")
        else:
            print("Split fehlgeschlagen")

    def record_single_Chunk(self):    
        """Only used for test purposes. To determine how many milliseconds
        one CHUNK equal to.
        """
        data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        frames = []
        frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        self.write_File(frames, 420)



