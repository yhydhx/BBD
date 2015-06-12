#!/usr/bin/env Python  
#encoding=utf-8

import urllib2
import time
import numpy as np
import matplotlib.pyplot as plt 
from scipy.stats import spearmanr
from scipy.stats import pearsonr
from scipy.stats import kendalltau



def main():
	#data =init()
	#computeYearNum(data)
	#computeLeaderAndManagerInfo(data)
	#computeDuplicatePropertyAndAliveTime(data)
	#getAdress(data)
	print getBirthRate('../log/dateLocationLog.log')

def init():
	data ={}
	originFile = file("../data/cleanData.txt")
	for element in originFile:
		Info = eval(element.strip())
		data[Info['reg_num']] =Info
	return data


def getAdress(data):
	addressFile = file("../data/address.txt" ,'w')
	errorAddressFile = file("../data/errorAddress.log",'w')
	address = {}
	for key,value in data.items():
		singleAdress = value['cmpn_address']
		if singleAdress == "":
			continue
		if address.has_key(singleAdress):
			address[singleAdress] += 1
		else:
			address[singleAdress] = 1
	for key,value in address.items():
		if value > 1:
			print key,value
		try:
			response = urllib2.urlopen('http://api.map.baidu.com/geocoder/v2/?address='+key+'&output=json&ak=XfCR6LMCt99qehhiCGzmlLEd&callback=showLocation', timeout=10)
			responseAddress = response.read()[27:-1]
			addressFile.write(key+"######"+responseAddress+"\n")
		except:
			errorAddressFile.write(key+"\n")



def computeDuplicatePropertyAndAliveTime(data):
	liveLong = {}

	count = 0
	duplicate2liveTime = []
	for key,value in data.items():
		
		if  value['cmpn_establish_date'] == "":
			continue
		registYear = time.strftime('%Y%m', time.localtime(float(value['cmpn_establish_date'])))
		if value['cmpn_pass_date'] != "":
			passMonth = time.strftime('%Y%m', time.localtime(float(value['cmpn_pass_date'])))
		if value['isDead'] == 1:
			if value['cmpn_pass_date'] == "":
				continue
			if 	value['aliveTime'] != 0:
				if liveLong.has_key(value['aliveTime']):
					liveLong[value['aliveTime']] += 1
				else:
					liveLong[value['aliveTime']] = 1
		# find the author duplicate
		
		if value['beian'] != {} and value['leader'] != {}:
 			(intersectionLength,unitLength) = getDuplicatePersonRate(value)
 			#print (intersectionLength,unitLength)
 			singleDuplitcatePropertion = float(intersectionLength)/unitLength
			if value.has_key('aliveTime'):
				if value['aliveTime']> 0:
					duplicate2liveTime.append([singleDuplitcatePropertion,value['aliveTime']])


	duplicate2liveTimeDetail = {}
	for key,value in duplicate2liveTime:
		duplicateDetail = int(key/0.2)
		if duplicate2liveTimeDetail.has_key(duplicateDetail):
			duplicate2liveTimeDetail[duplicateDetail].append(value/60/60/24/30)
		else:
			duplicate2liveTimeDetail[duplicateDetail] = [value/60/60/24/30]
	
	duplicate2liveTimeValue = []
	for key,value in duplicate2liveTimeDetail.items():
		mean = np.array(value).mean()
		std = np.array(value).std()
		duplicate2liveTimeValue.append([key,mean,std])



	drawDuplicate2AliveTimeProperty(duplicate2liveTimeValue,duplicate2liveTime)



def drawDuplicate2AliveTimeProperty(data,data2):
	title = "colapping and livetime(chengdu)"
	xlabel = "collaping "
	ylabel = "live time"

	collapingList = []
	duplicate2liveTimeMeanList = []
	duplicate2liveTimeStdList = []
	yearRange = {}
	logFile = file("../log/"+title+'.log','w')
	for singleCollap,singleMean,singleStd in data:
		singleMean = int(singleMean);
		if singleMean < 0:
			singleMean = 0
		collapingList.append(singleCollap)
		duplicate2liveTimeMeanList.append(singleMean)
		duplicate2liveTimeStdList.append(singleStd)
		logFile.write(str(singleCollap)+"\t"+str(singleMean)+"\t"+str(singleStd)+"\n")

	a = []
	b = []
	for singleCo,singleTime in data2:
		a.append(singleCo*5)
		b.append(singleTime/60/60/24/30)

	l = plt.plot(a,b,'yo')


	
	'''
	for key in sortedYear:
		company_year.append(np.log(key))
		company_year_number.append(yearRange[key])
		logFile.write(str(key)+"\t"+str(yearRange[key])+"\n")
	'''
	x = np.array(collapingList)
	y = np.array(duplicate2liveTimeMeanList)
	z = np.array(duplicate2liveTimeStdList)
	#print len(x),len(y),len(z)


	line = plt.plot(x, y, 'r-',label='mean')
	line2 = plt.plot(x, z, 'b-',label='std')

	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend()
	#plt.xlim([0,5000])
	plt.savefig("../img/"+title)
	plt.show()	

