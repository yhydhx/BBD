#!/usr/bin/env Python  
#encoding=utf-8

import urllib2
import time
import numpy as np
import matplotlib.pyplot as plt 

def main():
	data =init()
	secondClean(data)
	#showGeology(data)	

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
	return data

def secondClean(data):
	outputFile = file("../data/secondCleanData.dat",'w')
	featureFile = file("../data/featureFile.dat",'w')
	for key,value in data.items():
		data[key] = getLeaderAndManagerInfo(value)
		data[key] = formatRegistMoney(value)
		outputFile.write(str(data[key])+'\n')
		featureFile.write(format(value)+"\n")


def format(data):
	outputList = []
	outputList.append(data['reg_num'])
	outputList.append(data['leader_nature_num'] )
	outputList.append(data['leader_company_num'] )
	outputList.append(data['directorNum'] )
	outputList.append(data['executiveNum'] )
	outputList.append(data['supervisorNum'])
	outputList.append(data['leaderNum'])
	outputList.append(data['beianNum'])
	outputList.append(data['duplicateLeaderNatureAndDirectorProperty'])
	outputList.append(data['duplicateDirectorAndExecutiveProperty'] )
	outputList.append(data['duplicateLeaderNatureAndexExecutiveProperty'] )
	if data['isDead'] == 1:
		try:
			outputList.append(float(data['aliveTime'])/3600/24)
		except:
			outputList.append(-1)
	else:
		outputList.append(-1)
	outputList.append(data['format_regist_money'])
	outputList.append(data['leader_nature_entropy'] )
	outputList.append(data['leader_company_entropy'] )
	outputList.append(data['leader_nature_biggest'] )
	outputList.append(data['leader_company_biggest'] )
	for i in range(len(outputList)):
		outputList[i] = str(outputList[i])
	return "\t".join(outputList)
	


#################################
##@input single data
##get the leader_nature leader_company director executive supervisor  biggestNatureLeader
##get the duplicate Info between the (leader_nature and director) (leader_nature and executive) (director and executive)
##compute the entropy 
##@output formatted single data
#################################
def getLeaderAndManagerInfo(data):
	managers = data['beian']
	leaders = data['leader']
	leader_nature_num = 0
	leader_company_num = 0
	directorNum = 0
	executiveNum = 0
	supervisorNum = 0
	biggestNatureLeader = 0
	leader_nature = []
	leader_company = []
	leader_nature_money = []
	leader_company_money = []
	director = []
	executive = []
	supervisor = []
	duplicateDirectorAndExecutiveNum = 0
	duplicateLeaderNatureAndDirectorNum = 0
	duplicateLeaderNatureAndexExecutiveNum = 0
	duplicateDirectorAndExecutiveProperty = 0
	duplicateLeaderNatureAndDirectorProperty = 0
	duplicateLeaderNatureAndexExecutiveProperty = 0
	for key,value in leaders.items():
		leaderType = value['reg_leader_type']
		if value['reg_real_pay'].strip() != "":
			singlePaid = float(value['reg_real_pay'].strip())
		else:
			singlePaid = 0.0
		if leaderType == "自然人" or leaderType == "自然人股东" or leaderType == "非农民自然人" or leaderType == "农民自然人" or leaderType == "外籍自然人" :
			leader_nature_num += 1
			leader_nature.append(value['reg_leader'])
			leader_nature_money.append(singlePaid)			
		else :
			leader_company_num += 1
			leader_company.append(value['reg_leader'])
			leader_company_money.append(singlePaid)

	for key,value in managers.items():
		managerType = value['reg_duty'].strip().split("兼")
		#check the duplicate in 
		directorFlag = 0
		executiveFlag = 0
		for singleType in managerType:
			if singleType == "":
				continue
			if singleType == "董事长" or singleType == "副董事长" or singleType == "董事" or singleType == "执行董事" :
				director.append(value['reg_person_name'])
				directorNum += 1
				directorFlag = 1
			elif singleType == "监事":
				supervisor.append(value['reg_person_name'])
				supervisorNum += 1
			else:
				executive.append(value['reg_person_name'])
				executiveNum  += 1
				executiveFlag = 1
			if executiveFlag == 1 and directorFlag ==1:
				duplicateDirectorAndExecutiveNum += 1

	'''Get the duplicate '''
	if (len(director)+len(executive)) == 0:
		duplicateDirectorAndExecutiveProperty = -1
	else:
		duplicateDirectorAndExecutiveProperty = float(duplicateDirectorAndExecutiveNum)/(len(director)+len(executive))
	(duplicateLeaderNatureAndDirectorProperty,duplicateLeaderNatureAndexExecutiveProperty) = getTheDuplicate(leader_nature,director,executive)

	"""Compute entropy"""

	'''save the info'''
	
	leader_nature_entropy = getEntropy(leader_nature_money)
	leader_company_entropy = getEntropy(leader_company_money)
	leader_nature_biggest = getMaxLeader(leader_nature_money)
	leader_company_biggest = getMaxLeader(leader_company_money)
	
	data['leader_nature_num'] = leader_nature_num
	data['leader_company_num'] = leader_company_num
	data['leader_nature_entropy'] = leader_nature_entropy
	data['leader_company_entropy'] = leader_company_entropy
	data['leader_nature_biggest'] = leader_nature_biggest
	data['leader_company_biggest'] = leader_company_biggest
	data['directorNum'] = directorNum
	data['executiveNum'] = executiveNum
	data['supervisorNum'] = supervisorNum
	data['duplicateDirectorAndExecutiveProperty'] = duplicateDirectorAndExecutiveProperty
	data['duplicateLeaderNatureAndDirectorProperty'] = duplicateLeaderNatureAndDirectorProperty
	data['duplicateLeaderNatureAndexExecutiveProperty'] = duplicateLeaderNatureAndexExecutiveProperty

	return data

