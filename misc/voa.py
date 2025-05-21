from tuning import Tuning
import usb.core
import usb.util
import time

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
#print dev

if dev:
    mic_tuning = Tuning(dev)
    print(mic_tuning.is_voice())
    while True:
        try:
            print(mic_tuning.is_voice())
            time.sleep(0.125)
        except KeyboardInterrupt:
            break
        
