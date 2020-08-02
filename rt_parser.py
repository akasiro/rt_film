from bs4 import BeautifulSoup
import json,re
import pandas as pd
import numpy as np
def list2str(value):
    if isinstance(value,list):
        value = ', '.join(value)
    return value
class rt_parser():
    '''
    html parser
    '''
    def parse_index(self, res):
        '''
        parser the all dvd index page of rotten tomato
        example: https://www.rottentomatoes.com/api/private/v2.0/browse?sortBy=release&type=dvd-streaming-all&page=312
        Args:
            res (binary): the content of requests response
        Return:
            boolen: parse success or not
            Dataframe (if success): the data in pandas dataframe format
        '''  
        data = json.loads(res)
        results = data.get('results')
        if not results:
            return False,
        else:
            dict_for_pandas = {'title':[], 'url':[], 'id':[], 'actors':[], 'dvdReleaseDate':[], 'mpaaRating':[], 'runtime':[], 'synopsis':[], 'synopsisType':[], 'theaterReleaseDate':[], 'tomatoIcon':[], 'tomatoScore':[]}
            for i in results:
                for j in dict_for_pandas.keys():
                    dict_for_pandas[j].append(i.get(j))
            df = pd.DataFrame(dict_for_pandas)
            for i in df.columns.tolist():
                df[i] = df[i].apply(list2str)
            return True, df
    def parse_page(self, url, res_content):
        '''
        parse the content page
        example: https://www.rottentomatoes.com/m/the_departure_2020
        Args:
            url (str): page url without domain, example: /m/the_departure_2020
            res_content(binary): the content of requests response
        Return:
            boolen: parse success or not
            Dataframe (if success): the data in pandas dataframe format 
        '''
        dict_for_pandas = {'url':[url], 'critics_percentage':[], 'critics_review_totals':[], 'audience_percentage':[], 'audience_review_totals':[], 'movieSynopsis':[]}
        soup = BeautifulSoup(res_content, 'html.parser')
