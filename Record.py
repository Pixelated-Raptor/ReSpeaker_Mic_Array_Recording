import pyaudio
import signal
import wave

class Record:
    
    RESPEAKER_RATE = 16000
    RESPEAKER_CHANNELS = 1
    RESPEAKER_WIDTH = 2
    RESPEAKER_INDEX = 11
    CHUNK = 1024
    #RECORD_SECONDS = 10
    
    OUTPUT_DIR = "./Recs/"
    WAVE_OUTPUT_FILENAME = "output"
    MIC_ARRAY_NAME = "ReSpeaker 4 Mic Array (UAC1.0)"

    CONTINUERECORDING = True
    
    p = None
    micIndex = None
    stream = None


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


    def getMic(self):
        numberDevices = self.p.get_host_api_info_by_index(0).get("deviceCount")

        for i in range(0, numberDevices):
            if(self.p.get_device_info_by_host_api_device_index(0, 1).get("maxInputChannels")) > 0:
                if(self.MIC_ARRAY_NAME in self.p.get_device_info_by_host_api_device_index(0, i).get("name")):
                    return i


    def startRecording(self):
        fileIndexName = 0
        frames = []

        while self.CONTINUERECORDING:
            data = self.stream.read(self.CHUNK)
            frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        wf = wave.open(self.OUTPUT_DIR + self.WAVE_OUTPUT_FILENAME + str(fileIndexName) + ".wav", "wb")
        wf.setnchannels(self.RESPEAKER_CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.p.get_format_from_width(self.RESPEAKER_WIDTH)))
        wf.setframerate(self.RESPEAKER_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        fileIndexName += 1


    def stopRecording(self):
        self.CONTINUERECORDING = False
