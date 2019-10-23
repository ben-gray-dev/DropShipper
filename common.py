from selenium import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.interaction import KEY
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
def waitAndClickCSS(css_selector, timeout, driver):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
    finally:
        element.click()

def waitAndClick(xPath, timeout, driver):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xPath))
        )
    finally:
        element.click()
        
def waitAndSendKeys(xPath, timeout, driver, keysToSend):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xPath))
        )
    finally:
        element.send_keys(keysToSend)

def waitAndSendKeysCSS(css_selector, timeout, driver, keysToSend):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
    finally:
        element.send_keys(keysToSend)
        

def waitAndTextCSS(css_selector, timeout, driver):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
    finally:
        return element.text