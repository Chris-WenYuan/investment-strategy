import os
import requests
import datetime

from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup
from pandas_datareader import data
from pandas import read_html, concat, DataFrame, set_option
from fake_useragent import UserAgent

set_option('display.unicode.ambiguous_as_wide', True)
set_option('display.unicode.east_asian_width', True)

"""Crawl taiwan stock list"""
def getStockList():
    print('[crawler.getStockList] 正在抓取台灣上市上櫃股票清單......')

    # Crawl taiwan listed company list from <https://isin.twse.com.tw/isin/C_public.jsp?strMode=2>
    headers = _getHeaders()
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    res = requests.get(url, headers=headers)
    df1 = read_html(res.text, encoding='big5hkscs')[0]
    df1.columns = df1.iloc[0]
    df1 = df1.drop('備註', axis=1)
    df1.columns = ['股票代號及名稱', 'ISIN Code', '上市日', '市場別', '產業別', '類型']
    df1 = df1.drop(df1[(df1.市場別!='上市')].index)
    df1.loc[df1['類型'].str.contains('RW'), '類型'] = '上市認購(售)權證'

    sleep(5)

    # Crawl taiwan OCT company list from <https://isin.twse.com.tw/isin/C_public.jsp?strMode=4>
    headers = _getHeaders()
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=4'
    res = requests.get(url, headers=headers)
    df2 = read_html(res.text, encoding='big5hkscs')[0]
    df2.columns = df2.iloc[0]
    df2 = df2.drop('備註', axis=1)
    df2.columns = ['股票代號及名稱', 'ISIN Code', '上市日', '市場別', '產業別', '類型']
    df2 = df2.drop(df2[(df2.市場別)!='上櫃'].index)
    df2.loc[df2['類型'].str.contains('RW'), '類型'] = '上櫃認購(售)權證'

    # Merge listed company list (df1) and OCT company list (df2)
    df = concat([df1, df2])
    df['股票代號'] = df['股票代號及名稱'].map(lambda x:x.split('　')[0])
    df['股票名稱'] = df['股票代號及名稱'].map(lambda x:x.split('　')[-1])
    df = df[['股票代號', '股票名稱', 'ISIN Code', '上市日', '市場別', '產業別', '類型']]
    df.reset_index(inplace=True, drop=True)
    df.loc[df['類型'].str.contains('ES'), '類型'] = '股票'
    df.loc[df['類型'].str.contains('CMX'), '類型'] = 'ETN'
    df.loc[df['類型'].str.contains('CEO'), '類型'] = 'ETF'
    df.loc[df['類型'].str.contains('EDS'), '類型'] = '臺灣存託憑證(TDR)'
    df.loc[df['類型'].str.contains('CBC'), '類型'] = '受益證券-不動產投資信託'
    df.loc[df['類型'].str.contains('DA'), '類型'] = '受益證券-資產基礎證券'
    df.loc[df['類型'].str.contains('EP'), '類型'] = '特別股'
    df = df.set_index('股票代號')

    filename = 'stockList.csv'
    base_path = os.path.join(os.path.abspath(os.getcwd()), 'data')
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    file_path = os.path.join(base_path, filename)
    df.to_csv(file_path)

    print('[crawler.getStockList] 上市櫃股票股票清單儲存至 {}'.format(file_path))
    print('[crawler.getStockList] 完成\n')

    return df

"""Get taiwan stock history"""
def getAllStockHistory(df, markets, types):
    print('[crawler.getAllStockHistory] 正在抓取全部個股的歷史紀錄......')

    if '上市' in markets:
        print('[crawler.getAllStockHistory] 開始抓取上市股票(類型={})的歷史紀錄'.format(types))
        result_df = df[(df['市場別']=='上市') & (df['類型'].isin(types))]
        sid = list(result_df.index)
        listed_date = df['上市日'].tolist()
        _fetchAll(sid, listed_date, market='.TW')
        
    if '上櫃' in markets:
        print('[crawler.getAllStockHistory] 開始抓取上櫃股票(類型={})的歷史紀錄'.format(types))
        result_df = df[(df['市場別']=='上櫃') & (df['類型'].isin(types))]
        sid = list(result_df.index)
        listed_date = df['上市日'].tolist()
        _fetchAll(sid, listed_date, market='.TWO')
    
    print('[crawler.getAllStockHistory] 完成\n')

'''
"""Get stock real time information"""
def getRealTime(sid):
    result = []
    
    while True:
        result = []
        for stock_numbers in sid:
            response = requests.get('https://tw.stock.yahoo.com/q/q?s=' + stock_numbers)
            soup = BeautifulSoup(response.text.replace('加到投資組合', ''), 'lxml')
            stock_date = soup.find('font', {'class', 'tt'}).getText().strip()[-9:]
            tables = soup.find_all('table')[2]
            tds = tables.find_all('td')[0:11]
            result.append((stock_date,) + tuple(td.getText().strip() for td in tds))

            sleep(1)
        
        df = DataFrame(result, columns=['日期', '股票代號', '時間', '成交', '買進', '賣出', '漲跌', '張數', '昨收', '開盤', '最高', '最低'])
        print(df)

    return result
'''

"""Get fake web headers"""
def _getHeaders():
    ua = UserAgent()
    user_agent = ua.random
    headers = {'user-agent': user_agent}
    return headers

"""Fetch all stock history of specific market"""
def _fetchAll(sid, listed_date, market):
    base_path = ''

    for i in tqdm(range(len(sid)), desc='[crawler._fetchAll]'):
        try:
            start_date = listed_date[i].replace('/', '-')
            if int(start_date.split('-')[0]) < 2000:
                start_date = '2000-01-01'
            end_date = datetime.date.today()

            df = data.get_data_yahoo(sid[i]+market, start_date, end_date)

            filename = '{}.csv'.format(sid[i])
            base_path = os.path.join(os.path.abspath(os.getcwd()), 'data', 'history')
            if not os.path.exists(base_path):
                os.mkdir(base_path)
            file_path = os.path.join(base_path, filename)
            df.to_csv(file_path)

        except Exception as e:
            pass

        sleep(0.1)
    
    print('[crawler._fetchAll] 個股歷史紀錄已儲存至 {}'.format(base_path))