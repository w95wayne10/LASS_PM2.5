import scrapy
import bs4
from bs4 import BeautifulSoup
import lxml
from scrapy.spiders import Spider
from scrapy.selector import Selector
import sys
import re
import os
import json


class LASSCrawler(Spider):
    name = 'LASS2'
    start_urls = ['ftp://gpssensor.ddns.net:2121/data.log-20160516']
    def parse(self, response):
        domain = 'ftp://gpssensor.ddns.net:2121/'
        sel = response.body
        #res = BeautifulSoup(response.extract(), "lxml")
        line = sel.split('\n')
        LASSvalue = {}
        LASStime = {}
        for i in line:
            #print line[i][0],
            #LASSitem.append()
            part = i.split('|')
            if len(part)==1:continue
            temp = {}
            for item in part:
                subitem = item.split('=')
                if len(subitem) == 2:
                    if subitem[0] == 'gps_lon': 
                        temp[subitem[0]] = subitem[1][:7]
                    if subitem[0] == 'gps_lat': 
                        temp[subitem[0]] = subitem[1][:6]
                    if subitem[0] == 's_d0' or subitem[0] == 'time': 
                        temp[subitem[0]] = subitem[1]
            if temp.get('gps_lat') == None or temp.get('gps_lon') == None or temp.get('s_d0') == None or temp.get('time') == None: continue
            if LASSvalue.get((temp['gps_lat'],temp['gps_lon'])) == None:
                LASSvalue[temp['gps_lat'],temp['gps_lon']] = []
                LASStime[temp['gps_lat'],temp['gps_lon']] = []
            LASSvalue[temp['gps_lat'],temp['gps_lon']].append(float(temp['s_d0']))
            LASStime[temp['gps_lat'],temp['gps_lon']].append(temp['time'])
        i = 0
        for myitem in LASSvalue.keys():
            i = i + 1
            with open("testfile"+str(i)+".json", "w") as outfile:
                json.dump({'gps_lat':myitem[0],'gps_lon':myitem[1],'s_d0':LASSvalue[myitem],'time':LASStime[myitem]}, outfile, sort_keys = True, indent=4)

    def start_requests(self):
        yield scrapy.http.Request('ftp://gpssensor.ddns.net:2121/data.log-20160516',
                      meta={'ftp_user': 'anonymous', 'ftp_password': ''})
    
