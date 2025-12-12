#import
import pandas as pd
import json
import math
import matplotlib.pyplot as plt

#config
configFile = json.load(open("./config.json", 'r', encoding='utf-8'))
readAndSavePath = configFile["getData"]["download path"]
stationNumber = configFile["getData"]["station number"]
testSetRatio = 0.05

#val
dataColumns = ["StnPres","SeaPres","StnPresMax","StnPresMin","Temperature","T Max","T Min","Td dew point","RH","RHMin","WS","WD","WSGust","WDGust","Precp","PrecpHour","PrecpMax10","PrecpMax60","SunShine","SunshineRate","GloblRad","VisbMean","EvapA","UVI Max","Cloud Amount","TxSoil0cm","TxSoil5cm","TxSoil10cm","TxSoil20cm","TxSoil30cm","TxSoil50cm","TxSoil100cm"]
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
data = []
rainData = []

fileName = "data"+ str(stationNumber) + ".csv"
filePath = readAndSavePath + "/" + fileName
dataFile = pd.read_csv(filePath, encoding="utf-8-sig")

for index, row in dataFile.iterrows():
    tempData = []
    for i in dataColumns:
        tempData.append(float(row[i]))
    dataNum += 1
    data.append(tempData)
    rainData.append(tempData[31])

#read std data
dataStd = []

fileName = "data"+ str(stationNumber) + "_std.csv"
filePath = readAndSavePath + "/" + fileName
dataFile = pd.read_csv(filePath, encoding="utf-8-sig")

for index, row in dataFile.iterrows():
    tempData = []
    for i in dataColumns:
        tempData.append(float(row[i]))
    
    dataStd.append(tempData)

#get mean std
rainDataMean = mean(rainData)
rainDataSd = sd(tempData)

print(rainDataMean, rainDataSd)

#get real y
testSetNum = math.ceil(dataNum*testSetRatio)

for i in range(dataNum-testSetNum+1, dataNum):
    plotDataY.append(rainData[i])

#get pred y
for i in range(dataNum-testSetNum, dataNum-1):
    plotDataYPred.append((dot(weight, data[i])*rainDataSd)+rainDataMean+185)

#draw
plt.plot(plotDataY, color="blue")
plt.plot(plotDataYPred, color = "red") 
plt.xlabel("Time(Day)")
plt.ylabel("Precp")

plt.show()

