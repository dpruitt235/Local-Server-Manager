# Imports
import psutil
import json
import subprocess
import datetime
import mcstatus
import flask
import os.path
from flask import Flask, render_template, url_for, request

# Global Vars
app = Flask(__name__)
owd = os.getcwd()
processArray = []
mcVanillaProcess = None
mcForgeProcess = None
configData = None


class ServerInstances:
    def __init__(self, config):
        self.m_Process = None
        self.m_Config_Data = config
        self.m_Active = False


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        post_data = json.loads(bytes.decode(request.data))
        handleMcStart(post_data)
        return 'OK'
    else:
        global processArray
        return render_template("index_revision.html", servers=processArray, server_number=0, active=True,
                               image_source="minecraft-vanilla.jpg", server_name="Minecraft", server_text="A minecraft Server")


@app.route("/update")
def update():
    update_data = getRamInfo()
    update_data["servers"] = getServerStatus()
    return flask.jsonify(update_data)


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


if __name__ == '__main__':
    readInConfig()
    app.run(host='192.168.0.55', port='80')
