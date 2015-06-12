# encoding=utf-8
# 
import time,re
import xlrd

def main():
	data = init()
	process(data)

def init():
	regist = initRegist()
	beian  = initBeiAn()
	leader = initLeader()
	return (regist,beian,leader)

def process(data):
	outputFile = file('../data/cleanData.txt','w')
	finalObject = {}
	(regist,beian,leader) = data
	
	time.sleep(10)
	for key,value in regist.items():
		value['beian'] ={}
		value['beianNum'] = 0
		value['leader'] = {}
		value['leaderNum'] = 0
		'''
			check whether the company is dead
		'''
		if value['cmpn_register_type'] == "吊销，未注销":
			value['isDead'] = 1
			
			if value['cmpn_pass_date'] == "" or value['cmpn_establish_date'] == "":
				value['aliveTime'] = ""
			else:
				value['aliveTime'] = value['cmpn_pass_date'] - value['cmpn_establish_date']
		else:
			value['isDead'] = 0
		'''
			check the categories of the company
		'''
		categories = getTheCategoryFromCompany(value['cmpn_range'])


		finalObject[key] = value


	for key,value in beian.items():
		
		finalObject[key]['beianNum'] = len(value)
		finalObject[key]['beian'] = value

	for key,value in leader.items():
		
		finalObject[key]['leaderNum']  = len(value)
		finalObject[key]['leader'] = value

	for element in finalObject:
		outputFile.write(str(finalObject[element])+"\n")

def initLeader():
	leaderFile = file("../gudong.csv")
	count = 0
	leader  = {}
	for element in leaderFile:

		if count == 0:
			count+= 1
			continue
		count	 +=1
		Info = element.split("\t")
		singleLeader = {}
		singleLeader['reg_num'] = Info[0]
		singleLeader['reg_complany_name'] = Info[1]
		singleLeader['reg_leader_type'] = Info[2]
		singleLeader['reg_leader'] = Info[3]
		singleLeader['reg_card_type'] = Info[4]
		singleLeader['reg_need_pay'] = Info[5]
		singleLeader['reg_real_pay'] = Info[6]

		if leader.has_key(singleLeader['reg_num']):
			subLeaderNum = len(leader[singleLeader['reg_num']])+1
			leader[singleLeader['reg_num']][str(subLeaderNum)] = singleLeader	
		else:
			leader[singleLeader['reg_num']] = {}
			leader[singleLeader['reg_num']]["1"] = singleLeader	
		
	return leader
def initBeiAn():
	beiAnFile = file("../beiAn.csv")
	errorLog = file('../log/beian.log','w')
	count = 0
	errorFlag = 0
	BNInfo = {}
	for element in beiAnFile:
		if count == 0:
			count += 1
			continue
		count += 1

		if count % 1000 == 0:
			print count
		Info = element.split("\t")

		singleBNInfo = {}
		singleBNInfo['reg_num'] = Info[0]

		try:
			singleBNInfo['reg_name'] = Info[1]
		except IndexError:
			exceptReason= "line "+str(count)+" name error "+singleBNInfo['reg_num']+'######'
			singleBNInfo ['reg_name'] = ""
			errorFlag = 1

		try:
			singleBNInfo['reg_subNum'] = Info[2]
		except IndexError:
			exceptReason= "line "+str(count)+" subNum error "+singleBNInfo['reg_num']+'######'
			singleBNInfo ['reg_subNum'] = ""
			errorFlag = 1
		
		try:
			singleBNInfo['reg_person_name'] = Info[3]
		except IndexError:
			exceptReason= "line "+str(count)+" person name error"+singleBNInfo['reg_num']+'######'
			singleBNInfo ['reg_person_name'] = ""
			errorFlag = 1

		try:
			singleBNInfo['reg_duty'] = Info[4]
		except IndexError:
			exceptReason= "line "+str(count)+" duty erorr"+singleBNInfo['reg_num']+'######'
			singleBNInfo ['reg_duty'] = ""
			errorFlag = 1
		if errorFlag == 1:
			errorLog.write(exceptReason + element+"\n")
		if BNInfo.has_key(singleBNInfo['reg_num']):
			BNInfo[singleBNInfo['reg_num']][singleBNInfo['reg_subNum']] = singleBNInfo 
		else:
			BNInfo[singleBNInfo['reg_num']] = {}
			BNInfo[singleBNInfo['reg_num']][singleBNInfo['reg_subNum']] = singleBNInfo 
	return BNInfo


