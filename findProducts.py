from AliProduct import AliProduct
from time import sleep
from selenium import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.interaction import KEY
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import requests
from getProductInfo import proxiedAliLogin
from firebase import firebase
import common
import urllib.parse

class ebayResult:
    def __init__(self, numSold, avgPrice):
        self.numSold = numSold
        self.avgPrice = avgPrice


def ebaySoldResults(query):
    r = requests.get('https://www.ebay.com/sch/i.html?_from=R40&_nkw=' + query  + '&_sacat=0&LH_TitleDesc=0&rt=nc&LH_Sold=1&LH_Complete=1')
    soup = BeautifulSoup(r.text, 'html.parser')
    numSold = int(soup.select('.srp-controls__count-heading')[0].decode_contents().split()[0].replace(',',''))
    avgPrice = 0.0
    if numSold > 0:
        totalPrice = 0
        prices = soup.select('.POSITIVE')
        for price in prices:
            totalPrice += float(price.decode_contents().replace('$', ''))
        avgPrice = totalPrice / len(prices)
    return ebayResult(numSold, avgPrice)
    
def getPageURL(baseURL, queryTerm, pageNumber):
    init_id_loc = baseURL.index('&initiative_id')
    initiative_id = baseURL[init_id_loc + 14: baseURL.index('&', init_id_loc)]
    return urllib.parse.quote('https://www.aliexpress.com/wholesale?site=glo&g=y&SortType=price_asc&SearchText=' + queryTerm + '&groupsort=1&page=' + pageNumber + '&initiative_id=' + initiative_id + '&needQuery=n&isFreeShip=y')



def aliQuery(queryTerm):
    pLinkList = []
    driver, proxy, proxyDict = proxiedAliLogin()
    #driver.get("https://www.aliexpress.com")
    
    common.waitAndSendKeysCSS('#search-key', 30, driver, queryTerm)
    common.waitAndClickCSS('.search-button', 10, driver)
    # common.waitAndSendKeysCSS('#fm-login-id', 5, driver, proxyDict[proxy]['username'])
    try:
        common.waitAndSendKeysCSS('#fm-login-password', 10, driver, proxyDict[proxy]['password'])
        common.waitAndClickCSS('#login-form > div.fm-btn > button', 10, driver)
    except:
        print('no login prompted')

    driver.fullscreen_window()
    common.waitAndClickCSS('#price_lowest_1', 5, driver)
    common.waitAndClickCSS('#linkFreeShip .check-icon', 5, driver)
    searchResultsCount = int(common.waitAndTextCSS('.search-count', 5, driver).replace(',',''))
    if (searchResultsCount < 1):
        print('no results :(')
        return pLinkList
    totalPages = searchResultsCount / 20
    sleep(5)
    baseURL = driver.current_url
    nextPageNum = 1
    while nextPageNum < round(totalPages * 0.5):
        if (nextPageNum > 1):
            driver.get(getPageURL(baseURL, queryTerm, nextPageNum))
        sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        productList = soup.select('.product')
        for product in productList:
            pLinkList.append(product['href'])
        print(pLinkList)
    return pLinkList

aliQuery('hammock')   