#         contentReviews = soup.find('a', {'href':'#contentReviews'})
#         audience_reviews = soup.find('a', {'href': '#audience_reviews'})
        mop_ratings_wrap__half = soup.find_all('div', {'class': 'mop-ratings-wrap__half'})
        try:
            critics_percentage = mop_ratings_wrap__half[0].find('span', {'class': 'mop-ratings-wrap__percentage'}).get_text()
            critics_percentage = re.sub(r'\s', '', critics_percentage)
            critics_review_totals = mop_ratings_wrap__half[0].find('small', {'class':'mop-ratings-wrap__text--small'}).get_text()
            critics_review_totals = re.sub(r'\s','', critics_review_totals)
            dict_for_pandas['critics_percentage'].append(critics_percentage)
            dict_for_pandas['critics_review_totals'].append(critics_review_totals)
            audience_percentage = mop_ratings_wrap__half[1].find('span', {'class': 'mop-ratings-wrap__percentage'})
            if audience_percentage:
                audience_percentage = audience_percentage.get_text()
                audience_review_totals = mop_ratings_wrap__half[1].find('strong', {'class':'mop-ratings-wrap__text--small'}).get_text().replace('User Ratings: ', '')
                audience_percentage = re.sub(r'\s','',audience_percentage)
                audience_review_totals = re.sub(r'\s','',audience_review_totals)
                dict_for_pandas['audience_percentage'].append(audience_percentage)
                dict_for_pandas['audience_review_totals'].append(audience_review_totals)
            else:
                dict_for_pandas['audience_percentage'].append(np.nan)
                dict_for_pandas['audience_review_totals'].append(np.nan)
            
            movieSynopsis = soup.find('div', {'id':'movieSynopsis'}).get_text().strip('\n')
            dict_for_pandas['movieSynopsis'].append(movieSynopsis)

            content_meta_info = soup.find('ul', {'class':'content-meta info'})
            for li in content_meta_info.find_all('li'):
                tmp_label = li.find('div', {'class':'meta-label subtle'}).get_text()
                tmp_label = re.sub('[\s:]','',tmp_label)
                tmp_value = li.find('div', {'class':'meta-value'}).get_text()
                tmp_value = re.sub(r' ','#',tmp_value)
                tmp_value = re.sub(r'[\s]','',tmp_value)
                tmp_value = re.sub(r'#+',' ',tmp_value)
                dict_for_pandas[tmp_label] = [tmp_value]
                
            df = pd.DataFrame(dict_for_pandas)
            return True, df
        except:
            return False,
    def parse_critic_review(self, url, res_content):
        '''
        parse the critics comemnt page
        example: 
            https://www.rottentomatoes.com/m/vengeance_is_mine_1979/reviews
            https://www.rottentomatoes.com/m/to_the_stars/reviews?page=2
        Args:
            url (str): page url without domain, example: /m/the_departure_2020
            res_content(binary): the content of requests response
        Return:
            boolen: parse success or not
            Dataframe (if success): the data in pandas dataframe format 
        '''
        try:
            soup = BeautifulSoup(res_content, 'html.parser')
            review_table_row = soup.find_all('div', {'class':'row review_table_row'})
            dict_for_pandas = {'url':[],'critic_name':[],'critic_link':[],'publication':[],'top_critic':[], 'review_date':[], 'the_review':[], 'review_link':[], 'original_score':[]}
            for i in review_table_row:
                tmp_data = {'url':url}
                review_date = i.find('div', {'class':'review-date subtle small'}).get_text()
                review_date = re.sub(r'\s', '', review_date)
                tmp_data['review_date'] = review_date
                the_review = i.find('div', {'class': 'the_review'}).get_text()
                the_review = re.sub(' ', '#', the_review)
                the_review = re.sub(r'\s', '', the_review)
                the_review = re.sub(r'[#]+', ' ', the_review).strip()
                tmp_data['the_review'] = the_review 
                review_link = i.find('div', {'class':'small subtle review-link'})
                full_review_link_a = review_link.find('a')
                if full_review_link_a:
                    full_review_link = full_review_link_a['href']
                    tmp_data['review_link'] = full_review_link
                original_score = review_link.get_text()
                original_score = re.sub(r'[\s(Full Review)(| Original Score:)]','',original_score)
                tmp_data['original_score'] = original_score
                critic = i.find('a', {'class': 'unstyled bold articleLink'})
                critic_name = critic.get_text()
                critic_link = critic['href']
                tmp_data['critic_name'] = critic_name
                tmp_data['critic_link'] = critic_link
                publication = i.find('em', {'class':'subtle critic-publication'})
                if publication:
                    publication = publication.get_text()
                    tmp_data['publication'] = publication
                top_critic = i.find('span', {'class': 'glyphicon glyphicon-star'})
                if top_critic:
                    tmp_data['top_critic'] = 1
                else:
                    tmp_data['top_critic'] = 0

                for k in dict_for_pandas.keys():
                    dict_for_pandas[k].append(tmp_data.get(k))
            df = pd.DataFrame(dict_for_pandas)
            return True, df
        except:
            return False,
    def parse_critic_review_next(self, url, res_content):
        '''
        parse the critics comemnt next page
        example: 
            https://www.rottentomatoes.com/m/vengeance_is_mine_1979/reviews
            https://www.rottentomatoes.com/m/to_the_stars/reviews?page=2
        Args:
            url (str): page url without domain, example: /m/the_departure_2020
            res_content(binary): the content of requests response
        Return:
            boolen: have next page or not
            str (if success): the next page url link 
        '''
        soup = BeautifulSoup(res_content, 'html.parser')
        page_div = soup.find('div', {'style':'display:inline-block; float:right; padding-bottom:10px'})
        if page_div:
            page_box = page_div.find_all('a')
            nextpage = page_box[1]['href']
            if nextpage != '#':
                return True, nextpage
        return False,
