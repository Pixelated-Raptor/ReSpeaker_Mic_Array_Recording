from Record import Record
from Log import Logging

import threading
import signal
import os


def signalHandler(signum, frame):
    print("Stopping")
    Rec.stopRecording()
    Log.stop_Log()



Rec = Record()
Log = Logging(os.getpid())

signal.signal(signal.SIGINT, signalHandler)

RecThread = threading.Thread(target=Rec.record_till_Interrupt) 
#RecThread = threading.Thread(target=Rec.record_With_Voice_Activity) 
#RecThread = threading.Thread(target=Rec.record_only_during_Voice_Activity) 
LogThread = threading.Thread(target=Log.start_Log)
DOAThread = threading.Thread(target=Rec.angle_Detection)

RecThread.start()
LogThread.start()
DOAThread.start()

RecThread.join()
LogThread.join()
DOAThread.join()
