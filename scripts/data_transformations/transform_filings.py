## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

import pandas as pd
from common.database.adatabase import ADatabase
from tqdm import tqdm
from difflib import SequenceMatcher
import re
import spacy

# Load spaCy's language model for word similarity
nlp = spacy.load("en_core_web_md")
## Define Database
sec = ADatabase("sec")

keywords = ["assets","liabilities","dividend","currentassets","currentliabilities","netincome","expense","revenue","commonstock"]
# Optimized function with external cache
def create_column_mappings(column_names, cache, threshold=0.85):
    mappings = {}
    column_names =  [re.sub(r'\d+', '', col).lower().replace(" ","_") for col in column_names if len(col) < 16]  # Filter out already cached names
    column_names.sort()
    for col in column_names:
        # If column is already in cache, reuse the standardized name
        score = 0
        for keyword in keywords:
            if keyword in col:
                score +=1
        if score > 0:
            if col in cache:
                mappings[col] = cache[col]
                continue

            col_doc = nlp(col)

            # Compare semantic similarity against existing standardized names
            for existing_name in keywords:
                existing_doc = nlp(existing_name)
                similarity = col_doc.similarity(existing_doc)
                if similarity >= threshold:
                    mappings[col] = existing_name
                    break
    return mappings


sec.connect()
sec.drop("filings")
col_mappings = {}
for year in tqdm(range(2012,2025)):
    for quarter in range(1,5):
        try:
            folder = f"./sec/{year}q{quarter}/"
            num = pd.read_csv(folder+"num.txt", quotechar='"',sep="\t",engine="c",low_memory=False,encoding="utf-8")
            num["tag"] = [str(x).lower() for x in num["tag"]]
            col_mappings = create_column_mappings(list(num["tag"].unique()),col_mappings,threshold=0.7)
            num = num[num["tag"].isin(col_mappings.keys())]
            num["tag"] = [col_mappings[x] for x in num["tag"]]
            num = num.pivot_table(index="adsh",columns="tag",values="value")
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