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
	data =init()
	getNetwork(data)


def getNetwork(data):
	nodes = []
	links = []
	company = {}
	count = 0
	networkFile = file("../data/network.dat",'w')
	for key,value in data.items():
		cmpn_name = value['cmpn_name'].strip()
		if cmpn_name =="":
			continue
		if not company.has_key(cmpn_name):

			company[cmpn_name] = {}
			company[cmpn_name]['num'] = len(company)
			company[cmpn_name]['establish_time'] = value['cmpn_establish_date']
			company[cmpn_name]['money'] = value['format_regist_money']

			#add nodes
			tmpNodes  = {}
			tmpNodes['name'] = cmpn_name
			singleCompanyMoney = value['format_regist_money']
			if singleCompanyMoney == 0:
				tmpNodes['group'] = 1
			elif 0 < singleCompanyMoney < 10:
				tmpNodes['group'] = 2
			elif 10 < singleCompanyMoney < 100:
				tmpNodes['group'] = 3
			elif 100 < singleCompanyMoney < 1000:
				tmpNodes['group'] = 4 
			else:
				tmpNodes['group'] = 5
			nodes.append(tmpNodes)


	for key,value in data.items():
		leaders = value['leader']
		#print len(leaders)
		for k, eachLeader in leaders.items():
			#print eachLeader
			outputList =[]
			leaderType = eachLeader['reg_leader_type']
			if eachLeader['reg_real_pay'].strip() != "":
				paidMoney = float(eachLeader['reg_real_pay'].strip())
			else:
				paidMoney = 1

			if leaderType == "自然人" or leaderType == "自然人股东" or leaderType == "非农民自然人" or leaderType == "农民自然人" or leaderType == "外籍自然人" :
				continue		
			else :
				leaderCompnayName = eachLeader['reg_leader'].strip()
				toCompanyName = eachLeader['reg_complany_name']
				if leaderCompnayName == "" or toCompanyName == "":
					continue
				if toCompanyName == "":
					continue
				if not company.has_key(toCompanyName):
					'a'#print toCompanyName
				if not company.has_key(leaderCompnayName):
					company[leaderCompnayName] = {}
					company[leaderCompnayName]['num']= len(company)

					#addNodes
					tmpNodes  = {}
					tmpNodes['name'] = leaderCompnayName
					tmpNodes['group'] = 6
					nodes.append(tmpNodes)

			#add link
			tmpLink = {}
			tmpLink['source'] = company[leaderCompnayName]['num']
			tmpLink['target'] = company[toCompanyName]['num']
			
			if paidMoney > 100:
				tmpLink['value'] = 100
			else:
				tmpLink['value'] = paidMoney
			links.append(tmpLink)


			outputList.append(str(company[leaderCompnayName]['num']))
			outputList.append(str(company[toCompanyName]['num']))
			#print toCompanyName
			outputList.append(str(company[toCompanyName]['money']))
			outputList.append(str(company[toCompanyName]['establish_time']))

			networkFile.write("\t".join(outputList)+"\n")

	companyFile = file("../log/company.log",'w')
	for element in company:
		companyFile.write(str(company[element]['num'])+"###"+str(element)+"\n")
	network = {}
	network['nodes'] = nodes
	network['links'] = links

	limitNodes = clustering(network)
	writeJson(network,limitNodes)


def clustering(network):
	cluster = {}
	isChoosed = {}
	count = 0
	for eachLink in network['links']:
		sourceNode = eachLink['source']
		targetNode = eachLink['target']
		if not isChoosed.has_key(sourceNode) and not isChoosed.has_key(targetNode):
			isChoosed[sourceNode] = count
			isChoosed[targetNode] = count
			cluster[count] = {}
			cluster[count][sourceNode] = 1
			cluster[count][targetNode] = 1
			count += 1
		if not isChoosed.has_key(sourceNode) and  isChoosed.has_key(targetNode):
			clusterNum = isChoosed[targetNode]
			isChoosed[sourceNode] = clusterNum
			cluster[clusterNum][sourceNode] = 1
			cluster[clusterNum][targetNode] += 1

		if isChoosed.has_key(sourceNode) and  not isChoosed.has_key(targetNode):
			clusterNum = isChoosed[sourceNode]
			isChoosed[targetNode] = clusterNum
			cluster[clusterNum][targetNode] = 1
			cluster[clusterNum][sourceNode] += 1
		
		if isChoosed.has_key(sourceNode) and  isChoosed.has_key(targetNode):
			'''  Combine the two *** to smaller one'''
			if isChoosed[sourceNode] != isChoosed[targetNode]:
				clusterNum1 = isChoosed[sourceNode]
				clusterNum2 = isChoosed[targetNode]
				smallerNum = min(clusterNum1,clusterNum2)
				biggerNum = max(clusterNum1,clusterNum2)
				for eachNode in cluster[biggerNum]:
					cluster[smallerNum][eachNode] = cluster[biggerNum][eachNode]
					isChoosed[eachNode] = smallerNum
				del cluster[biggerNum]

	print len(cluster)
	networkLog = file('../log/networkLog.log','w')
	networkRange = {}
	for e in cluster:
		length = len(cluster[e])
		if networkRange.has_key(length):
			networkRange[length]+=1
		else:
			networkRange[length] = 1

		networkLog.write(str(len(cluster[e]))+"###"+str(cluster[e])+"\n")

	for element in networkRange:
		print element , networkRange[element]

	print cluster[30]
	return  cluster[30]


def writeJson(data,limitNodes):
	outputJson = file("../data/network.json",'w')
	transferNodes = {}
	outputJson.write("{\n")
	##########nodes##############
	outputJson.write('\t"nodes":[\n')
	count = 0
	nodesLen = len(limitNodes)
	for element in limitNodes:
		transferNodes[element] = count
		
		count += 1
		if count == nodesLen:
			outputJson.write("\t\t"+'{"name":"'+str(data['nodes'][element]['name'])+'","group":'+str(data['nodes'][element]['group'])+'}'+"\n")
		else:
			outputJson.write("\t\t"+'{"name":"'+str(data['nodes'][element]['name'])+'","group":'+str(data['nodes'][element]['group'])+'},'+"\n")
	outputJson.write("\t],\n")

	##########links##############
	outputJson.write('\t"links":[\n')
	count = 0
	linkLen = len(data['links'])
	outputLink = []
	for element in data['links']:
		count += 1
		if limitNodes.has_key(element['source']) and limitNodes.has_key(element['target']):
			if count == linkLen:
				outputLink.append("\t\t"+'{"source":'+str(transferNodes[element['source']])+',"target":'+str(transferNodes[element['target']])+',"value":'+str(element['value'])+'}')
			else:
				outputLink.append("\t\t"+'{"source":'+str(transferNodes[element['source']])+',"target":'+str(transferNodes[element['target']])+',"value":'+str(element['value'])+'}')
	outputJson.write(",\n".join(outputLink)+"\n")
	outputJson.write("\t]\n")
	outputJson.write("}\n")




def init():
	data ={}
	originFile = file("../data/secondCleanData.dat")
	for element in originFile:
		Info = eval(element.strip())
		data[Info['reg_num']] =Info
	return data



if __name__ == '__main__':
	main()
