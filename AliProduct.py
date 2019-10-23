'''
Created on Jun 9, 2019

@author: Bgray
'''
class AliProduct:
    def __init__(self, productName, hasColors, images, imageDir, price, shippingPrice, shippingService, deliveryEst, maxDeliveryTimeDays, minDeliveryTimeDays, reviewScore, reviewNum, numOrders, itemSpecifics, colorOptions, preferredColor ):
        self.productName = productName
        self.hasColors = hasColors
        self.images = images
        self.imageDir = imageDir
        self.price = price
        self.shippingPrice = shippingPrice
        self.shippingService = shippingService
        self.deliveryEst = deliveryEst
        self.maxDeliveryTimeDays = maxDeliveryTimeDays
        self.minDeliveryTimeDays = minDeliveryTimeDays
        self.reviewScore = reviewScore
        self.numOrders = numOrders
        self.itemSpecifics = itemSpecifics
        self.colorOptions = colorOptions
        self.preferredColor = preferredColor

    def get_name(self):
        return self.name


    def get_images(self):
        return self.images


    def get_price(self):
        return self.price


    def get_shipping_price(self):
        return self.shippingPrice


    def get_shipping_service(self):
        return self.shippingService


    def get_review_score(self):
        return self.reviewScore


    def get_num_orders(self):
        return self.numOrders


    def set_name(self, value):
        self.name = value


    def set_images(self, value):
        self.images = value


    def set_price(self, value):
        self.price = value


    def set_shipping_price(self, value):
        self.shippingPrice = value


    def set_shipping_service(self, value):
        self.shippingService = value


    def set_review_score(self, value):
        self.reviewScore = value


    def set_num_orders(self, value):
        self.numOrders = value
    
    def printProduct(self):
        print(self.productName)
        print(self.hasColors)
        print(self.images)
        print(self.imageDir)
        print(self.price)
        print(self.shippingPrice)
        print(self.shippingService) 
        print(self.deliveryEst)
        print(self.maxDeliveryTimeDays)
        print(self.minDeliveryTimeDays)
        print(self.reviewScore)
        print(self.numOrders)
        print(self.itemSpecifics)
        print(self.colorOptions) 
        print(self.preferredColor)