def getDuplicatePersonRate(value):
	leaderList = []
	beianList = []
	leader = value['leader']
	beian = value['beian']
	for eachValue in leader.values():
		leaderList.append(eachValue['reg_leader'])
	for eachValue in beian.values():
		beianList.append(eachValue['reg_person_name'])
	leaderList = list(set(leaderList))
	beianList = list(set(beianList))

	unitLength = len(list(set(leaderList+beianList)))
	intersectionLength = len(beianList) + len(leaderList) - unitLength
	return (intersectionLength,unitLength)


def computeLeaderAndManagerInfo(data):
	'''
		find the chongdie property of gudong and beian
		The number of zongjingli, dongshizhang,dongshi,jianshi,fuzongjingli ,qitarenshi,zhixingdongshi
		@input data

	'''

	typeOfLeader = {}
	gudongNumberOfSingleCompany = {}
	leaderNumOfSingleCompany = {}
	typeOfStock = {}
	StockNumOfSingleCompany = {}
	companyType = {}

	leaderNum_liveList = []
	managerNum_liveList = []
	leaderNum_manageNumList =[]
	leaderAndManager_liveList = []
	entropy_liveList = []
	biggestLeader_liveList = []



	for key,value in data.items():
		#compute the live long 
		singleLiveLong = 0
		if  value['cmpn_establish_date'] == "":
			continue
		registYear = time.strftime('%Y%m', time.localtime(float(value['cmpn_establish_date'])))
		if value['cmpn_pass_date'] != "":
			passMonth = time.strftime('%Y%m', time.localtime(float(value['cmpn_pass_date'])))
		if value['isDead'] == 1:
			if value['cmpn_pass_date'] == "":
				continue
			if 	value['aliveTime'] != 0:
				singleLiveLong = value['aliveTime']


		#statistic beian number

		if value.has_key('beian'):
			managerLength = len(value['beian'])
			managerNameList = []
			for key,eachBeian in value['beian'].items():
				managerNameList.append(eachBeian['reg_person_name'])
		
		#statistic leader Number
		singleEntropy = 0
		maxLeader = 0
		if value.has_key('leader'):
			leaderLength = len(value['leader'])
			leaderNameList = []
			realPaidList = []
			for key,eachLeader in value['leader'].items():
				leaderNameList.append(eachLeader['reg_leader'])
				if eachLeader['reg_real_pay'].strip() != "":
					realPaidList.append(float(eachLeader['reg_real_pay'].strip()))
			if realPaidList != []:
				if sum(realPaidList) != 0:
					singleEntropy = getEntropy(realPaidList)
					if len(realPaidList) == 1:
						maxLeader = 1
					else:
						maxLeader = max(realPaidList)/float(sum(realPaidList))
		#push data in list
		interval = 60*60*24
		leaderNum_manageNumList.append([leaderLength,managerLength])

		if singleLiveLong > 0:
			singleLiveData = singleLiveLong/interval
			leaderNum_liveList.append([leaderLength, singleLiveData])
			managerNum_liveList.append([managerLength,singleLiveData])
			leaderAndManager_liveList.append([len(set(leaderNameList+managerNameList)),singleLiveData])
			if singleEntropy!= 0:
				entropy_liveList.append([singleEntropy,singleLiveData])
			if maxLeader != 0:
				biggestLeader_liveList.append([maxLeader,singleLiveData])

	'''
		draw picture
	'''
	drawMutiPoints(leaderNum_liveList,'leader number(both people and company)','alive time','leader number and alive time')
	drawMutiPoints(managerNum_liveList,'manager number','alive time','manager number and alive time')
	drawMutiPoints(leaderNum_manageNumList,'leader number(both people and company)','manager number','leader number and manager number')
	drawMutiPoints(leaderAndManager_liveList,'leader number(both people and company) and manager number','alive time','leader&manager number and alive time')
	drawMutiPoints(entropy_liveList,'entrop','alive time','entrop and alive time')
	drawMutiPoints(biggestLeader_liveList,'biggest leader\'money','alive time','biggest leader money and alive time')
	
	#print companyType
	#showLine(companyType)
	#showLine(typeOfLeader)
	#showLine(leaderNumOfSingleCompany)
	#showLine(gudongNumberOfSingleCompany)

