from datetime import datetime
import pdfplumber
import pandas as pd
import re



class Extractor:
    def __init__(self,pdf) -> None:
        self.__pdf=pdf

    __columns=['Order No.','OrderTime','TradeNo.','TradeTime',
                'Security/ContractDescription','Buy(B) /Sell(S)','Quantity','Gross Rate/trade price per Unit(Rs)','Brokerage perUnit','NetRate perUnit(Rs)','ClosingRatePerUnit(Rs)'
                ,'NetTotal(BeforeLevies)(Rs.)','remark','Symbol','ISIN','Total Buy','Total Sell'
                ]
    __symbolRegex="[:][0-9]+"
    __ISINRegex="[:]\s[A-Z0-9]+\s[a-zA-Z]+"
    __BuySellRegex="[0-9]*\s[@]\s[0-9]+[.][0-9]*\s[=]\s[0-9]*[.][0-9]*\s[a-zA-Z]*[:]\s[0-9]*[.][0-9]*"


    def __findSymbol(self,target)->list:
        return re.findall(self.__symbolRegex,target)

    def __findISIN(self,target)->list:
        return re.findall(self.__ISINRegex,target)

    def __findBuySell(self,arr)->list:
        return [i for i in arr if i is not None and re.findall(self.__BuySellRegex,i)]

    def __isData(self,arr)->bool:
        if (len(arr)<4 or not arr[2]):
            return False
        res=False
        try:
            datetime.strptime(arr[2],"%H:%M:%S")
            res=True
        except ValueError:
            return False
        return arr[0].isdigit() and len(arr[0])>=8 and res

    def __removeNone(self,array)->list:
        return [i for i in array if i is not None]

    def __createOrganizedDf(self,page:list=[])->pd.DataFrame:
        row=[]
        temp=[]
        for elem in page:
            ISIN=self.__findISIN(elem[0])
            Symbol=self.__findSymbol(elem[0])
            buySell=self.__findBuySell(elem)
            if len(Symbol)==1:
                temp+=Symbol
            if len(ISIN)==1:
                temp+=ISIN
            elif len(buySell)>0:
                if (temp[5]=="B"):
                    temp+=[buySell[0],None]
                else:
                    temp+=[None,buySell[0]]
            elif self.__isData(elem):
                temp=self.__removeNone(elem)+temp
            if len(temp)==17:
                row.append(temp)
                temp=[]
        df=pd.DataFrame(row,columns=self.__columns)
        return df

    def __dataFrameResult(self)->pd.DataFrame:
        pdf=pdfplumber.open(self.__pdf)
        pages=[]
        for i in pdf.pages:
            pages+=i.extract_table()
        # remove the headers and useless data
        del pages[0][0:2]
        return self.__createOrganizedDf(page=pages)

    Frame=__dataFrameResult