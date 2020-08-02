import configparser
import sys,os,sqlite3
import pandas as pd
from urllib.parse import urljoin
from rt_parser import rt_parser
from rt_output import rt_output
from log_manager import log_manager
sys.path.append('/home/guijideanhao/pyproject/scrapy_toolv2')
from html_downloader import html_downloader
from rt_index_spider import rt_index_spider
CONF = configparser.ConfigParser()
CONF.read('rt_config.cfg')
DATAPATH = CONF.get('DEFAULT','datapath')
TABLE_NAME = CONF.get('PAGE','table_name')
TABLE_NAME2 = CONF.get('PAGE','table_name2')
TABLE_NAME3 = CONF.get('PAGE','table_name3')
DBPATH =CONF.get('PAGE','dbpath')
LOGGING_FILE = CONF.get('PAGE','logging_file')
DOMAIN_URL = CONF.get('DEFAULT', 'domain_url')
index_table_name = CONF.get('INDEX', 'table_name')
index_dbpath_full = os.path.join(DATAPATH,DBPATH)
index_conn = sqlite3.connect(index_dbpath_full)

URLLIST = pd.read_sql('select url from {}'.format(index_table_name), index_conn)['url'].values.tolist()
index_conn.close()

class rt_page_spider(rt_index_spider):
    def __init__(self,datapath=DATAPATH, logging_file=LOGGING_FILE, dbpath=DBPATH):
        rt_index_spider.__init__(self, datapath, logging_file, dbpath)
    def scrape(self,urllist=URLLIST, table_name=TABLE_NAME, teststop=-1):
        for url in urllist:
            if url in self.usedurl:
                continue
            if teststop==0:
                print('test end')
                break
            if teststop>0:
                teststop=teststop-1
            full_url = urljoin(DOMAIN_URL,url)
            try:
                res = self.hd.request_proxy(full_url)
                if res == None:
                    self.lg.write_log(info=url,success=False,info_type='download1')
                    continue
            except:
                self.lg.write_log(info=url,success=False,info_type='download2')
                continue
            try:
                success,*df = self.parser.parse_page(url,res.content)
                if not success:
                    self.lg.write_log(info=url,success=False,info_type='parse1')
                    continue
            except:
                self.lg.write_log(info=url,success=False,info_type='parse2')
                continue
            try:
                self.output.output_page(df[0], table_name)
                self.lg.write_log(info=url,success=True,info_type='success')
            except:
                self.lg.write_log(info=url,success=False,info_type='db')
                continue
        print('mission complete')
if __name__ == '__main__':
#     #test code
    
#     urllist = ['/m/to_be_and_to_have', '/m/the_living_end', '/m/the_blood_of_a_poet']
#     test = rt_page_spider(datapath=CONF.get('TEST','datapath'))
#     test.scrape(urllist, teststop=2)
    
    # formal code
    spider = rt_page_spider()
    spider.scrape(table_name=TABLE_NAME3)
