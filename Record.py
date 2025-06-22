from tuning import Tuning

import pyaudio
import signal
import wave
import usb.core
import usb.util
import sys
import time
import subprocess
import yaml


class Record:
    """Class for recording audio with a ReSpeaker Mic Array from Seeed Studio

    Using tuning.py provided by Seeed Studio this class allows to record audio
    continously until CONTINUERECORDING is set to false.
    A signal handler can call stop_Recording() to stop the recording.
    """
    
    p = None
    mic_index = None
    stream = None
    dev = None
    voice_activity = None
    voice_direction = None

    CONFIG_FILE = "config.yml"
    config = None

    CONTINUERECORDING = True

    frames = []
    all_frames = []

    split_index = 0

    def __init__(self):
        try:
            with open(self.CONFIG_FILE, "r") as config_file:
                self.config = list(yaml.safe_load_all(config_file))
                self.config = self.config[0]
        except:
            print("Failed to load or parse config.yml in Recording.py!")
            sys.exit(1)
            
        self.p = pyaudio.PyAudio()
        self.mic_index = self.get_Mic()
        
        try:
            self.stream = self.p.open(
                rate=self.config["Recording"]["rate"],
                format=self.p.get_format_from_width(self.config["Recording"]["width"]),
                channels=self.config["Recording"]["channels"],
                input=True,
                input_device_index=self.mic_index
            ) 
        except:
            print("Couldn't open audio stream. Check if Microphone properly connected.")
            sys.exit(1)

        try:
            self.dev = usb.core.find(idVendor=self.config["Recording"]["idVendor"], idProduct=self.config["Recording"]["idProduct"])
        except:
            print("Couldn't find mic for voice activity and angle detection.")
            sys.exit(1)

        self.voice_activity = Tuning(self.dev)

    
    def get_Mic(self):
        numberDevices = self.p.get_host_api_info_by_index(0).get("deviceCount")

        for i in range(0, numberDevices):
            if(self.p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")) > 0:
                if(self.config["Recording"]["mic_name"] in self.p.get_device_info_by_host_api_device_index(0, i).get("name")):
                    return i

        
    def record_till_Interrupt(self):
        """Record continously."""
        while self.CONTINUERECORDING:
            data = self.stream.read(self.config["Recording"]["chunk"])
            self.frames.append(data)
            self.all_frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        self.write_File()


    def write_File(self):
        """Write recording to a file."""

        wf = wave.open(self.config["Recording"]["wave_output"], "wb")
        wf.setnchannels(self.config["Recording"]["channels"])
        wf.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(self.config["Recording"]["width"])))
        wf.setframerate(self.config["Recording"]["rate"])
        wf.writeframes(b''.join(self.all_frames))
        wf.close()
        

    def write_Frames(self, frames):
        """Write frames to a file."""

        wf = wave.open(self.config["Recording"]["live_split_output"] + str(self.split_index) + ".wav", "wb")
        wf.setnchannels(self.config["Recording"]["channels"])
        wf.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(self.config["Recording"]["width"])))
        wf.setframerate(self.config["Recording"]["rate"])
        wf.writeframes(b''.join(frames))
        wf.close()
        

    def stop_Recording(self):
        self.CONTINUERECORDING = False


    def angle_Detection(self):
        self.voice_direction = self.voice_activity.direction
        return self.voice_activity.direction


    def write_Angle(self):
        timer = 0
        f = open(self.config["Recording"]["angle_output"], "w")

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
            "-i", self.config["Recording"]["wave_output"],
            "-acodec", "copy",
            "-f", "segment",
            "-segment_time", "10",
            "-reset_timestamps", "1",
            "-map", "0",
            self.config["Recording"]["split_output"]
            ]

        if subprocess.run(commands).returncode == 0:
            print("Split erfolgreich")
        else:
            print("Split fehlgeschlagen")


    def list_microphones(self):
        numberDevices = self.p.get_host_api_info_by_index(0).get("deviceCount")
        for i in range(numberDevices):
            device_info = self.p.get_device_info_by_host_api_device_index(0, i)
            print(f"Device {i}: {device_info['name']}, Channels: {device_info['maxInputChannels']}")

            
    def split_live(self):
        chunks_per_second = self.config["Recording"]["rate"] / self.config["Recording"]["chunk"]
        chunks_per_split = int(self.config["Recording"]["split_length_sec"] * chunks_per_second)
        chunks_per_overlap = int(self.config["Recording"]["overlap_length_sec"] * chunks_per_second)

        # Keep spliting, as long as enough data is available
        while len(self.frames) >= chunks_per_split:
            self.write_Frames(self.frames[:chunks_per_split])
            self.split_index += 1
            self.frames = self.frames[chunks_per_split - chunks_per_overlap:]

