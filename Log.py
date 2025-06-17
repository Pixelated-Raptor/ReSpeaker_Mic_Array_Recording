import time
import psutil
import re
import yaml


class Logging:

    #OUTPUT_DIR = "./Logs/"
    #LOGFILE = OUTPUT_DIR + "log.txt"

    CONTINUERECORDING = True

    file = None
    pid = None
    process = None

    CONFIG_FILE = "config.yml"
    config = None

    def __init__(self, pid):
        try:
            with open(self.CONFIG_FILE, "r") as config_file:
                self.config = list(yaml.safe_load_all(config_file))
                self.config = self.config[1]
        except:
            print("Failed to load or parse config.yml in Log.py!")

        
        self.file = open(self.config["Logging"]["log_output"], "w")
        self.pid = pid
        self.process = psutil.Process(self.pid)


    def write_CPU_usage(self, timer):
        cpu = psutil.cpu_percent()
        owncpu = self.process.cpu_percent() / psutil.cpu_count()
        self.file.write(str(timer) + "sec." + " CPU% (system): " + str(cpu) + "\n")
        self.file.write(str(timer) + "sec." + " CPU% (" + str(self.pid) + "): " + str(owncpu) + "\n")
         

    def write_RAM_usage(self, timer):
        ram = psutil.virtual_memory()
        ram = re.findall("percent=\d+.\d+", str(ram)) 
        ram = re.findall("\d+.\d", str(ram))

        ownram = self.process.memory_percent()

        self.file.write(str(timer) + "sec." + " RAM% (system): " + str(ram) + "\n")
        self.file.write(str(timer) + "sec." + " RAM% (" + str(self.pid) + "): " + str(ownram) + "\n")


    def start_Log(self):
        timer = 0

        while self.CONTINUERECORDING:
            self.write_CPU_usage(timer)
            self.write_RAM_usage(timer)
            print(str(timer))
            time.sleep(1)
            timer += 1

        self.file.close()


    def stop_Log(self):
        self.CONTINUERECORDING = False
