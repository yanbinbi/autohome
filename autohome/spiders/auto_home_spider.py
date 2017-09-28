# -*- coding: utf-8 -*-
import scrapy
from autohome.items import AutohomeItem
import logging

# 日志器
logger = logging.getLogger()


class AutoHomeSpider(scrapy.Spider):
	name = "autohome"
	allowed_domains = ["autohome.com.cn"]
	start_urls = ["http://www.autohome.com.cn"]

	def start_request(self):
		# 分类列表
		items = ['all', 'news', 'advice', 'drive', 'use', 'culture', 'travels', 'tech', 'tuning']

		reqs = []

		for item in items:
			for i in range(1,5545):
				req = scrapy.Request("http://www.autohome.com.cn/{0}/{1}/#liststart".format(item, i))
				reqs.append(req)

		return reqs

	def parse(self, response):
		for href in response.css('.article li a::attr(href)').extract():
			if 'http' not in href:
				full_url = response.urljoin('http:' + href)
			else:
				full_url = response.urljoin(href)
			yield scrapy.Request(full_url, callback=self.parse_content)

		# 多级页面爬取,倒数第二个为'下一页'的uri
		try:
			next_page = response.xpath('//*[@id="articlewrap"]/div/a/@href')[-2]
			if next_page is not None:
				next_full_url = response.urljoin(next_page)
				yield scrapy.Request(next_full_url, callback=self.parse)
		except Exception as e:
			logger.error(e)
			print(e)


	def parse_content(self, response):
		for sel in response.xpath('//*[@id="articlewrap"]'):#articlewrap
			item = AutohomeItem()
			item["title"] = sel.xpath('h1/text()').extract()[0].strip()#//*[@id="articlewrap"]/h1
			item["content"] = ''.join(sel.xpath('//*[@id="articleContent"]/p//text()').extract())#//*[@id="articleContent"]/p[61]
			
			yield item