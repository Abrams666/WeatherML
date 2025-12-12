#import
import pandas as pd
import json

#function
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def mean(a):
    total=0
    for i in a:
        total+=float(i)

    return total/len(a)

def sd(a):
    tempMean = mean(a)
    total = 0

    for i in a:
        total += (float(i)-tempMean)**2

    return (total/len(a))**0.5

#config
print("Loading configuration...")
configFile = json.load(open("./config.json", 'r', encoding='utf-8'))

stationNumber = configFile["getData"]["station number"]
startYear= configFile["getData"]["start year"]
startMonth= configFile["getData"]["start month"]
endYear= configFile["getData"]["end year"]
endMonth= configFile["getData"]["end month"]
readAndSavePath = configFile["getData"]["download path"]
testSetRatio = configFile["getData"]["test set ratio"]

print("Station number: " + stationNumber)
print("Data start date: " + str(startYear) + "/" + str(startMonth))
print("Data end date: " + str(endYear) + "/" + str(endMonth))
print("Download path: " + readAndSavePath)
print("-------------------------------")

#setup
start = int(startYear) * 12 + int(startMonth)
end = int(endYear) * 12 + int(endMonth)

#create a new CSV file
print("Creating new CSV file...")
dataColumns = ["StnPres","SeaPres","StnPresMax","StnPresMin","Temperature","T Max","T Min","Td dew point","RH","RHMin","WS","WD","WSGust","WDGust","PrecpHour","PrecpMax10","PrecpMax60","SunShine","SunshineRate","GloblRad","VisbMean","EvapA","UVI Max","Cloud Amount","TxSoil0cm","TxSoil5cm","TxSoil10cm","TxSoil20cm","TxSoil30cm","TxSoil50cm","TxSoil100cm"]
dataColumnsChinese = ["測站氣壓(hPa)","海平面氣壓(hPa)","測站最高氣壓(hPa)","測站最低氣壓(hPa)","氣溫(℃)","最高氣溫(℃)","最低氣溫(℃)","露點溫度(℃)","相對溼度(%)","最小相對溼度(%)","風速(m/s)","風向(360degree)","最大瞬間風(m/s)","最大瞬間風風向(360degree)","降水時數(hour)","最大十分鐘降水量(mm)","最大六十分鐘降水量(mm)","日照時數(hour)","日照率(%)","全天空日射量(MJ/㎡)","能見度(km)","A型蒸發量(mm)","日最高紫外線指數","總雲量(0~10)","地溫0cm","地溫5cm","地溫10cm","地溫20cm","地溫30cm","地溫50cm","地溫100cm"]
data = {"StnPres": [],"SeaPres": [],"StnPresMax": [],"StnPresMin": [],"Temperature": [],"T Max": [],"T Min": [],"Td dew point": [],"RH": [],"RHMin": [],"WS": [],"WD": [],"WSGust": [],"WDGust": [],"PrecpHour": [],"PrecpMax10": [],"PrecpMax60": [],"SunShine": [],"SunshineRate": [],"GloblRad": [],"VisbMean": [],"EvapA": [],"UVI Max": [],"Cloud Amount": [],"TxSoil0cm": [],"TxSoil5cm": [],"TxSoil10cm": [],"TxSoil20cm": [],"TxSoil30cm": [],"TxSoil50cm": [],"TxSoil100cm": []}
rainData = {"Precp": []}

#read csv files and combine
print("Combining CSV files...")
skipRain = False
for i in range(end, start + 1):
    year = i // 12
    month = i % 12
    if month == 0:
        year -= 1
        month = 12

    fileName = str(stationNumber) + "-" + str(year) + "-" + str(month).zfill(2) + ".csv"
    filePath = readAndSavePath + "/" + fileName

    df = pd.read_csv(filePath, encoding="utf-8-sig")
    for index, row in df.iterrows():
        for j in range(len(dataColumns)):
            data[dataColumns[j]].append(row[dataColumnsChinese[j]])
        rainData["Precp"].append(row["降水量(mm)"])
    print("Finished reading and combining data of " + fileName + ".")
print("-------------------------------")
        
