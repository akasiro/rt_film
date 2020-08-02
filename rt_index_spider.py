import configparser
import sys,os
from rt_parser import rt_parser
from rt_output import rt_output
from log_manager import log_manager
sys.path.append('/home/guijideanhao/pyproject/scrapy_toolv2')
from html_downloader import html_downloader

CONF = configparser.ConfigParser()
CONF.read('rt_config.cfg')
DATAPATH = CONF.get('DEFAULT','datapath')
TABLE_NAME = CONF.get('INDEX','table_name')
DBPATH =CONF.get('INDEX','dbpath')
LOGGING_FILE = CONF.get('INDEX','logging_file')

class rt_index_spider():
    '''
    organizer for scrape index page
    Attributes:
        
    '''
    def __init__(self,datapath=DATAPATH, logging_file=LOGGING_FILE, dbpath=DBPATH):
        self.hd = html_downloader(china=False)
        self.lg = log_manager(os.path.join(datapath,logging_file))
        self.parser = rt_parser()
        self.output = rt_output(os.path.join(datapath,dbpath))
        
        self.usedurl = self.lg.get_info_list(success_tag='SUCCESS')
    def scrape(self,table_name=TABLE_NAME, teststop=-1):
        i = 0
        while True:
            i = i+1
            url = 'https://www.rottentomatoes.com/api/private/v2.0/browse?sortBy=release&type=dvd-streaming-all&page={}'.format(i+1)
            if url in self.usedurl:
                continue
            try:
                res = self.hd.request_proxy(url)
                if res == None:
                    self.lg.write_log(info=url,success=False,info_type='download1')
                    break
            except:
                self.lg.write_log(info=url,success=False,info_type='download2')
                break
            try:
                success,*df = self.parser.parse_index(res.content)
                if not success:
                    self.lg.write_log(info=url,success=False,info_type='parse1')
                    break
            except:
                self.lg.write_log(info=url,success=False,info_type='parse2')
                break
            try:
                self.output.output_index(df[0], table_name)
                self.lg.write_log(info=url,success=True,info_type='success')
            except:
                self.lg.write_log(info=url,success=False,info_type='db')
                break
            if teststop==0:
                print('test end')
                break
            if teststop>0:
                teststop=teststop-1
        print('mission complete')
                
if __name__ == '__main__':
#     # test code
#     test = rt_index_spider(datapath=CONF.get('TEST','datapath'))
#     test.scrape(teststop=2)
    # formal code
    spider = rt_index_spider()
    spider.scrape()
    
