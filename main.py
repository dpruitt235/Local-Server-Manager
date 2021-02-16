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
owd = None
processArray = []


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        post_data = json.loads(bytes.decode(request.data))
        handleMcStart(post_data)
        return 'OK'
    else:
        return render_template("index.html")


@app.route("/update")
def update():
    update_data = getRamInfo()
    update_data.update(getMcStatus())
    return flask.jsonify(update_data)


# Helper Functions

def handleMcStart(mc_data):
    mcProcess = None
    if mc_data['msg'] == "stop":
        stopMc(mc_data)
    else:
        # Start Server
        # todo Rewrite to take in any number of servers
        if mc_data['srv'] == 0:
            runMcVanillia()
        else:
            runMcForge()


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


def getMcStatus():
    serverStatus = {
        "vanillia": getMcVanilliaStatus(),
        "forge": getMcForgeStatus()
    }
    return serverStatus


def getAmountOfRamTotal():
    memory_Bytes_Total = psutil.virtual_memory().total
    return round(memory_Bytes_Total / 1073741824, 2)


def getAmountOfRamFree():
    memory_Bytes_Free = psutil.virtual_memory().free
    return round(memory_Bytes_Free / 1073741824, 2)


def getAmountOfRamUsed():
    memory_Bytes_Used = psutil.virtual_memory().used
    return round(memory_Bytes_Used / 1073741824, 2)


def getMcVanilliaStatus():
    global mcVanilliaProcess
    return mcVanilliaProcess is not None


def getMcForgeStatus():
    global mcForgeProcess
    return mcForgeProcess is not None


# Todo rewrite to dynamically take in amount of servers
def runMcVanillia():
    global mcVanilliaProcess
    if mcVanilliaProcess is not None:
        return
    executable = 'java -Xms4G -Xmx4G -jar E:\\MinecraftTest\\server\\server.jar'
    os.chdir("E:\\MinecraftTest\\server\\")
    mcVanilliaProcess = subprocess.Popen(executable, stdin=subprocess.PIPE)
    os.chdir(owd)


def runMcForge():
    global mcForgeProcess
    if mcForgeProcess is not None:
        return
    executable = 'java -Xms4G -Xmx4G -jar pathToServerJar'
    os.chdir('pathToServerFolder')
    mcForgeProcess = subprocess.Popen(executable, stdin=subprocess.PIPE)
    os.chdir(owd)


def stopMc(data):
    global mcVanilliaProcess
    global mcForgeProcess
    mcProcess = None
    if data['srv'] == 0:
        mcProcess = mcVanilliaProcess
    else:
        mcProcess = mcForgeProcess
    if mcProcess is None:
        return
    mcProcess.stdin.write("stop\r\n".encode())
    mcProcess.stdin.flush()
    mcProcess = None # todo This is not clearing the original process. Maybe do rewrite now?


def readInConfig():
    data = None
    with open("configs/config.json") as file:
        data = file.read()
    configData = json.loads(data)
    print(configData['0'])


if __name__ == '__main__':
    readInConfig()
    exit()
    owd = os.getcwd()
    app.run()
