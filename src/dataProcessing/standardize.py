#import
import pandas as pd
import json

#function
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

def is_number(s):
    try:
        float(s)  # 嘗試轉換為浮點數
        return True
    except ValueError:
        return False



#config
print("Loading configuration...")
configFile = json.load(open("./config.json", 'r', encoding='utf-8'))

stationNumber = configFile["getData"]["station number"]
startYear= configFile["getData"]["start year"]
startMonth= configFile["getData"]["start month"]
endYear= configFile["getData"]["end year"]
endMonth= configFile["getData"]["end month"]
readAndSavePath = configFile["getData"]["download path"]

print("Station number: " + stationNumber)
print("Data start date: " + str(startYear) + "/" + str(startMonth))
print("Data end date: " + str(endYear) + "/" + str(endMonth))
print("Download path: " + readAndSavePath)
print("-------------------------------")

#setup

#create a new CSV file
print("Creating new CSV file...")
dataColumns = ["StnPres","SeaPres","StnPresMax","StnPresMin","Temperature","T Max","T Min","Td dew point","RH","RHMin","WS","WD","WSGust","WDGust","Precp","PrecpHour","PrecpMax10","PrecpMax60","SunShine","SunshineRate","GloblRad","VisbMean","EvapA","UVI Max","Cloud Amount","TxSoil0cm","TxSoil5cm","TxSoil10cm","TxSoil20cm","TxSoil30cm","TxSoil50cm","TxSoil100cm"]
data = {"StnPres": [],"SeaPres": [],"StnPresMax": [],"StnPresMin": [],"Temperature": [],"T Max": [],"T Min": [],"Td dew point": [],"RH": [],"RHMin": [],"WS": [],"WD": [],"WSGust": [],"WDGust": [],"PrecpHour": [],"PrecpMax10": [],"PrecpMax60": [],"SunShine": [],"SunshineRate": [],"GloblRad": [],"VisbMean": [],"EvapA": [],"UVI Max": [],"Cloud Amount": [],"TxSoil0cm": [],"TxSoil5cm": [],"TxSoil10cm": [],"TxSoil20cm": [],"TxSoil30cm": [],"TxSoil50cm": [],"TxSoil100cm": [],"Precp": []}

#read csv files and combine
print("Loading data file...")
fileName = "data"+ str(stationNumber) + ".csv"
filePath = readAndSavePath + "/" + fileName

df = pd.read_csv(filePath, encoding="utf-8-sig")

print("Standardizing data...")
for j in dataColumns:
    tempData=[]

    for index, row in df.iterrows():
        if(is_number(row[j])):
            tempData.append(row[j])

    dataMean = mean(tempData)
    dataSd = sd(tempData)

    for k in tempData:
        data[j].append((k - dataMean) / dataSd)

#save csv
print("Saving CSV file...")
df = pd.DataFrame(data)
df.to_csv(readAndSavePath + "/"+"data" + str(stationNumber) + "_std.csv", index=False, encoding="utf-8-sig")
print("data" + str(stationNumber) + ".csv has been created successfully at " + readAndSavePath + ".")