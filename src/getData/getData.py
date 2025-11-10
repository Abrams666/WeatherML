#import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import json

#config
print("Loading configuration...")
configFile = json.load(open("./config.json", 'r', encoding='utf-8'))

stationNumber = configFile["getData"]["station number"]
startYear= configFile["getData"]["start year"]
startMonth= configFile["getData"]["start month"]
endYear= configFile["getData"]["end year"]
endMonth= configFile["getData"]["end month"]
downLoadPath = configFile["getData"]["download path"]

if(configFile["getData"]["year of today"] == "auto"):
    todayYear = int(datetime.date.today().year)
else:
    todayYear = int(configFile["getData"]["year of today"])

if(configFile["getData"]["month of today"] == "auto"):
    todayMonth = int(datetime.date.today().month)
else:
    todayMonth = int(configFile["getData"]["month of today"])

print("Station number: " + stationNumber)
print("Today's date: " + str(todayYear) + "/" + str(todayMonth))
print("Data start date: " + str(startYear) + "/" + str(startMonth))
print("Data end date: " + str(endYear) + "/" + str(endMonth))
print("Download path: " + downLoadPath)
print("-------------------------------")

#setup
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": downLoadPath,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)

today = todayYear * 12 + todayMonth
start = startYear * 12 + startMonth
end = endYear * 12 + endMonth

#open website
print("Opening website...")
driver.get('https://codis.cwa.gov.tw/StationData')
time.sleep(1)

#enter station code
print("Entering station number...")
stationInput = driver.find_element(By.CSS_SELECTOR, "input[list='station_name']")
stationInput.send_keys(stationNumber)
time.sleep(0.5)

#select station
print("Selecting station on map...")
station = driver.find_element(By.CSS_SELECTOR, ".leaflet-marker-icon.ash-icon-small")
station.click()
time.sleep(0.5)

#click view data
print("Navigating to data page...")
viewDataButton = driver.find_element(By.CSS_SELECTOR, 'button[data-stn_id='+'"'+stationNumber+'"]')
viewDataButton.click()
time.sleep(0.5)

#switch to monthly data
print("Switching to monthly data tab...")
monthlyDataTab = driver.find_element(By.CSS_SELECTOR, 'img[src="https://codis.cwa.gov.tw/Images/stn-tool/report_month.svg"]')
monthlyDataTab.click()
time.sleep(0.5)
print("-------------------------------")

#download data
print("Starting data download...")
while(1==1):
    if(today > start):
        lastPageButton = driver.find_elements(By.CSS_SELECTOR, "div[class='datetime-tool-prev-next']")
        for btn in lastPageButton:
            if(btn.text == "<"):
                btn.click()
                break
        time.sleep(0.5)
        today -= 1
    elif(today == start):
        break

while(1==1):
    downloadButton = driver.find_element(By.CSS_SELECTOR, "div[class='lightbox-tool-type-ctrl-btn']")
    driver.execute_script("arguments[0].click();", downloadButton)
    time.sleep(0.5)
    if(today % 12 == 0):
        print("Downloaded data for " + str((today // 12)-1) + "/" + str(12))
    else:
        print("Downloaded data for " + str(today // 12) + "/" + str(today % 12))

    lastPageButton = driver.find_elements(By.CSS_SELECTOR, "div[class='datetime-tool-prev-next']")
    for btn in lastPageButton:
        if(btn.text == "<"):
            btn.click()
            break
    time.sleep(0.5)

    today -= 1

    if(today < end):
        print("Download complete.")
        print("Data saved to: " + downLoadPath)
        break

#close browser
print("-------------------------------")
time.sleep(2)
print("Closing browser...")
driver.close()
print("Process complete.")