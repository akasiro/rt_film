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
TABLE_NAME = CONF.get('CRITIC_REVIEW','table_name')
DBPATH =CONF.get('CRITIC_REVIEW','dbpath')
LOGGING_FILE = CONF.get('CRITIC_REVIEW','logging_file')
DOMAIN_URL = CONF.get('DEFAULT', 'domain_url')
index_table_name = CONF.get('INDEX', 'table_name')
index_dbpath_full = os.path.join(DATAPATH,DBPATH)
index_conn = sqlite3.connect(index_dbpath_full)

URLLIST = pd.read_sql('select url from {}'.format(index_table_name), index_conn)['url'].values.tolist()
index_conn.close()

class rt_critic_review_spider(rt_index_spider):
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
            self.scrape_single_url(url)
        print('mission complete')
    def scrape_single_url(self, url,pageurl=None,table_name=TABLE_NAME):
        if pageurl:
            full_url = urljoin(DOMAIN_URL, pageurl)
        else:
            full_url = urljoin(DOMAIN_URL, url)+'/reviews'
#         print(full_url)
        try:
            res = self.hd.request_proxy(full_url)
            
            if res == None:
                self.lg.write_log(info=url,success=False,info_type='download1')
                return
#             print(res.status_code)
        except:
            self.lg.write_log(info=url,success=False,info_type='download2')
            return
        try:
            success,*df = self.parser.parse_critic_review(url,res.content)
#             print(success)
            if not success:
                self.lg.write_log(info=url,success=False,info_type='parse1')
                return
        except:
            self.lg.write_log(info=url,success=False,info_type='parse2')
            return
        try:
            self.output.output_critic_review(df[0], table_name)
#             print('saved')
        except:
            self.lg.write_log(info=url,success=False,info_type='db')
            return

        next_page, *pageurls = self.parser.parse_critic_review_next(url,res.content)
#         print(next_page)
#         print(pageurls)
        if next_page:
            self.scrape_single_url(url=url, pageurl=pageurls[0], table_name=TABLE_NAME)
        else:
            self.lg.write_log(info=url,success=True,info_type='success')
            return
if __name__ == "__main__":
    # test
#     urllist = ['/m/to_the_stars']
#     test = rt_critic_review_spider(datapath=CONF.get('TEST','datapath'))
#     test.scrape_single_url(urllist[0])
    # formal
    spider = rt_critic_review_spider()
    spider.scrape(table_name=TABLE_NAME)
