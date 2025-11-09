#import
from selenium import webdriver
import time

#config
driver = webdriver.Chrome()

#open website
driver.get('https://codis.cwa.gov.tw/StationData')
time.sleep(2)

#close browser
driver.close()