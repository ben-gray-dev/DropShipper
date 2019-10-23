'''
Created on Jun 9, 2019

@author: Bgray
'''
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
import threading
import requests
import os
import random
import jsonpickle
import string
import pickle
import time
from datetime import datetime
import json
from bs4 import BeautifulSoup
from firebase import firebase
firebase = firebase.FirebaseApplication('https://proxypool-f3996.firebaseio.com/', None)
proxyDict = {}
proxyCookieDict = {}

def getProxiesFromDB():
    try: 
        resul = firebase.get('/proxies/value/', None)
        if (resul is not None):
            proxyDict.update(json.loads(resul)['data'])
        cookieResul = firebase.get('/proxies/cookies', None)
        if (cookieResul is not None):
            proxyCookieDict.update(jsonpickle.decode(cookieResul)['data'])
            print(proxyCookieDict)
    except:
        print('I/O error. Retrying...', flush=True)
        getProxiesFromDB()

def postProxiesToDB():
    proxyData = {'data': proxyDict}
    proxyCookieData = {'data': proxyCookieDict}
    try:
        firebase.put('/proxies/', 'value', json.dumps(proxyData))
        firebase.put('/proxies/', 'cookies', jsonpickle.encode(proxyCookieData))
    except:
        print('I/O error. Retrying...', flush=True)
        postProxiesToDB()


options = webdriver.ChromeOptions()


def scrapeProxyLists():
    r = requests.get("https://www.us-proxy.org/")
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('tr')
    for ind, row in enumerate(rows):
        try:
            rowSoup = BeautifulSoup(str(row), 'html.parser')
            tds = rowSoup.find_all('td')
            if (tds[6].decode_contents() == 'yes'):
                proxy = tds[0].decode_contents() + ":" + tds[1].decode_contents()
                if proxy not in proxyDict:
                    proxyDict[proxy] = {'failures': 0, 'username': '', 'password': ''}
                proxies.append(proxy)
            # else:
            #     print('skipping %s:%s since no https' % (tds[0].decode_contents(), tds[1].decode_contents()))
        except:
            pass
            # print("skipping row %d" % ind)

def saveProxies():
    with open("proxyList.txt", "w+") as f:
        for proxy in proxyDict.values():
            f.write("%s\n" % proxy)


def getRandProxy():
    #return proxies[random.randrange(0, len(proxies))]
    return '1.1.1.1:3300'

proxy = getRandProxy()
options.add_argument("--headless")
options.add_argument("--log-level=3")
threadList = []


def getRandomString(stringLength):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def proxiedAliLogin():
    myProxy = ''
    getProxiesFromDB()
    scrapeProxyLists()
    print(proxyDict)
    print(proxyCookieDict)
    successfulProxy = False
    for proxy in list(proxyCookieDict.keys()) + list(proxyDict.keys()):
        print(proxy)
        if successfulProxy:
            break
        myProxy = proxy
        options.add_argument('--proxy-server=%s' % proxy)
        driver = webdriver.Chrome(chrome_options=options,executable_path="chromedriver.exe")
        driver.get("https://www.aliexpress.com")
        print("starting proxy: %s" % proxy)
        try:
            waitAndClickCSS('body > div.ui-window.ui-window-normal.ui-window-transition.ui-newuser-layer-dialog > div > div > a', 5, driver)
        except:
            print('no popup')
        if proxy not in proxyCookieDict.keys():
            print("login first!")
            emailName = ''
            passwordStr = ''
            try:
                waitAndClickCSS('span.join-btn > a', 60, driver) 
                emailName = getRandomString(12)
                waitAndSendKeys('//*[@id="ws-xman-register-email"]', 30, driver, '%s@gmail.com' % emailName)
                passwordStr = getRandomString(10)
                waitAndSendKeys('//*[@id="ws-xman-register-password"]', 30, driver, passwordStr)
                waitAndClickCSS('#ws-xman-register-submit', 30, driver)
                sleep(10)
            except:
                print('error with proxy: %s' % proxy)
                proxyDict[proxy]['failures'] += 1
                driver.quit()
                continue
            proxyDict[proxy]['username'] = emailName
            proxyDict[proxy]['password'] = passwordStr
            proxyCookieDict[proxy] = pickle.dumps(driver.get_cookies())
        # try:
        #     waitAndTextCSS('body > div.ui-window.ui-window-normal.ui-window-transition.ui-newuser-layer-dialog > div > div > a', 5, driver)
        # except:
        #     proxyDict[proxy]['failures'] += 1
        #     driver.quit()
        #     continue
        successfulProxy = True
        for c in pickle.loads(proxyCookieDict[proxy]):
            try:
                driver.add_cookie(c)
                print('working cookie!')
            except:
                print('error with proxy: %s' % proxy)
                proxyDict[proxy]['failures'] += 1
                driver.quit()
                successfulProxy = False
                break
        if not successfulProxy:
            continue
        postProxiesToDB()
        
    return (driver, myProxy, proxyDict)
 