def drawMutiPoints(data,xlabel,ylabel,title):
	

	aList  = []
	bList = []
	
	logFile = file("../log/"+title+'.log','w')
	for a,b in data:
		aList.append(a)
		bList.append(b)
		logFile.write(str(a)+"\t"+str(b)+"\n")
	
	
	x = np.array(aList)
	y = np.array(bList)
	


	#line = plt.plot(x, y, 'r')
	line2 = plt.plot(x, y, 'bo')

	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend()
	
	plt.savefig("../img/"+title)
	plt.show()	


def getEntropy(realPaidList):

	if len(realPaidList) == 1:
		return 1

	realPaidList = np.array(realPaidList)
	#print realPaidList
	paidList = realPaidList / float(sum(realPaidList))
	
	result = -sum(np.log2(paidList)*paidList)
	#print realPaidList,paidList,result
	#time.sleep(2)
	return result


def showLine(data):
	for key,value in data.items():
		try:
			print key.decode('utf8'), value
		except:
			print key, value

def computeYearNum(data):
	year = {}
	deadCompany = {}
	liveLong = {}
	registerMoney = {}
	dateAll = []
	count = 0
	money2liveTime = []
	moneyDivision = {}
	for key,value in data.items():
		
		if  value['cmpn_establish_date'] == "":
			continue
		registYear = time.strftime('%Y%m', time.localtime(float(value['cmpn_establish_date'])))
		if value['cmpn_pass_date'] != "":
			passMonth = time.strftime('%Y%m', time.localtime(float(value['cmpn_pass_date'])))
		if year.has_key(registYear):
			year[registYear] += 1
		else:
			year[registYear] = 1
		if value['isDead'] == 1:
			if value['cmpn_pass_date'] == "":
				continue
			if deadCompany.has_key(passMonth):
				deadCompany[passMonth] += 1
			else:
				deadCompany[passMonth] = 1
			if 	value['aliveTime'] != 0:
				if liveLong.has_key(value['aliveTime']):
					liveLong[value['aliveTime']] += 1
				else:
					liveLong[value['aliveTime']] = 1
		# find the register money
		dollar2yuan = 6.1428
		if value['cmpn_register_finacial'] != "":
			singleMoney  =  value['cmpn_register_finacial'].split("万")[0].strip()
			#print len(singleMoney)
			#print singleMoney
			while not singleMoney[-1] in "1234567890":
				singleMoney = singleMoney[:-1]
				#print len(singleMoney)
			if "美" in value['cmpn_register_finacial']:
				singleCompanyMoney = float(singleMoney) * dollar2yuan
			else:
				singleCompanyMoney = float(singleMoney)
			if moneyDivision.has_key(singleCompanyMoney):
				moneyDivision[singleCompanyMoney] += 1
			else:
				moneyDivision[singleCompanyMoney] = 1
			if  registerMoney.has_key(registYear):
				registerMoney[registYear] += singleCompanyMoney
			else:
				registerMoney[registYear] = singleCompanyMoney
			if value.has_key('aliveTime'):
				money2liveTime.append([singleCompanyMoney,value['aliveTime']])


	year_momth = []
	year_month_number = []
	year_month_number_percent = []
	circleX = []
	circleY = []
	monthArrange = []
	deadCompanyList = []
	sumAliveCompany = 0
	aliveCompanyList = []
	newComplanyList = []
	registerMoneyList = []
	registerMoneyPercentList  = []
	tmpYear = sorted(year)
	for key in tmpYear:
		count += 1
		monthArrange.append(getMonth(key))
		dateAll.append(count)
		year_momth.append(key)
		year_month_number.append(year[key])
		sumAliveCompany
		#print key,year[key]
		#compute alive companies
		sumAliveCompany += year[key]
		if deadCompany.has_key(key):
			sumAliveCompany -= deadCompany[key]
			deadCompanyList.append(deadCompany[key])
			newComplanyList.append(year[key] - deadCompany[key])
		else:
			deadCompanyList.append(0)
			newComplanyList.append(year[key])
		aliveCompanyList.append(sumAliveCompany)
		#get the regist money
		if registerMoney.has_key(key):
			registerMoneyList.append(registerMoney[key])
		else:
			registerMoneyList.append(0)


	year_month_number_percent = np.array(year_month_number)/float(sum(year_month_number))
	registerMoneyPercentList = np.array(registerMoneyList)/float(sum(registerMoneyList))

	#drawLine(year_momth,dateAll,year_month_number,136,-1,"The number of established company in each month (chengdu)",'month','establish number')
	#drawLine(year_momth,dateAll,year_month_number_percent,136,-1,"The percent0 of established company in each month (chengdu)",'month','establish number')
	#drawLine(year_momth,dateAll,aliveCompanyList,136,-1,"The alived  company in each month (chengdu)",'month','alived company number')
	#drawLine(year_momth,dateAll,registerMoneyList,136,-1,"The register money in each month (chengdu)",'month','registered company number')
	#drawLine(year_momth,dateAll,registerMoneyPercentList,136,-1,"The register money percent in each month (chengdu)",'month','establish number')
	#drawMutiLine(year_momth,dateAll,[deadCompanyList,newComplanyList],136,-1,['Dead Company Number','New Company Number'],'Company Number')

	#drawAliveLongBarGraph(liveLong)
	drawMoneyBarGraph(moneyDivision)
	
	#drawMoney2AliveTime(money2liveTime)

	
