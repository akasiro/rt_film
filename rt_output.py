import pandas as pd
import sqlite3

class rt_output():
    '''
    for data save
    Attributes:
        dbpath (str): the database path
    '''
    def __init__(self, dbpath=None):
        '''
        Args:
            dbpath (str): the database path, default to None
        '''
        self.dbpath = dbpath
        self.conn = sqlite3.connect(dbpath)
    def output_index(self, df, table_name):
        '''
        for save index to database
        Args:
            df (DataFrame): the data
            table_name (str): the table name to store the data
        '''
        df.to_sql(name=table_name,con=self.conn,if_exists='append',index=False)
    def output_page(self, df, table_name):
        '''
        for save page to database
        Args:
            df (DataFrame): the data
            table_name (str): the table name to store the data
        '''
        df.to_sql(name=table_name,con=self.conn,if_exists='append',index=False)
    def output_critic_review(self, df, table_name):
        '''
        for save page to database
        Args:
            df (DataFrame): the data
            table_name (str): the table name to store the data
        '''
        df.to_sql(name=table_name,con=self.conn,if_exists='append',index=False)