def getAliProdInfo(url, driver=None):
    if driver is None:
        driver = webdriver.Chrome(chrome_options=options,executable_path='chromedriver.exe')
    prodDeliveryEstimate = "undefined"
    prodNumOrders = -1
    prodReviewScore = 0.0
    prodReviewNum = 0
    colorInfo = {}
    itemSpecs = {}
    urlFilenameDict = {}
    itemSpecs['ItemSpecifics'] = {}
    itemSpecs['ItemSpecifics']['NameValueList'] = []
    hasColors = False
    preferredColor = {}
    today = datetime.today()
    driver.get(url)
    try:
        waitAndClickCSS('body > div.next-overlay-wrapper.opened > div.next-overlay-inner.next-dialog-container > div > a', 5, driver)
    except:
        print('no popup')
    shippingOpts = driver.find_elements_by_css_selector('#root > div > div.product-main > div > div.product-info > div.product-sku > div > div:nth-child(2) > ul > li > div')
    if (len(shippingOpts) > 1):
        waitAndClickCSS('#root > div > div.product-main > div > div.product-info > div.product-sku > div > div:nth-child(2) > ul > li > div > span', 30, driver)
    elemList = driver.find_elements_by_css_selector('#j-image-thumb-list span img')
    if (len(elemList) == 0):
        elemList = driver.find_elements_by_css_selector('#root > div > div.product-main > div > div.img-view-wrap > div > div > div.images-view-wrap > ul div img')
    fURL = elemList[0].get_attribute('src')
    imageDir = fURL[57:fURL.index('.jpg')]
    
     #prodName = waitAndTextCSS('.product-name', 5, driver)
    prodName = waitAndTextCSS('.product-title', 5, driver)

    #prodPrice = waitAndTextCSS('#j-sku-price', 30, driver)
    prodPrice = getPriceFromString(waitAndTextCSS('.product-price-value', 5, driver))

    #prodShippingPrice = waitAndTextCSS('.logistics-cost', 30, driver)
    prodShippingPrice = waitAndTextCSS('.product-shipping-price', 5, driver)

    #prodShippingService = waitAndTextCSS('.shipping-link', 30, driver)
    prodShippingService = waitAndTextCSS('.product-shipping-info', 5, driver)

    try:
        #prodReviewScore = waitAndTextCSS('.percent-num', 30, driver)
        prodReviewScore = waitAndTextCSS('.overview-rating-average', 5, driver)
        
        #prodReviewNum = waitAndTextCSS('.rantings-num', 30, driver)
        prodReviewNum = waitAndTextCSS('.product-reviewer-reviews', 5, driver)
        if (len(prodReviewNum) > 0):
            prodReviewNum = prodReviewNum.split()[0][1:]  
    except:
        print('no reviews')
    
    try:
        os.mkdir(imageDir)
    except:
        print("already exists")


    colorOpts = driver.find_elements_by_css_selector('.sku-title')
    if (len(colorOpts) > 0):
        runningTotalPrice = 0.0
        numColors = 0
        hasColors = True
        waitAndClickCSS('.sku-property-image img', 5, driver)
        colorName = waitAndTextCSS('.sku-title-value', 5, driver)
        itemSpecs['Color'] = colorName
        colorChoices = driver.find_elements_by_css_selector('.sku-property-image img')
        print(len(colorChoices))
        for ind, color in enumerate(colorChoices):
            if (ind != 0):
                color.click()
            thisColorName = waitAndTextCSS('.sku-title-value', 5, driver)  
            
            thisColorPrice = waitAndTextCSS('.product-price-value', 5, driver)
            tipVal = waitAndTextCSS('.product-quantity-tip span',5,driver).split()[0]
            if (tipVal == 'Only'):
                continue
            colorInfo[thisColorName] = {}
            colorInfo[thisColorName]['numLeft'] = int(waitAndTextCSS('.product-quantity-tip span',5,driver).split()[0])
            rawURL = driver.find_element_by_css_selector('#root > div > div.product-main > div > div.img-view-wrap > div > div > div.image-view-magnifier-wrap > img').get_attribute('src')
            filename = imageDir + "/" + prodName + "-" + thisColorName
            savePicToFile(rawURL, filename)
            colorInfo[thisColorName]['thisColorImg'] = filename
            colorInfo[thisColorName]['price'] = getPriceFromString(thisColorPrice)
            runningTotalPrice += colorInfo[thisColorName]['price']
            numColors += 1
        
        cheapest_color_choice = min(colorInfo.keys(), key=(lambda k: colorInfo[k]['price']))
        print(cheapest_color_choice)
        if (colorInfo[cheapest_color_choice]['price'] < 0.9 * (runningTotalPrice/numColors)):
            del colorInfo[cheapest_color_choice]
        most_popular_color_choice = min(colorInfo.keys(), key=(lambda k: colorInfo[k]['numLeft']))
        preferredColor = colorInfo[most_popular_color_choice]
        preferredColor['colorName'] = most_popular_color_choice
   

    prodDeliveryEstimate = waitAndTextCSS('.product-shipping-delivery span',5,driver)
    prodDeliveryEstimate = list(map(int, prodDeliveryEstimate.split('/')))
    if prodDeliveryEstimate[0] < today.month:
        deliveryDate = datetime(today.year + 1, prodDeliveryEstimate[0], prodDeliveryEstimate[0])
    else:
        deliveryDate = datetime(today.year, prodDeliveryEstimate[0], prodDeliveryEstimate[0])
    prodMaxDeliveryTimeDays = (deliveryDate - today).days
    prodMinDeliveryTimeDays = prodMaxDeliveryTimeDays - 7
    try:
        #prodNumOrders = waitAndTextCSS('#j-order-num', 30, driver)
        prodNumOrders = waitAndTextCSS('.product-reviewer-sold', 5, driver)
        if (len(prodNumOrders) > 0):
            prodNumOrders = prodNumOrders.split()[0] 
    except:
        print('no prod num orders')

    
    
    images = set()
    for ind, e in enumerate(elemList):
        imageURL = e.get_attribute('src')
        images.add(imageDir + "/" + imageDir.split('-')[0] + '-' + str(ind) + ".jpg")
        savePicToFile(imageURL[:imageURL.index('_50')], imageDir + "/" + imageDir.split('-')[0] + '-' + str(ind) + ".jpg")
    actionChain = webdriver.ActionChains(driver)
    actionChain.send_keys(Keys.SPACE).perform()
    waitAndClickCSS('#product-detail > div.product-detail-tab > div > div.detail-tab-bar > ul > li:nth-child(3) > div > span', 10, driver)
    
    itemSpecsElems = driver.find_elements_by_css_selector('.product-prop')
    if (len(itemSpecsElems) == 0):
        print("no specs")
    else:
        for itemElem in itemSpecsElems:
            title = itemElem.find_element_by_css_selector('.property-title').text
            title = title[:title.index(':')].replace('&', '')
            if (title not in itemSpecs):
                itemSpecs[title] = itemElem.find_element_by_css_selector('.property-desc').text
                itemSpecs['ItemSpecifics']['NameValueList'].append({"Name": title, "Value": itemElem.find_element_by_css_selector('.property-desc').text.replace('&', '') })

    driver.quit()
    return AliProduct(prodName, hasColors, images, imageDir, prodPrice, prodShippingPrice, prodShippingService, prodDeliveryEstimate, prodMaxDeliveryTimeDays, prodMinDeliveryTimeDays, prodReviewScore, prodReviewNum, prodNumOrders, itemSpecs['ItemSpecifics'], colorInfo, preferredColor)