def getMonth(dateStr):
	month = dateStr[-2:]
	if month[0] == "0":
		return int(month[1])
	else:
		return int (month)


def drawMoney2AliveTime(data):
	title = "register money and livetime(chengdu)"
	xlabel = "registerMoney"
	ylabel = "live time"

	registerMoneyList = []
	companyLiveTimeList = []
	yearRange = {}
	logFile = file("../log/"+title+'.log','w')
	for singleMoney,singleTime in data:
		singleTime = int(singleTime/60/60/24/30);
		if singleTime < 0:
			singleTime = 0
		registerMoneyList.append(singleMoney)
		companyLiveTimeList.append(singleTime)
		logFile.write(str(singleMoney)+"\t"+str(singleTime)+"\n")


	
	'''
	for key in sortedYear:
		company_year.append(np.log(key))
		company_year_number.append(yearRange[key])
		logFile.write(str(key)+"\t"+str(yearRange[key])+"\n")
	'''
	x = np.array(registerMoneyList)
	y = np.array(companyLiveTimeList)
	


	#line = plt.plot(x, y, 'r')
	line2 = plt.plot(x, y, 'bo')

	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend()
	plt.xlim([0,5000])
	plt.savefig("../img/"+title)
	plt.show()	

def drawMoneyBarGraph(data):
	title = "company regist money and number(month)"
	xlabel = "company regist money"
	ylabel = "number"

	yearRange = {}
	for key,value in data.items():
		yearInterval = int(key/100);
		if yearInterval < 0:
			yearInterval = 0
		if yearRange.has_key(yearInterval):
			yearRange[yearInterval] += value
		else:
			yearRange[yearInterval] = value

	company_year_number = []
	company_year = []
	sortedYear =sorted(yearRange)
	logFile = file("../log/"+title+'.log','w')

	for key in sortedYear:
		company_year.append(key)
		company_year_number.append(yearRange[key])
		logFile.write(str(key)+"\t"+str(yearRange[key])+"\n")
	
	x = np.log(np.array(company_year))
	y = np.log(np.array(company_year_number))
	


	#line = plt.plot(x, y, 'r')
	line2 = plt.plot(x, y, 'bo')

	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend()
	plt.savefig("../img/"+title)
	plt.show()	

def drawAliveLongBarGraph(data):
	title = "company_live_long and number(month)"
	xlabel = "live month log range"
	ylabel = "number"

	yearRange = {}
	for key,value in data.items():
		yearInterval = int(key/60/60/24/30);
		if yearInterval < 0:
			yearInterval = 0
		if yearRange.has_key(yearInterval):
			yearRange[yearInterval] += value
		else:
			yearRange[yearInterval] = value

	company_year_number = []
	company_year = []
	sortedYear =sorted(yearRange)
	logFile = file("../log/"+title+'.log','w')

	for key in sortedYear:
		company_year.append(key)
		company_year_number.append(yearRange[key])
		logFile.write(str(key)+"\t"+str(yearRange[key])+"\n")
	
	x = np.array(company_year)
	y = np.array(company_year_number)
	


	#line = plt.plot(x, y, 'r')
	line2 = plt.plot(x, y, 'bo')

	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend()
	plt.savefig("../img/"+title)
	plt.show()	

