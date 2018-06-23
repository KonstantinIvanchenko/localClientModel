import paho.mqtt.client as mqtt
from lib import argparser as marg
from enum import Enum

import pandas as pd
import os
from time import sleep

import numpy as np


#Filename
Filename = 'SensorDataOut.csv'
#number data points
ndataPoints = 100
#new update
glUpdateState = False
#update counter
glUpdateCounter = 0
#update counter for "time"
glTimeUpdateCounter = 0
#number of messages
glNumberOfMessages = 3

newCPULoad = 0
newCPUTemp = 0
newVirtMemUsed = 0
newVirtMemAvail = 0

dataFieldNames = ['CpuTemp','CpuLoad','VirtMemUsed','VirtMemAvail']

raw_assocData = {'CpuTemp' : pd.Series(0, index=list(range(ndataPoints)),dtype='float32' ),
                 'CpuLoad' : pd.Series(0, index=list(range(ndataPoints)),dtype='float32' ),
                 'VirtMemUsed' : pd.Series(0, index=list(range(ndataPoints)), dtype='int32' ),
                 'VirtMemAvail' : pd.Series(0, index=list(range(ndataPoints)),dtype='int32' )}

pd_frame = pd.DataFrame(raw_assocData, dataFieldNames)


rawDataTime = np.zeros(ndataPoints)
rawDataCpuLoad = np.zeros(ndataPoints)


#TODO: read only last to knopw index
#TODO: add TIMESTAMP index
def loadDataLastIndex():
    if os.path.isfile(Filename) and os.path.getsize(Filename) > 0:
        #load from file
        data = pd.read_csv(Filename, names=dataFieldNames, nrows=1)
        return data.get_value(0, '')
    else:
        #create a new data structure
        return 0#rawdata


def writeDatatoCSV(dataframe):
    if os.path.isfile(Filename) and os.path.getsize(Filename) > 0:
        dataframe.to_csv(Filename, mode='a', header=False)

'''
tempTrace = plg.Scatter(x=raw_assocData['Timestamp'], y=raw_assocData['CpuTemp'],
                        xaxis='Timestamp',yaxis='CpuTemp')
loadTrace = plg.Scatter(x=raw_assocData['Timestamp'], y=raw_assocData['CpuLoad'],
                        xaxis='Timestamp', yaxis='CpuLoad')
virtMemAvailTrace = plg.Scatter(x=raw_assocData['Timestamp'], y=raw_assocData['CpuLoad'],
                        xaxis='Timestamp', yaxis='VirtMemAvail')

data = plg.Data([tempTrace, loadTrace, virtMemAvailTrace])

figure = plg.Figure(data=data)
figure = pl.tools.make_subplots(rows=3, cols=1)
figure.append_trace(tempTrace, 1, 1)
figure.append_trace(loadTrace, 2, 1)
figure.append_trace(virtMemAvailTrace, 3, 1)

pl.offline.plot(figure,  filename='Sensor data')
'''

class Subsriptions(Enum):
    CPUTEMP = 0,
    CPULOAD = 1,
    MEMORIES = 2

def on_message(client, userdata, message):
        global glUpdateCounter
        global glTimeUpdateCounter
        global pd_frame
        global newCPULoad
        global newCPULoad
        global newCPUTemp
        global newVirtMemUsed
        global newVirtMemAvail

        mesDec = str(message.payload.decode("utf-8"))
        print("message received ", mesDec)
        print(glTimeUpdateCounter)
        #print("message topic=", message.topic)
        #print("message qos=", message.qos)
        #print("message retain flag=", message.retain)


        if (message.topic == "cpuload"):
            newCPULoad = mesDec
        if (message.topic == "cputemp"):
            newCPUTemp = mesDec
        if (message.topic == "memories"):
            mes_list = mesDec.split(',')
            newVirtMemAvail = mes_list[0]
            newVirtMemUsed = mesDec[1]


        if glUpdateCounter == glNumberOfMessages:
            glUpdateCounter = 0
            glTimeUpdateCounter = glTimeUpdateCounter + 1

            currentRow = glTimeUpdateCounter % ndataPoints
            pd_frame.at[currentRow, 'CpuLoad'] = newCPULoad
            pd_frame.at[currentRow, 'CpuTemp'] = newCPUTemp
            pd_frame.at[currentRow, 'VirtMemUsed'] = newVirtMemUsed
            pd_frame.at[currentRow, 'VirtMemAvailable'] = newVirtMemAvail

            if currentRow == 0:
                writeDatatoCSV(pd_frame)

        #Write to dataframe here
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



            #plt.subplot(212)
            #plt.plot(rawDataTime, rawDataCpuLoad, 'r--')



class SysSensorSubscriber:
    def __init__(self, ipv4, port, servicesToSubscribe):
        self.client = mqtt.Client("SensorListener")
        #self.client.on_connect = self.on_connect
        #self.client.on_disconnect = self.on_disconnect
        self.client.on_message = on_message
        self.hostAddress = ipv4
        self.port = port

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
        #sensorSub.client.loop_start()
        #self.client.loop_forever()
        self.subscribe_to_topics()
        self.client.loop_forever()
        #time.sleep(10)
        #sensorSub.client.loop_stop()

    def subscribe_to_topics(self):
        if self.bCpuTemp:
            self.client.subscribe("cputemp")
            print ("Subscribing to topic 'cputemp'")
        if self.bCpuLoad:
            self.client.subscribe("cpuload")
            print ("Subscribing to topic 'cpuload'")
        if self.bMemories:
            self.client.subscribe("memories")
            print ("Subscribing to topic 'memories'")



#run argument parser
arg_parser = marg.InputArguments()
args = arg_parser.parser.parse_args()

data = loadData()

sensorSub = SysSensorSubscriber(args.host, args.p,
                                ((Subsriptions.CPUTEMP, args.ct),
                                (Subsriptions.CPULOAD, args.cl),
                                (Subsriptions.MEMORIES, args.memo)) )

sensorSub.connect_to_broker()

