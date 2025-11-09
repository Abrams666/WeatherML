#import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

#config
stationNumber = "467050"                                        #測站代碼(新屋)
todayYear = int(datetime.date.today().year)                     #今年(自動獲取)
todayMonth = int(datetime.date.today().month)                   #本月(自動獲取)
startYear= 2025                                                 #資料開始年
startMonth= 10                                                  #資料開始月
endYear= 2013                                                   #資料開始年
endMonth= 7                                                     #資料開始月
downLoadPath = r"D:\School\#課程\計算機概論\專題\程式\data"       #下載路徑

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
driver.get('https://codis.cwa.gov.tw/StationData')
time.sleep(1)

#enter station code
stationInput = driver.find_element(By.CSS_SELECTOR, "input[list='station_name']")
stationInput.send_keys(stationNumber)
time.sleep(0.5)

#select station
station = driver.find_element(By.CSS_SELECTOR, ".leaflet-marker-icon.ash-icon-small")
station.click()
time.sleep(0.5)

#click view data
viewDataButton = driver.find_element(By.CSS_SELECTOR, 'button[data-stn_id='+'"'+stationNumber+'"]')
viewDataButton.click()
time.sleep(0.5)

#switch to monthly data
monthlyDataTab = driver.find_element(By.CSS_SELECTOR, 'img[src="https://codis.cwa.gov.tw/Images/stn-tool/report_month.svg"]')
monthlyDataTab.click()
time.sleep(0.5)

#download data
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
        break

#close browser
time.sleep(2)
driver.close()