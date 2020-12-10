import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from db import Report

PATH = '/usr/local/bin/chromedriver'
url = 'https://www.booking.com/city/fi/helsinki.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaEiIAQGYAQm4AQfIAQzYAQHoAQGIAgGoAgO4Aveuvv4FwAIB0gIkMWZkODFkYTYtY2M5Yy00N2E1LTlhNGItNmQ0YjZmZjkxYTFk2AIF4AIB;sid=d2a36dfc62f9e56716f35a50ec9c0d1d;breadcrumb=searchresults_irene;srpvid=76826ad4b0170334&'

## Get today date and 1 day after
dt = datetime.now()

## Set up for checkin field
checkin_monthyear_input = f'{dt.strftime("%B")} {dt.strftime("%Y")}'
checkin_date_input = f'{dt.day}, {dt.strftime("%A")}'

driver = webdriver.Chrome(PATH)
page_urls = []

## Open browser to Booking search page
driver.get(url)
driver.maximize_window()

## Choose checkin month
try:
  wait = WebDriverWait(driver, 5)
  elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#frm > div.xp__fieldset.js--sb-fieldset.accommodation > div.xp__dates.xp__group > div.xp__dates-inner > div:nth-child(2) > div > div > div > div > div.sb-date-field__controls.sb-date-field__controls__ie-fix > div.sb-date-field__select.-month-year.js-date-field__part > select[class*='sb-date-field__select-field js-date-field__select'] option")))
  for option in elements:
    if(option.text == checkin_monthyear_input):
      option.click()
      break
except:  
  driver.quit()

## Choose checkin day
try:
  wait = WebDriverWait(driver, 5)
  elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#frm > div.xp__fieldset.js--sb-fieldset.accommodation > div.xp__dates.xp__group > div.xp__dates-inner > div:nth-child(2) > div > div > div > div > div.sb-date-field__controls.sb-date-field__controls__ie-fix > div.sb-date-field__select.-day.js-date-field__part > select[class*='sb-date-field__select-field js-date-field__select'] option")))
  for option in elements:
    if(option.text == checkin_date_input):
      option.click()
      break
except:
  driver.quit()

time.sleep(2)

## Submit search form
submit_button = driver.find_element_by_class_name("sb-searchbox__button")
submit_button.click()

## Choose hotels filter
try:
  wait = WebDriverWait(driver, 10)
  elements = wait.until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, "Hotels")))
  for option in elements:
    if(re.search(r'^[^\s]+\s\d+', option.text)):
      link = option.get_attribute("href")
      time.sleep(2)
      driver.get(link)
      break
except:
  driver.quit()

## Find all url pages
try:
  wait = WebDriverWait(driver, 10)
  container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "bui-pagination__pages")))
  pages = container.find_elements_by_tag_name("a")
  for link in pages:
    page_urls.append(link.get_attribute("href"))
except:
  driver.quit()

## Loop through pages
for page_url in page_urls:
  driver.get(page_url)

  ## Find all hotels
  try:
    wait = WebDriverWait(driver, 10)

    ## Find container of all hotels
    container = wait.until(EC.presence_of_element_located((By.ID, "hotellist_inner")))

    ## Find hotel info containers
    hotel_containers = container.find_elements_by_class_name("sr_item_content")
    for hotel_container in hotel_containers:

      ## Find hotel name
      hotel_name = hotel_container.find_element_by_class_name("sr-hotel__name").text.strip()

      ## Find room name
      room_container = hotel_container.find_element_by_class_name("room_link")
      room_name = room_container.find_element_by_tag_name("strong").text.strip()

      ## Find room price
      room_price = hotel_container.find_element_by_class_name("bui-price-display__value")
      price_original = ''.join(e for e in room_price.text.strip() if e.isalnum())
      price_int = int(price_original)

      ## Insert into DB
      hotel = Report(hotel_name=hotel_name, room_name=room_name, room_price=price_int)
      hotel.add()
  except:
    driver.quit()