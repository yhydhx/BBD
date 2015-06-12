#!/usr/bin/env Python  
#encoding=utf-8

import urllib2
import time
import numpy as np
import matplotlib.pyplot as plt 

def main():
	data =init()
	showGeology(data)	

def init():
	data ={}
	address = {}
	addressFile = file('../data/address.txt')
	for element in addressFile:
		if element.strip()[-1] == "\"":
			continue
		Info = element.strip().split("######")
		if Info[1][-1] != "\"":
			address[Info[0]] = eval(Info[1])
			try:
				print address[Info[0]]['result']['location']['level']
			except:
				pass

	originFile = file("../data/cleanData.txt")
	count = 0
	errcount = 0
		
	for element in originFile:
		Info = eval(element.strip())
		
		if Info['cmpn_address'] == "":
			Info['hasAddress'] = 0
		else:
			Info['hasAddress'] = 0
			#print Info['cmpn_address']
			try:
				Info['location'] = address[Info['cmpn_address']]['result']['location']	
				Info['hasAddress'] = 1	
				count += 1
			except KeyError:
				errcount += 1
				pass
		
		data[Info['reg_num']] =Info
	print count, errcount
		 
	return data


def showGeology(data):

	liveLong = {}

	count = 0

	for key,value in data.items():
		
		if  value['cmpn_establish_date'] == "":
			continue
		registYearMonth = time.strftime('%Y%m', time.localtime(float(value['cmpn_establish_date'])))
		if value['cmpn_pass_date'] != "":
			passMonth = time.strftime('%Y%m', time.localtime(float(value['cmpn_pass_date'])))
		
		if value['hasAddress'] == 1:
			if liveLong.has_key(registYearMonth):
				liveLong[registYearMonth]['num'] +=1
				liveLong[registYearMonth]['location'].append([value['location']['lng'],value['location']['lat']])
			else:
				liveLong[registYearMonth] = {}
				liveLong[registYearMonth]['num'] = 1
				liveLong[registYearMonth]['deadNum'] =0
				liveLong[registYearMonth]['deadLocation'] = []
				liveLong[registYearMonth]['location'] = [[value['location']['lng'],value['location']['lat']]]
			if value['isDead'] == 1:
				liveLong[registYearMonth]['deadNum'] += 1
				liveLong[registYearMonth]['deadLocation'].append([value['location']['lng'],value['location']['lat']])


	date = sorted(liveLong)
	for element in date:
		if liveLong[element]['deadNum'] != 0:
			pass
			#print liveLong[element]['deadNum'] 

	dateLocationFile = file('../data/dateLocation.log','w')
	dateLocationFile.write(str(liveLong))
	dateLocationLogFile = file("../log/dateLocationLog.log",'w')
	for element in date:
		num = liveLong[element]['num']
		deadNum = liveLong[element]['deadNum']
		dateLocationLogFile.write(element+"###"+str(num)+"###"+str(deadNum)+"\n")



main()