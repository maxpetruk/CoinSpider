# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from influxdb import InfluxDBClient
from scrapy.conf import settings
from scrapy.exceptions import DropItem
import logging
import traceback

_logging = logging.getLogger('CoinSpider.pipelines')


class CoinspiderInfluxdb(object):
    parent_tpl = {
        "measurement": "localbitcoins",
        "tags": {
        },
        "fields": {
        }
    }

    def open_spider(self, spider):
        _logging.info('create influxdb connections...')
        try:
            self.client = InfluxDBClient(
                host=settings.INFLUX_HOST,
                port=settings.INFLUX_PORT,
                username=settings.INFLUX_USER,
                password=settings.INFLUX_PASS,
                database=settings.INFLUX_DATABASE
            )
        except Exception as e:
            _logging.error('connection error: %s', traceback.format_exc())

    def process_item(self, item, spider):
        # if current spider is `localcoins` then stop running other pipeline
        if spider.name != 'localbitcoins':
            return item
        data_tpl = self.parent_tpl
        data_tpl['tags'] = {
            'price': item['price'],
            'price_currency': item['price_currency'],
            'trade_bank': item['trade_bank'],
            'trade_method': item['trade_method'],
            'trade_location': item['trade_location'],
            'time': item['time'],
        }
        data_tpl['fields'] = {
            'user': item['user'],
            'email': item['email'],
            'url': item['url'],
            'trade_msg': item['trade_msg'],
            'require_min': item['require_min'],
            'require_max': item['require_max']
        }
        self.client.write_points([data_tpl])
        raise DropItem
    
    def close_spider(self, spider):
        logging.info('close influxdb connections...')
        self.client.close()