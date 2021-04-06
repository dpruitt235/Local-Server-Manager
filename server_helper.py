# Imports
import subprocess
import json
import datetime
import mcstatus
import psutil
import os.path
import os

# Global Variables
owd = os.getcwd()
processArray = []
mcVanillaProcess = None
mcForgeProcess = None
configData = None


# Classes
class ServerInstances:
    def __init__(self, config):
        self.m_Process = None
        self.m_Config_Data = config
        self.m_Active = False


# Getters of Global Variables
def get_process_array():
    return processArray


# Helper Functions
def handleMcStart(mc_data):
    global processArray
    m_process = processArray[mc_data['srv']]

    if mc_data['msg'] == "stop":
        stopServerProcesses(mc_data['srv'])
    else:
        # Start Server
        startServerProcesses(mc_data['srv'])


def getRamInfo():
    utc_str = '{:%m/%d/%y %H:%M:%S UTC}'.format(datetime.datetime.utcnow())
    ramInfo = {
        "ramPercent": psutil.virtual_memory().percent,
        "ramUsed": getAmountOfRamUsed(),
        "ramFree": getAmountOfRamFree(),
        "ramTotal": getAmountOfRamTotal(),
        "time": utc_str
    }
    return ramInfo


def getServerStatus():
    global processArray
    return {str(i): processArray[i].m_Active for i in range(0, len(processArray))}


def getAmountOfRamTotal():
    memory_Bytes_Total = psutil.virtual_memory().total
    return round(memory_Bytes_Total / 1073741824, 2)


def getAmountOfRamFree():
    memory_Bytes_Free = psutil.virtual_memory().free
    return round(memory_Bytes_Free / 1073741824, 2)


def getAmountOfRamUsed():
    memory_Bytes_Used = psutil.virtual_memory().used
    return round(memory_Bytes_Used / 1073741824, 2)


def getProcessStatus(m_pass_data):
    global processArray
    return processArray[m_pass_data].m_Process is not None


def startServerProcesses(m_pass_data):
    global processArray
    mProcess = processArray[m_pass_data]

    os.chdir(mProcess.m_Config_Data['wd'])
    processArray[m_pass_data].m_Process = subprocess.Popen(mProcess.m_Config_Data['launch'], stdin=subprocess.PIPE)
    os.chdir(owd)
    mProcess.m_Active = True


def stopServerProcesses(m_pass_data):
    global processArray
    mProcess = processArray[m_pass_data]

    if mProcess is None:
        return
    if mProcess.m_Config_Data['stopCommandsFlag']:
        mProcess.m_Process.stdin.write(mProcess.m_Config_Data['stopCommand'].encode())
        mProcess.stdin.flush()
    mProcess.m_Active = False
    mProcess.m_Process = None


def readInConfig():
    global processArray
    global configData
    data = None
    with open("configs/config.json") as file:
        data = file.read()
    configData = json.loads(data)

    # Check if all paths are valid
    for i in range(len(configData)):
        temp_data = configData[str(i)]
        processArray.append(ServerInstances(temp_data))

        if not temp_data['status']:  # todo Remove this as a temp check to get around Status set to False Data
            continue

        if not os.path.isdir(temp_data['wd']):
            raise Exception(temp_data['name'] + ": wd is not set as a valid directory. \"" + temp_data['wd'] + "\"")


# Returns a random key. Used for secure keys
def get_random_key(i):
    return os.urandom(i)