def drawLine(week,tmpX,tmpY,begin,end,title,xlabel,ylabel):
	x = np.array(tmpX[begin:end])
	y = np.array(tmpY[begin:end])
	week = np.array(week[begin:end])
	logFile = file("../log/"+title+'.log','w')
	weekendX = []
	weekendY = []
	weekdayX = []
	weekdayY = []

	for i in range(len(x)):
		logFile.write(str(week[i])+"\t"+str(y[i])+"\n")
		if week[i] == 1 :
			weekendX.append(x[i])
			weekendY.append(y[i])
		else :
			weekdayX.append(x[i])
			weekdayY.append(y[i])

	weekendX = np.array(weekendX)
	weekendY = np.array(weekendY)
	weekdayX = np.array(weekdayX)
	weekdayY = np.array(weekdayY)
	
	line = plt.plot(x, y, 'r')
	weekendLine = plt.plot(weekendX,weekendY, 'yo',label="Jan.")
	weekdayLine = plt.plot(weekdayX,weekdayY, 'ko',label='Other Month')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend()
	plt.savefig("../img/"+title)
	plt.show()	

def drawMutiLine(week,tmpX,tmpY,begin,end,labels,title):
	
	color = ['r','b','k','m','y','g']
	#print len(tmpY)
	x = np.array(tmpX[begin:end]) 
	week = np.array(week[begin:end])

	for lineIndex in range(len(tmpY)):

		
		y = np.array(tmpY[lineIndex][begin:end]) #/ max(tmpY[lineIndex][begin:end])

		weekendX = []
		weekendY = []
		weekdayX = []
		weekdayY = []

		for i in range(len(x)):
			if week[i] == 7 or week[i] == 6:
				weekendX.append(x[i])
				weekendY.append(y[i])
			else :
				weekdayX.append(x[i])
				weekdayY.append(y[i])

		weekendX = np.array(weekendX)
		weekendY = np.array(weekendY)
		weekdayX = np.array(weekdayX)
		weekdayY = np.array(weekdayY)
		
		weekendLine = plt.plot(weekendX,weekendY, 'yo')
		weekdayLine = plt.plot(weekdayX,weekdayY, 'ko')
		
		line = plt.plot(x, y, color[lineIndex],label=labels[lineIndex])

	plt.legend()
	plt.savefig(title)
	plt.show()	
	

def getBirthRate(birthAndDeadFileName):
	'''
	Get the birth rate in each month.
	Parameters:
		birthAndDeadFileName: str
			The file of firm birth and dead in every month.
	
	Return:
		{'date':[], 'birthRate':[]}: dict
			Record of firm birth rate of every month.

	Note:
		The input record format must be separated by '###'.
		e.g. '1983###11###4'.
	'''

	birthAndDeadFile = open(birthAndDeadFileName, 'r').readlines()
	existFirmNum = int(birthAndDeadFile[0].split('###')[1])
	birthRate = []
	recordDate = []
	for birthDeadRecord in birthAndDeadFile[1:]:
		birth = int(birthDeadRecord.split('###')[1])
		dead = int(birthDeadRecord.split('###')[2])
		birthRate.append(1.0 * birth / existFirmNum)
		recordDate.append(int(birthDeadRecord.split('###')[0]))
		existFirmNum += birth - dead
	return {'date': recordDate, 'birthRate': birthRate}
	

def getBirthDeadCor(birthAndDeadFileName):
	'''
	Explore the correlation betweeen firm death and firm emergence via Spearman coefficient.
	PS: the records later than 01/2010 should be abandoned.

	Parameters:
		birthAndDeadFileName: str
			The file of firm birth and dead in every month.

	Return:
		coefficient: int 
			correlation coefficient between firm death and emergence.
	'''
	
	birthAndDeadFile = open(birthAndDeadFileName, 'r').readlines()
	seq1, seq2 = [], []
	for birthDeadRecord in birthAndDeadFile[1:]:
		birth = int(birthDeadRecord.split('###')[1])
		dead = int(birthDeadRecord.split('###')[2])
		seq1.append(birth)
		seq2.append(dead)
		if int(birthDeadRecord.split('###')[0]) >= 201001:
			break
	print spearmanr(seq1, seq2)
	print pearsonr(seq1, seq2)
	print kendalltau(seq1, seq2)



if __name__ == '__main__':
	main()
