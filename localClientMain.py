import paho.mqtt.client as mqtt
from lib import argparser as marg
from enum import Enum

import pandas as pd
import numpy as np

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from threading import Thread, Event
import os
from time import sleep

#Filename
Filename = 'SensorDataOut.csv'
#number data points
ndataPoints = 3
#new update
glUpdateState = False
#update counter
glUpdateCounter = 0
#update counter for "index"
glIndexCounter = 0
#number of messages
glNumberOfMessages = 3
#initial values. Will be used as 0 for unsubcribed topics
newCPULoad = 0
newCPUTemp = 0
newVirtMemUsed = 0
newVirtMemAvail = 0

#random thread handlers
threadDataSender = Thread()
thread_stop_event_rand = Event()

#flask thread handlers
threadFlask = Thread()
thread_stop_event_flask = Event()

#register name of app in flask
app = Flask(__name__)
socketio = SocketIO(app)
##################################################################################### - Browser connectivity
#DataSenderThread
class DataSenderThread(Thread):
    def __init__(self):
        self.delay = 4# s delay to send data to the browser
        super(DataSenderThread, self).__init__()

    def dataSend(self):
        print("Sending datasets..")
        while not thread_stop_event_rand.isSet():

            dataset = pd.read_csv(Filename)
            total_rows = dataset.shape[0]
            #data is written without header information. Therefore use iloc
            index = dataset.iloc[total_rows-100:total_rows,1].astype('int32').tolist()
            values_cputemp = dataset.iloc[total_rows-100:total_rows,2].astype('int32').tolist()
            values_cpuload = dataset.iloc[total_rows-100:total_rows,3].astype('int32').tolist()
            values_virtmused = dataset.iloc[total_rows - 100:total_rows, 4].astype('int64').tolist()
            values_virtmavai = dataset.iloc[total_rows - 100:total_rows, 5].astype('int64').tolist()

            values_virtmused = [int(x/1000000) for x in values_virtmused]#to Mb
            values_virtmavai = [int(x /1000000) for x in values_virtmavai]#to Mb

            alldata_to_send = [index, values_cpuload, values_cputemp, values_virtmused, values_virtmavai]

            socketio.emit('new_data', alldata_to_send)
            sleep(self.delay)

    def run(self):
        self.dataSend()
#DataSenderThread - end

#flaskThread
class FlaskThread(Thread):
    def __init__(self):
        super(FlaskThread, self).__init__()

    def flaskServer(self):
        print("Starting flask thread..")
        if __name__ == "__main__":
            app.run()

    def run(self):
        self.flaskServer()
#flaskThread - end


@app.route("/")
def index():
    return render_template('/chart.html')

@socketio.on('connect')
def test_connect():
    global threadDataSender
    print('Client connected')


    if not threadDataSender.isAlive():
        print("Starting thread for sending data to browser..")
        threadDataSender = DataSenderThread()
        threadDataSender.start()


threadFlask = FlaskThread()
threadFlask.start()

##################################################################################### -end Browser connectivity

##################################################################################### - Sensor connectivity
dataFieldNames = ['Index','CpuTemp','CpuLoad','VirtMemUsed','VirtMemAvail']
dataindex = np.arange(ndataPoints)

raw_assocData = {'Index' : np.zeros(shape=(ndataPoints), dtype=int ),
                 'CpuTemp' : np.zeros(shape=(ndataPoints), dtype=float ),
                 'CpuLoad' : np.zeros(shape=(ndataPoints), dtype=float ),
                 'VirtMemUsed' : np.zeros(shape=(ndataPoints), dtype=int ),
                 'VirtMemAvail' : np.zeros(shape=(ndataPoints), dtype=int )}


pd_frame = pd.DataFrame(raw_assocData, columns=dataFieldNames, index=dataindex)


rawDataTime = np.zeros(ndataPoints)
rawDataCpuLoad = np.zeros(ndataPoints)


#TODO: read only last to knopw index
#TODO: add TIMESTAMP index
def loadDataLastIndex():
    if os.path.isfile(Filename) and os.path.getsize(Filename) > 0:
        #load from file
        data = pd.read_csv(Filename, names=dataFieldNames) #nrows=1)
        lastindex = data['Index'].iloc[-1]
        return lastindex
    else:
        #create a new data structure
        return 0#rawdata


def writeDatatoCSV(dataframe):
    #if os.path.isfile(Filename):
        dataframe.to_csv(Filename, mode='a', header=False)
    #else:
       # dataframe.to_csv


class Subsriptions(Enum):
    CPUTEMP = 0,
    CPULOAD = 1,
    MEMORIES = 2

