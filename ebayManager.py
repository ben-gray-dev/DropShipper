# -*- coding: utf-8 -*-
'''
 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''
from time import sleep
import getProductInfo
from AliProduct import AliProduct
import pprint
import json
import os
import requests
import math
import ebaysdk
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError

api = Trading(appid='BradGray-Soldi-PRD-947f2a39f-550d6605', certid='PRD-47f2a39f61ac-fb65-4c10-b1a3-fafd',
                             devid='2786f563-f132-4c58-a214-e6e93e174878',
                             warnings=False)


def getItemInfo(itemID):
    try:

        itemData = {
            "IncludeItemSpecifics": "true",
            "ItemID": itemID
        }

        response = api.execute('GetItem', itemData)
        validateResponse(response)
        return response.dict()['Item']

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def validateResponse(response):
    assert(response.dict()['Ack'] == 'Success')


def printResponse(response):
    pprint.pprint(response.dict())


def getItemFromProduct(product: AliProduct):
    
    item = {}
    with open("itemTemplate.json", "r") as f:
        item = json.load(f)
    if (product.hasColors):
        item['Item']['PictureDetails']['PictureURL'] = uploadImageToEbay(os.path.dirname(__file__) + "/" + product.preferredColor['thisColorImg'], product.imageDir)
    else:
        item['Item']['PictureDetails']['PictureURL'] = []
        for image in product.images:
            item['Item']['PictureDetails']['PictureURL'].append(uploadImageToEbay(image, product.imageDir))
    item['Item']['PrimaryCategory']['CategoryID'] = getSuggestedCategories(product.productName)
    item['Item']['Title'] = generateTitle(product.productName)
    item['Item']['Description'] = product.productName + '. Condition is New with tags.'
    item['Item']['BuyItNowPrice'] = 0.0
    item['Item']['ListingDetails']['MinimumBestOfferPrice'] = roundUpPrice(product.price * 3)
    item['Item']['ShippingDetails']['ShippingServiceOptions']['ShippingTimeMin'] = product.minDeliveryTimeDays
    item['Item']['ShippingDetails']['ShippingServiceOptions']['ShippingTimeMax'] = product.maxDeliveryTimeDays
    item['Item']['StartPrice'] = roundUpPrice(product.price * 4)
    item['Item']['ItemSpecifics']['NameValueList'] = product.itemSpecifics['NameValueList']
    return item        


def generateTitle(rawTitle):
    t = 'NWT ' + rawTitle
    t_words = t.split()
    t_final = ''
    word_ctr = 0
    while len(t_words[word_ctr] + ' ' + t_final) < 70:
        t_final += ' '
        t_final += t_words[word_ctr]
        word_ctr += 1
    return t_final


def getSuggestedCategories(query):
    newCallData = {
        'Query': query,
    }
    response = api.execute('GetSuggestedCategories', newCallData)
    rDict = response.dict()
    if (int(rDict['CategoryCount']) > 0):
        return rDict['SuggestedCategoryArray']['SuggestedCategory'][0]['Category']['CategoryID']
    else:
        return '31387'



def uploadImageToEbay(filePath, picName):
    
    try:
        files = {'file': ('EbayImage', open(filePath, 'rb'))}
        pictureData = {
            "PictureName": picName
        }
        response = api.execute('UploadSiteHostedPictures', pictureData, files=files)
        return response.dict()['SiteHostedPictureDetails']['FullURL']

    except ConnectionError as e:
        print(e)
        print(e.response.dict())

def uploadPictureFromFilesystem(filepath):

    try:

        api = Trading(appid='BradGray-Soldi-PRD-947f2a39f-550d6605', certid='PRD-47f2a39f61ac-fb65-4c10-b1a3-fafd',
                             devid='2786f563-f132-4c58-a214-e6e93e174878',
                             warnings=False)
        # pass in an open file
        # the Requests module will close the file
        files = {'file': ('EbayImage', open(filepath, 'rb'))}

        pictureData = {
            "WarningLevel": "High",
            "PictureName": "WorldLeaders"
        }

        api.execute('UploadSiteHostedPictures', pictureData, files=files)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())



def verifyAddItem(item):
    try:
        response = api.execute('VerifyAddItem', item)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())

def addItem(item):
    try:
        response = api.execute('AddItem', item)
    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def roundUpPrice(price):
    return math.ceil(price) - 0.01

if __name__ == "__main__":
    with open('aliProducts.txt', 'r', encoding = "utf-16") as f:
        for line in f:
            # try:
                print("adding aliproduct %s" % line)
                p = getProductInfo.getAliProdInfo(line)
                addItem(getItemFromProduct(p))
                sleep(120)
            # except Exception as e:
            #     print("===============================================")
            #     print("ERROR adding aliproduct: %s" % line)
            #     print(e)
            #     print("===============================================")
            #     continue
    # p = getProductInfo.getAliProdInfo('https://www.aliexpress.com/item/32889675086.html?spm=2114.search0104.3.121.500667bd65JdeT&ws_ab_test=searchweb0_0%2Csearchweb201602_3_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103%2Csearchweb201603_53%2CppcSwitch_0&algo_expid=f7517f6c-ad71-4b08-bb8a-a0b06501c97d-15&algo_pvid=f7517f6c-ad71-4b08-bb8a-a0b06501c97d')
    # #getItemFromProduct(p)
    # addItem(getItemFromProduct(p))
        
    