def getPriceFromString(priceStr):
    priceNameList = priceStr.strip().split()
    return float(priceNameList[len(priceNameList) - 1].replace('$',''))

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

def waitAndTextCSS(css_selector, timeout, driver):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
    finally:
        return element.text
        
def savePicToFile(picURL, filename):
    pic_r = requests.get(picURL)
    if (pic_r.status_code != 200):
        print("error: picture does not exist!")
        return -1 
    with open(filename, "wb+") as f:
        f.write(pic_r.content)

# for proxy in proxies:
#     threadList.append(threading.Thread(target=getAliProdInfo, args = (proxy, 'https://www.aliexpress.com/item/32890025580.html?spm=a2g0o.productlist.0.0.7cda67bdNmwO33&algo_pvid=0725aed4-e4a2-4530-b795-5e09456ae942&algo_expid=0725aed4-e4a2-4530-b795-5e09456ae942-12&btsid=182cff63-a588-48e6-96ec-151b65dd82cc&ws_ab_test=searchweb0_0%2Csearchweb201602_4%2Csearchweb201603_52')))
#     threadList.pop().start()

# if __name__ == '__main__':
    # getProxiesFromDB()
    # scrapeProxyLists()
    # postProxiesToDB()
    # driver = webdriver.Chrome(chrome_options=options,executable_path="chromedriver.exe")
    
    #driver.get('https://www.aliexpress.com')
    #getAliProdInfo(driver, 'https://www.aliexpress.com/item/Luxury-Women-Watches-Magnetic-Starry-Sky-Female-Clock-Quartz-Wristwatch-Fashion-Ladies-Wrist-Watch-reloj-mujer/32968577325.html?spm=2114.search0104.3.1.3fc967bd4Dqp18&ws_ab_test=searchweb0_0,searchweb201602_3_10065_10130_10068_10890_10547_319_10546_317_10548_10545_10696_453_10084_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_53,ppcSwitch_0&algo_expid=40a38e8b-dda1-4af1-a4d0-fc00d4ec1897-0&algo_pvid=40a38e8b-dda1-4af1-a4d0-fc00d4ec1897')
    #p = getAliProdInfo(driver, 'https://www.aliexpress.com/item/Men-Sport-LED-Watches-Men-s-Digital-Watch-Men-Watch-Silicone-Electronic-Watch-Men-Clock-reloj/32914540611.html?spm=2114.search0104.3.9.165467bdwzCFFF&ws_ab_test=searchweb0_0,searchweb201602_3_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_53,ppcSwitch_0&algo_expid=7390a65f-2daa-4ddb-825e-26130f84a936-1&algo_pvid=7390a65f-2daa-4ddb-825e-26130f84a936')
    #p = getAliProdInfo(driver, 'https://www.aliexpress.com/item/33016438300.html?spm=2114.search0104.3.36.298367bdBLy6pE&ws_ab_test=searchweb0_0,searchweb201602_3_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_53,ppcSwitch_0&algo_expid=b7430a35-c2e7-416c-8cba-67336d7c7ad9-4&algo_pvid=b7430a35-c2e7-416c-8cba-67336d7c7ad9')
    # p = getAliProdInfo('https://www.aliexpress.com/item/32889675086.html?spm=2114.search0104.3.121.500667bd65JdeT&ws_ab_test=searchweb0_0%2Csearchweb201602_3_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103%2Csearchweb201603_53%2CppcSwitch_0&algo_expid=f7517f6c-ad71-4b08-bb8a-a0b06501c97d-15&algo_pvid=f7517f6c-ad71-4b08-bb8a-a0b06501c97d')
    # p.printProduct()