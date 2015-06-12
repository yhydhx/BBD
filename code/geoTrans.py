#!/usr/bin/env Python  
#encoding=utf-8

import urllib2
import time
import numpy as np
import matplotlib.pyplot as plt 

def main():
	#data = init()
	#getLocation(data)
	address = initData()
	#cities = process(data)

	getCompanyNumberInEachCity(address)


def getCompanyNumberInEachCity(address):
	data ={}
	cmpNumInCity  = {}
	originFile = file("../data/cleanData.txt")
	for element in originFile:
		Info = eval(element.strip())
		data[Info['reg_num']] =Info
	
	for key,value in data.items():
		if value['cmpn_address'] == "":
			continue
		try:
			singleCity = address[value['cmpn_address']]['result']['addressComponent']['city']
			singleDistrict = address[value['cmpn_address']]['result']['addressComponent']['district']
		except:
			print value['cmpn_address'].decode('utf8')
		if singleCity != "":

			if cmpNumInCity.has_key(singleCity):
				cmpNumInCity[singleCity] += 1
			else:
				cmpNumInCity[singleCity] = 1

			if singleCity == "成都市":
				print "a"
				
				if cmpNumInCity.has_key(singleDistrict):
					cmpNumInCity[singleDistrict] += 1
				else:
					cmpNumInCity[singleDistrict] = 1
				

	for key,value in cmpNumInCity.items():
		if value > 10:
			print key.decode('utf8'),value



def process(data):
	cities = {}
	for key,value in data.items():
		singleCity = value['result']['addressComponent']['city']
		if cities.has_key(singleCity):
			cities[singleCity] += 1
		else:
			cities[singleCity] = 1
	return cities

def init():
	originAddressFile = file("../data/address.txt")
	address = {}
	for element in originAddressFile:
		Info = element.strip().split("######")
		try:
			address[Info[0]] = eval(Info[1])
		except:
			pass
	return address


def initData():
	originAddressFile = file("../data/addressWithDistrict.txt")
	address = {}
	for element in originAddressFile:
		Info = element.strip().split("######")
		try:
			address[Info[0]] = eval(Info[2])
		except:
			pass
	return address


def getLocation(data):
	errorLog = file("getDistrictLog.log",'w')
	addressFile = file("../data/addressWithDistrict.txt",'w')
	count = 0
	for key,value in data.items():
		count += 1
		if count % 100 == 0:
			print count
		try:
			location = getLocationSpider(value['result']['location']['lng'],value['result']['location']['lat'])
			#print location
			addressFile.write(key+"######"+str((value['result']['location']['lng'],value['result']['location']['lat']))+"######"+location+"\n")

		except:
			errorLog.write(key+"\n")
		
		

def getLocationSpider(log,lat):
	url = "http://api.map.baidu.com/geocoder/v2/?ak=XfCR6LMCt99qehhiCGzmlLEd&callback=renderReverse&location="+str(lat)+","+str(log)+"&output=json&pois=1"
	response = urllib2.urlopen(url, timeout=10)
	responseAddress = response.read()#[27:-1]
	return responseAddress[29:-1]


main()