import requests

from time import sleep
from pandas import read_html, concat
from fake_useragent import UserAgent

class TaiwanStock:
    def __init__(self):
        self.temp = 0
    
    def getStockList(self, filename='stockList.csv'):
        # 從 <https://isin.twse.com.tw/isin/C_public.jsp?strMode=2> 抓取台灣上市股票清單
        headers = self.getHeaders()
        url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
        res = requests.get(url, headers=headers)
        df1 = read_html(res.text, encoding='big5hkscs')[0]
        df1.columns = df1.iloc[0]
        df1 = df1.drop('備註', axis=1)
        df1.columns = ['股票代號及名稱', 'ISIN Code', '上市日', '市場別', '產業別', '類型']
        df1 = df1.drop(df1[(df1.市場別!='上市')].index)
        df1.loc[df1['類型'].str.contains('RW'), '類型'] = '上市認購(售)權證'
        
        sleep(10)

        # 從 <https://isin.twse.com.tw/isin/C_public.jsp?strMode=4> 抓取台灣上櫃股票清單
        headers = self.getHeaders()
        url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=4'
        res = requests.get(url, headers=headers)
        df2 = read_html(res.text, encoding='big5hkscs')[0]
        df2.columns = df2.iloc[0]
        df2 = df2.drop('備註', axis=1)
        df2.columns = ['股票代號及名稱', 'ISIN Code', '上市日', '市場別', '產業別', '類型']
        df2 = df2.drop(df2[(df2.市場別)!='上櫃'].index)
        df2.loc[df2['類型'].str.contains('RW'), '類型'] = '上櫃認購(售)權證'

        # 合併上市股票清單(df1)與上櫃股票清單(df2)
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
        df.loc[df['類型'].str.contains('EPN'), '類型'] = '特別股'
        
        # 將上市櫃股票清單存成一個 CSV 檔
        df.to_csv(filename)
        print('[INFO] <{}> 已儲存至您的當前目錄。'.format(filename))

        return df
    
    def getHeaders(self):
        ua = UserAgent()
        user_agent = ua.random
        headers = {'user-agent': user_agent}
        
        return headers