#remove error value
for i in range(len(rainData["Precp"])-1,-1,-1):
    if(rainData["Precp"][i] == "Precp" or rainData["Precp"][i] == "--"):
        rainData["Precp"].pop(i)
        for j in range(len(dataColumns)):
            data[dataColumns[j]].pop(i)

rainData["Precp"].pop(0)
for i in range(len(dataColumns)):
    data[dataColumns[i]].pop(-1)

for i in range(len(rainData["Precp"])-1,1,-1):
    isAllNum = True

    for j in range(len(dataColumns)):
        if(not is_number(data[dataColumns[j]][i])):
            isAllNum = False
            break

    if((not isAllNum) or (not is_number(rainData["Precp"][i]))):
        rainData["Precp"].pop(i)
        for j in range(len(dataColumns)):
            data[dataColumns[j]].pop(i)

#to float
for i in range(len(rainData["Precp"])):
    rainData["Precp"][i] = float(rainData["Precp"][i])

for i in range(len(dataColumns)):
    for j in range(len(data[dataColumns[i]])):
        data[dataColumns[i]][j] = float(data[dataColumns[i]][j])

#save csv
print("Saving CSV file...")
dataFile = pd.DataFrame(data)
splitIndex = int(len(dataFile) * (1 - testSetRatio))
trainSetDataFile = dataFile.iloc[:splitIndex]
testSetDataFile  = dataFile.iloc[splitIndex:]

rainDataFile = pd.DataFrame(rainData)
splitIndex = int(len(rainDataFile) * (1 - testSetRatio))
trainSetRainDataFile = rainDataFile.iloc[:splitIndex]
testSetRainDataFile  = rainDataFile.iloc[splitIndex:]

trainSetDataFile.to_csv(readAndSavePath + "/"+"trainSetDataFile" + str(stationNumber) + ".csv", index=False, encoding="utf-8-sig")
testSetDataFile.to_csv(readAndSavePath + "/"+"testSetDataFile" + str(stationNumber) + ".csv", index=False, encoding="utf-8-sig")
trainSetRainDataFile.to_csv(readAndSavePath + "/"+"trainSetRainDataFile" + str(stationNumber) + ".csv", index=False, encoding="utf-8-sig")
testSetRainDataFile.to_csv(readAndSavePath + "/"+"testSetRainDataFile" + str(stationNumber) + ".csv", index=False, encoding="utf-8-sig")
print("CSV has been created successfully at " + readAndSavePath)

#std
m = mean(rainData["Precp"])
s = sd(rainData["Precp"])
for i in range(len(rainData["Precp"])):
    rainData["Precp"][i] = (rainData["Precp"][i]-m)/s

for i in range(len(dataColumns)):
    m = mean(data[dataColumns[i]])
    s = sd(data[dataColumns[i]])
    for j in range(len(data[dataColumns[i]])):
        data[dataColumns[i]][j] = (data[dataColumns[i]][j]-m)/s

#save std csv
print("Saving CSV file...")
dataFile = pd.DataFrame(data)
splitIndex = int(len(dataFile) * (1 - testSetRatio))
trainSetDataFile = dataFile.iloc[:splitIndex]
testSetDataFile  = dataFile.iloc[splitIndex:]

rainDataFile = pd.DataFrame(rainData)
splitIndex = int(len(rainDataFile) * (1 - testSetRatio))
trainSetRainDataFile = rainDataFile.iloc[:splitIndex]
testSetRainDataFile  = rainDataFile.iloc[splitIndex:]

trainSetDataFile.to_csv(readAndSavePath + "/"+"trainSetDataFile" + str(stationNumber) + "_std.csv", index=False, encoding="utf-8-sig")
testSetDataFile.to_csv(readAndSavePath + "/"+"testSetDataFile" + str(stationNumber) + "_std.csv", index=False, encoding="utf-8-sig")
trainSetRainDataFile.to_csv(readAndSavePath + "/"+"trainSetRainDataFile" + str(stationNumber) + "_std.csv", index=False, encoding="utf-8-sig")
testSetRainDataFile.to_csv(readAndSavePath + "/"+"testSetRainDataFile" + str(stationNumber) + "_std.csv", index=False, encoding="utf-8-sig")
print("CSV_std has been created successfully at " + readAndSavePath)