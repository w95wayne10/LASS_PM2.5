import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
import sys
import os
import json

def myFormatDump(filename, result, sort = True, ind = 2):
	temp = json.dumps(result, sort_keys = sort, indent = ind)
	nil = temp.find('[')
	nir = temp.find(']')
	while nil >= 0:
		T = temp[nil:nir+1]
		T2 = T.replace('\n','').replace(' ','')
		temp = temp.replace(T, T2)
		nil = temp.find('[', nil + 1)
		nir = temp.find(']', nil + 1)
	myfile = open(filename, "w")
	myfile.write(temp)
	myfile.close()

class LASSCrawler(Spider):
	name = 'LASS5'
	start_urls = ['ftp://gpssensor.ddns.net:2121/data.log-20160517']
	def parse(self, response):
		domain = 'ftp://gpssensor.ddns.net:2121'
		sel = response.body
		line = sel.split('\n')

		#construct container
		UsedAvg = ['gps_lat', 'gps_lon']
		UsedKey = ['device_id']
		UsedFloat = ['s_d0'] + UsedAvg
		UsedValue = ['time'] + UsedFloat
		UsedItem = UsedKey + UsedValue
		CanNotUseValue = [None, '']
		LASSinfo = {}
		LASSinfo[UsedKey[0]] = []
		for item in UsedValue:
			LASSinfo[item] = {}

		#parting website's data and putting what we need in temp
		for i in line:
			part = i.split('|')
			if len(part)==1:continue
			temp = {}
			for item in part:
				subitem = item.split('=')
				if len(subitem) == 2 and subitem[0] in UsedItem:
					temp[subitem[0]] = subitem[1]
			
			#drup the value we can't use
			valid = True
			for item in UsedItem:
				for CNUV in CanNotUseValue:
					if temp.get(item) == CNUV:
						valid = False
			if not valid: continue

			#creating unique key list in LASSinfo
			if temp[UsedKey[0]] not in LASSinfo[UsedKey[0]]:
				LASSinfo[UsedKey[0]].append(temp[UsedKey[0]])

			#putting data in LASSinfo and turn to float in need 
			for item in UsedValue:
				if LASSinfo[item].get(temp[UsedKey[0]]) == None:
					LASSinfo[item][temp[UsedKey[0]]] = []
				if item in UsedFloat:
					LASSinfo[item][temp[UsedKey[0]]].append(float(temp[item]))
				else:
					LASSinfo[item][temp[UsedKey[0]]].append(temp[item])

		#construction completed LASSinfo, exporting to a json file
		myFormatDump("LASSinfo.json", LASSinfo)

		#export all device id to a json file
		with open("device_id_list.json", "w") as outfile:
			json.dump(LASSinfo[UsedKey[0]], outfile, sort_keys=True, indent=2)

		#parting LASSinfo by unique key
		i = 0
		for ID in LASSinfo[UsedKey[0]]:
			i += 1

			#making avg info
			for item in UsedAvg:
				InfoAvg = LASSinfo[item][ID]
				LASSinfo[item][ID] = sum(InfoAvg)/len(InfoAvg)

			#export a conplete info about one object
			result = {}
			result[UsedKey[0]] = ID
			for item in UsedValue:
				result[item] = LASSinfo[item][ID]
			myFormatDump("testfile_device_id_"+str(i)+".json", result)
			



	def start_requests(self):
		yield scrapy.http.Request('ftp://gpssensor.ddns.net:2121/data.log-20160517', 
			meta={'ftp_user': 'anonymous', 'ftp_password': ''})
