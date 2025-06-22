from Record import Record

import threading
import signal
import os
import time


def signalHandler(signum, frame):
    print("Stopping")
    Rec.stop_Recording()


def split_handler():
    while Rec.CONTINUERECORDING:
        time.sleep(30)
        Rec.split_live()


Rec = Record()

signal.signal(signal.SIGINT, signalHandler)

RecThread = threading.Thread(target=Rec.record_till_Interrupt) 
SplitThread = threading.Thread(target=split_handler)

RecThread.start()
SplitThread.start()

RecThread.join()
SplitThread.join()

Rec.split_live()

