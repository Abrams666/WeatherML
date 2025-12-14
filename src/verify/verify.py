#import
import pandas as pd
import json
import math
import matplotlib.pyplot as plt

#config
configFile = json.load(open("./config.json", 'r', encoding='utf-8'))
readAndSavePath = configFile["getData"]["download path"]
stationNumber = configFile["getData"]["station number"]
verifySetStart = 0.9
verifySetEnd = 0.95

#val
dataColumns = ["StnPres","SeaPres","StnPresMax","StnPresMin","Temperature","T Max","T Min","Td dew point","RH","RHMin","WS","WD","WSGust","WDGust","PrecpHour","PrecpMax10","PrecpMax60","SunShine","SunshineRate","GloblRad","VisbMean","EvapA","UVI Max","Cloud Amount","TxSoil0cm","TxSoil5cm","TxSoil10cm","TxSoil20cm","TxSoil30cm","TxSoil50cm","TxSoil100cm"]
dataNum = 0
plotDataY = []
plotDataYPred = []

#function
def dot(a,b):
    res = 0

    for i in range(len(a)):
        res += a[i]*b[i]

    return res

def mean(a):
    total=0
    for i in a:
        total+=i

    return total/len(a)

def sd(a):
    tempMean = mean(a)
    total = 0

    for i in a:
        total += (i-tempMean)**2

    return (total/len(a))**0.5


#read weight
weight = []

fileName = "weight.csv"
filePath = readAndSavePath + "/" + fileName
weightFile = pd.read_csv(filePath, encoding="utf-8-sig")

for i in dataColumns:
    weight.append(float(weightFile[i][0]))

#read data
dataStd = []
rainData = []

stdFileName = "dataFile"+ str(stationNumber) + "_std.csv"
stdFilePath = readAndSavePath + "/" + stdFileName
stdDataFile = pd.read_csv(stdFilePath, encoding="utf-8-sig")

for index, row in stdDataFile.iterrows():
    tempData = []
    for i in dataColumns:
        tempData.append(float(row[i]))
    dataNum += 1
    dataStd.append(tempData)

rainFileName = "rainDataFile"+ str(stationNumber) + ".csv"
rainFilePath = readAndSavePath + "/" + rainFileName
rainDataFile = pd.read_csv(rainFilePath, encoding="utf-8-sig")

for index, row in rainDataFile.iterrows():
    rainData.append(float(row["Precp"]))

#get mean std
rainDataMean = mean(rainData)
rainDataSd = sd(rainData)

#get real y ypred
testSetStartIdx = math.ceil(dataNum*verifySetStart)
testSetEndIdx = math.floor(dataNum*verifySetEnd)

for i in range(testSetStartIdx, testSetEndIdx):
    plotDataY.append(rainData[i])
    plotDataYPred.append((dot(weight, dataStd[i])*rainDataSd)+rainDataMean)

#draw
print(plotDataY)
plt.plot(plotDataY, color="blue", label="Real Rain Data")
plt.plot(plotDataYPred, color = "red", label="Predict Rain Data") 
plt.xlabel("Time(Day)")
plt.ylabel("Precp(mm)")

plt.legend()
plt.savefig("./src/verify/verify.png") 
plt.show()

