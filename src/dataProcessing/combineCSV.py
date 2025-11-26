#import
import pandas as pd
import json

#function
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
start = int(startYear) * 12 + int(startMonth)
end = int(endYear) * 12 + int(endMonth)

#create a new CSV file
print("Creating new CSV file...")
dataColumns = ["StnPres","SeaPres","StnPresMax","StnPresMin","Temperature","T Max","T Min","Td dew point","RH","RHMin","WS","WD","WSGust","WDGust","Precp","PrecpHour","PrecpMax10","PrecpMax60","SunShine","SunshineRate","GloblRad","VisbMean","EvapA","UVI Max","Cloud Amount","TxSoil0cm","TxSoil5cm","TxSoil10cm","TxSoil20cm","TxSoil30cm","TxSoil50cm","TxSoil100cm"]
dataColumnsChinese = ["測站氣壓(hPa)","海平面氣壓(hPa)","測站最高氣壓(hPa)","測站最低氣壓(hPa)","氣溫(℃)","最高氣溫(℃)","最低氣溫(℃)","露點溫度(℃)","相對溼度(%)","最小相對溼度(%)","風速(m/s)","風向(360degree)","最大瞬間風(m/s)","最大瞬間風風向(360degree)","降水量(mm)","降水時數(hour)","最大十分鐘降水量(mm)","最大六十分鐘降水量(mm)","日照時數(hour)","日照率(%)","全天空日射量(MJ/㎡)","能見度(km)","A型蒸發量(mm)","日最高紫外線指數","總雲量(0~10)","地溫0cm","地溫5cm","地溫10cm","地溫20cm","地溫30cm","地溫50cm","地溫100cm"]
data = {"StnPres": [],"SeaPres": [],"StnPresMax": [],"StnPresMin": [],"Temperature": [],"T Max": [],"T Min": [],"Td dew point": [],"RH": [],"RHMin": [],"WS": [],"WD": [],"WSGust": [],"WDGust": [],"PrecpHour": [],"PrecpMax10": [],"PrecpMax60": [],"SunShine": [],"SunshineRate": [],"GloblRad": [],"VisbMean": [],"EvapA": [],"UVI Max": [],"Cloud Amount": [],"TxSoil0cm": [],"TxSoil5cm": [],"TxSoil10cm": [],"TxSoil20cm": [],"TxSoil30cm": [],"TxSoil50cm": [],"TxSoil100cm": [],"Precp": []}

#read csv files and combine
print("Combining CSV files...")
id = 0
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
        isAllNum = True

        for j in range(len(dataColumns)):
            if(not is_number(row[dataColumnsChinese[j]])):
                isAllNum = False
                break

        if(isAllNum):
            #data["ID"].append(id)
            id += 1
            for j in range(len(dataColumns)):
                data[dataColumns[j]].append(row[dataColumnsChinese[j]])
    print("Finished reading and combining data of " + fileName + ".")
print("-------------------------------")

#save csv
print("Saving CSV file...")
df = pd.DataFrame(data)
df.to_csv(readAndSavePath + "/"+"data" + str(stationNumber) + ".csv", index=False, encoding="utf-8-sig")
print("data" + str(stationNumber) + ".csv has been created successfully at " + readAndSavePath + ".")