def initRegist():
	errorLog = file("../log/errorLog.txt",'w')
	registerFile = xlrd.open_workbook("../data.xls",'r')
	gudongFile  = file("../gudong.csv")
	beiAnFile = file("../beiAn.csv")
	count =  0
	rigist = {}
	table  = registerFile.sheets()[0]
	nrows = table.nrows

	for rownum in range(nrows):
		
		if count == 0:
			count += 1
			continue
		count += 1
		if count % 1000 == 0:
			print count
		Info =table.row_values(rownum)

		errorFlag = 0
		singleRigister = {}
		singleRigister['reg_num']  = Info[0].encode('utf8')
		#print singleRigister['reg_num']
		try:
			singleRigister ['cmpn_name'] = Info[1].encode("utf8")
		except IndexError:
			singleRigister ['cmpn_name'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_type'] = Info[2].encode("utf8")
		except IndexError:
			singleRigister ['cmpn_type'] = ""
			errorFlag = 1
		
		try:
			singleRigister ['cmpn_legal_person'] = Info[3].encode("utf8")
		except IndexError:
			singleRigister ['cmpn_legal_person'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_register_finacial'] = Info[4].encode("utf8")
		except IndexError:
			singleRigister ['cmpn_register_finacial'] = ""
			errorFlag = 1
		try:
			#print Info
			singleRigister ['cmpn_establish_date'] = Info[5].encode('utf8')
		except IndexError:
			singleRigister ['cmpn_establish_date'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_address'] = Info[6].encode("utf8")
		except IndexError:
			singleRigister ['cmpn_address'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_open_date'] = Info[7].encode('utf8')
		except IndexError:
			singleRigister ['cmpn_open_date'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_end_date'] = Info[8].encode('utf8')
		except IndexError:
			singleRigister ['cmpn_end_date'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_range'] = Info[9].encode("utf8")
		except IndexError:
			singleRigister ['cmpn_range'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_register_department'] = Info[10].encode("utf8")
		except IndexError:
			singleRigister ['cmpn_register_department'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_pass_date'] = Info[11].encode('utf8')
		except IndexError:
			singleRigister ['cmpn_pass_date'] = ""
			errorFlag = 1
		try:
			singleRigister ['cmpn_register_type'] = Info[12].encode("utf8")
		except IndexError:
			singleRigister ['cmpn_register_type'] = ""
			errorFlag = 1
		formatTimeForSingleRigister(singleRigister,count)
		if errorFlag == 1:
			errorLog.write(element+"\n")
		rigist[singleRigister['reg_num']] = singleRigister
	
	return rigist

def formatTimeForSingleRigister(singleRigister,line):
	timeLog = file("../log/timeErrorLog.txt",'a')
	timeErrorFlag = 0
	singleRigister['cmpn_establish_date'] = formatTime(singleRigister['cmpn_establish_date']) 

	try:
		singleRigister['cmpn_open_date'] = formatTime(singleRigister['cmpn_open_date']) 
	except ValueError:
			
		print singleRigister['reg_num'] ,line
		print "open date error"
		exceptReason = str(line)+" "+singleRigister['reg_num']+"open date error     " 
		print singleRigister['cmpn_open_date']
		try:
			singleRigister['cmpn_open_date'] = float(singleRigister['cmpn_open_date'])
		except:
			timeErrorFlag =1
			singleRigister['cmpn_open_date'] = ""

	try:
		singleRigister['cmpn_end_date'] = formatTime(singleRigister['cmpn_end_date']) 
	except ValueError:
		print singleRigister['reg_num'] ,line
		print "end date error"
		print singleRigister['cmpn_end_date']
		exceptReason = str(line)+" "+singleRigister['reg_num']+"end date error     " 
		try:
			singleRigister['cmpn_end_date'] = float(singleRigister['cmpn_end_date'])
		except:
			timeErrorFlag =1
			singleRigister['cmpn_end_date'] = ""
	try:
		singleRigister['cmpn_pass_date'] = formatTime(singleRigister['cmpn_pass_date']) 
	except ValueError:
		print singleRigister['reg_num'] ,line
		print "pass date error"
		print singleRigister['cmpn_pass_date']
		exceptReason = str(line)+" "+singleRigister['reg_num']+"pass date error     " 
		try:
			singleRigister['cmpn_pass_date'] = float(singleRigister['cmpn_pass_date'])
		except:
			timeErrorFlag =1
			singleRigister['cmpn_pass_date'] = ""
	if timeErrorFlag == 1:
		timeLog.write(exceptReason + "#######"+str(singleRigister)+"\n")
	
def formatTime(singleTime):
	if singleTime == "":
		return ""
	if singleTime[0] == '0' or "1899" in singleTime:
		return ""
	else:
		try:
			currentTime = time.strptime(singleTime,'%Y-%m-%d')
		except:
			currentTime = time.strptime(singleTime,'%Y年%m月%d日')
		if currentTime == "":
			print "error"
		try:
			timeStamp =  time.mktime(currentTime)
			return timeStamp
		except ValueError:
			print singleTime
			print currentTime
			time.sleep(100)

def getTheCategoryFromCompany(categoryRange):
	pass#print categoryRange

main()
