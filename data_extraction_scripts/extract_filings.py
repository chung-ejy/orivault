import pandas as pd
from database.adatabase import ADatabase
from processor.processor import Processor as p
from tqdm import tqdm
sec = ADatabase("sec")

sec.connect()
sec.drop("filings")
for year in tqdm(range(2013,2025)):
    for quarter in range(1,5):
        try:
            folder = f"./sec/{year}q{quarter}/"
            num = pd.read_csv(folder+"num.txt", quotechar='"',sep="\t",engine="c",low_memory=False,encoding="utf-8")
            num["tag"] = [str(x).lower() for x in num["tag"]]
            num.replace("totalassets","assets",inplace=True)
            num.replace("totalliabilities","liabilities",inplace=True)
            num.replace("totalassets1","assets",inplace=True)
            num.replace("totalliabilities1","liabilities",inplace=True)
            num.replace("assets1","assets",inplace=True)
            num.replace("liabilities1","liabilities",inplace=True)
            num.replace("liabilitiestotal","liabilities",inplace=True)
            num.replace("assetstotal","assets",inplace=True)
            num.replace("netassets","assets",inplace=True)
            num.replace("assetsnet","assets",inplace=True)
            num.replace("netliabilities","liabilities",inplace=True)
            num.replace("liabilitiesnet","liabilities",inplace=True)
            included = ["assets","liabilities","netincomeloss"]
            num = num[num["tag"].isin(included)].pivot_table(index="adsh",columns="tag",values="value")
            sub = pd.read_csv(folder+"sub.txt", quotechar='"',sep="\t",engine="c",low_memory=False,encoding="utf-8")[["adsh","cik","filed"]]
            sub["cik"] = [int(x) for x in sub["cik"]]
            filing = num.merge(sub,on="adsh",how="left")
            filing["date"] = pd.to_datetime(filing["filed"],format="%Y%m%d")
            filing["year"] = year
            filing["quarter"] = quarter
            filing.drop(["filed","adsh"],axis=1,inplace=True)
            sec.store("filings",filing)
        except Exception as e:
            print(year,quarter,str(e))
sec.create_index("filings","cik")
sec.disconnect()