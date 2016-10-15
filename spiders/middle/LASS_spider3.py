import scrapy
from scrapy.spiders import Spider
import sys
import os
import json


class LASSCrawler(Spider):
    name = 'LASS3'
    start_urls = ['ftp://gpssensor.ddns.net:2121/data.log-20160517']
    def parse(self, response):
        domain = 'ftp://gpssensor.ddns.net:2121'
        sel = response.body
        line = sel.split('\n')
        temp = {}
        for i in line:
            part = i.split('|')
            if len(part)==1:continue
            for item in part:
                subitem = item.split('=')
                if len(subitem) == 2:
                    temp[subitem[0]] = True
            with open("totalitem.json", "w") as outfile:
                json.dump({'items':temp.keys()}, outfile, sort_keys = True, indent=2)

    def start_requests(self):
        yield scrapy.http.Request('ftp://gpssensor.ddns.net:2121/data.log-20160517',
                      meta={'ftp_user': 'anonymous', 'ftp_password': ''})
    