def on_message(client, userdata, message):
        global glUpdateCounter
        global glIndexCounter
        global pd_frame
        global newCPULoad
        global newCPULoad
        global newCPUTemp
        global newVirtMemUsed
        global newVirtMemAvail

        mesDec = str(message.payload.decode("utf-8"))
        print("message received ", mesDec)
        print(glIndexCounter)
        #print("message topic=", message.topic)
        #print("message qos=", message.qos)
        #print("message retain flag=", message.retain)


        if (message.topic == "cpuload"):
            newCPULoad = float(mesDec)
        if (message.topic == "cputemp"):
            if (mesDec != "None"):
                newCPUTemp = float(mesDec[:len(mesDec)-2])
            else:
                newCPUTemp = 25
        if (message.topic == "memories"):
            mes_list = list(mesDec.split(','))
            newVirtMemAvail = int(mes_list[0][1:])
            newVirtMemUsed = int(mes_list[1][1:(len(mes_list[1])-1)])

        #update global counter
        glUpdateCounter += 1
        #if the glUpdateCounter reach the amount. glNumberOfMessages is equal to the amount of subcriptions
        if glUpdateCounter == glNumberOfMessages :

            currentRow = glIndexCounter % ndataPoints

            #Cputemp is not always properly recognized by temp reader in remote sensor. insert dummy value
            if newCPUTemp == "None":
                newCPUTemp = 25

            pd_frame.at[currentRow, 'Index'] = glIndexCounter
            pd_frame.at[currentRow, 'CpuLoad'] = newCPULoad
            pd_frame.at[currentRow, 'CpuTemp'] = newCPUTemp
            pd_frame.at[currentRow, 'VirtMemUsed'] = newVirtMemUsed
            pd_frame.at[currentRow, 'VirtMemAvail'] = newVirtMemAvail

            glUpdateCounter = 0
            glIndexCounter += 1
            if currentRow == ndataPoints - 1:
                writeDatatoCSV(pd_frame)


'''        
        #update for message data
        if (message.topic == "cpuload"):
            if (glTimeUpdateCounter < 100):
                rawDataCpuLoad[glUpdateCounter] = float(mesDec)
            else:
                np.roll(rawDataCpuLoad, -1)
                rawDataCpuLoad[100] = float(mesDec)

        #update "timestamp". Based on a simple counter at the moment
        if glUpdateCounter == glNumberOfMessages:
            glUpdateCounter = 0
            glTimeUpdateCounter = glTimeUpdateCounter + 1

            if (glTimeUpdateCounter < 100):
                rawDataTime[glTimeUpdateCounter] = glTimeUpdateCounter
            else:
                np.roll(rawDataTime, -1)
                rawDataTime[100] = glTimeUpdateCounter
'''


class SysSensorSubscriber:
    def __init__(self, ipv4, port, servicesToSubscribe):
        self.client = mqtt.Client("SensorListener")
        #self.client.on_connect = self.on_connect
        #self.client.on_disconnect = self.on_disconnect
        self.client.on_message = on_message
        self.hostAddress = ipv4
        self.port = port
        self.number_of_subscriptions = 0

        #assign True/False to each service accordingly to input values
        for pair in servicesToSubscribe:
            if pair[0] == Subsriptions.CPUTEMP:
                self.bCpuTemp = pair[1]
            if pair[0] == Subsriptions.CPULOAD:
                self.bCpuLoad = pair[1]
            if pair[0] == Subsriptions.MEMORIES:
                self.bMemories = pair[1]

    def connect_to_broker(self):
        self.client.connect(self.hostAddress, keepalive=60)

    def client_loopforever(self):
        self.client.loop_forever()
        # sensorSub.client.loop_start()
        # self.client.loop_forever()

        # time.sleep(10)
        # sensorSub.client.loop_stop()

    def subscribe_to_topics(self):
        if self.bCpuTemp:
            self.client.subscribe("cputemp")
            print ("Subscribing to topic 'cputemp'")
            self.number_of_subscriptions +=1
        if self.bCpuLoad:
            self.client.subscribe("cpuload")
            print ("Subscribing to topic 'cpuload'")
            self.number_of_subscriptions += 1
        if self.bMemories:
            self.client.subscribe("memories")
            print ("Subscribing to topic 'memories'")
            self.number_of_subscriptions += 1

        return self.number_of_subscriptions
##################################################################################### - end Sensor connectivity

#run argument parser
arg_parser = marg.InputArguments()
args = arg_parser.parser.parse_args()

#update global index
glIndexCounter = loadDataLastIndex() + 1

sensorSub = SysSensorSubscriber(args.host, args.p,
                                ((Subsriptions.CPUTEMP, args.ct),
                                (Subsriptions.CPULOAD, args.cl),
                                (Subsriptions.MEMORIES, args.memo)) )

sensorSub.connect_to_broker()

#update global number of messages to wait for in each iterations
glNumberOfMessages = sensorSub.subscribe_to_topics()

#MQTT subscribe requires run in a loop
sensorSub.client_loopforever()



