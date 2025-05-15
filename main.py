from Record import Record
from Log import Logging

import threading
import signal
import os

def signalHandler(signum, frame):
    print("Stopping")
    Rec.stopRecording()
    Log.stopLog()



Rec = Record()
Log = Logging(os.getpid())

signal.signal(signal.SIGINT, signalHandler)

#RecThread = threading.Thread(target=Rec.recordTillInterrupt) 
RecThread = threading.Thread(target=Rec.recordWithVoiceActivity) 
#RecThread = threading.Thread(target=Rec.recordOnlyDuringVoiceActivity) 
LogThread = threading.Thread(target=Log.startLog)

RecThread.start()
LogThread.start()

RecThread.join()
LogThread.join()