def getMaxLeader(realPaidList):

	if realPaidList == [] or sum(realPaidList) == 0:
		return 0.0
	else:

		return float(max(realPaidList))/sum(realPaidList)

def getEntropy(realPaidList):

	if len(realPaidList) == 0 or sum(realPaidList) == 0:
		return -1 

	if len(realPaidList) == 1:
		return 1
	realPaid = []
	for eachPay in realPaidList:
		if eachPay != 0:
			realPaid.append(eachPay)
	realPaid = np.array(realPaid)
	#print realPaidList

	paidList = realPaid / float(sum(realPaid))
	
	result = -sum(np.log2(paidList)*paidList)

	return result

def getTheDuplicate(leader_nature,director,executive):
	'''
		Find the duplicate between the third body
	'''
	leader_nature_number = len(list(set(leader_nature)))
	directorNum = len(list(set(director)))
	executiveNum = len(list(set(executive)))
	leader_nature_director_num = len(list(set(leader_nature+director)))
	leader_nature_executive_num = len(list(set(leader_nature+executive)))
	if leader_nature_director_num == 0:
		duplicateLeaderNatureAndDirectorProperty = -1
	else:
		duplicateLeaderNatureAndDirectorProperty =  float(leader_nature_number + directorNum - leader_nature_director_num)/leader_nature_director_num
	if leader_nature_executive_num == 0:
		duplicateLeaderNatureAndexExecutiveProperty = -1
	else:
		duplicateLeaderNatureAndexExecutiveProperty =   float(leader_nature_number + executiveNum - leader_nature_executive_num)/leader_nature_executive_num

	return (duplicateLeaderNatureAndDirectorProperty,duplicateLeaderNatureAndexExecutiveProperty)


#################################
##@input single data
##
##@output formatted single data
#################################

def formatRegistMoney(data):
	dollar2yuan = 6.1428
	if data['cmpn_register_finacial'] != "":
		singleMoney  =  data['cmpn_register_finacial'].split("万")[0].strip()
		#print len(singleMoney)
		#print singleMoney
		while not singleMoney[-1] in "1234567890":
			singleMoney = singleMoney[:-1]
			#print len(singleMoney)
		if "美" in data['cmpn_register_finacial']:
			singleCompanyMoney = float(singleMoney) * dollar2yuan
		else:
			singleCompanyMoney = float(singleMoney)
	else:
		singleCompanyMoney = 0.0
	data['format_regist_money'] = singleCompanyMoney
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