import pandas as pd

class Processor(object):

    @classmethod
    def lower_column(self,data):
        for col in data.columns:
            data.rename(columns={col:col.replace(" ","_").lower()},inplace=True)
        return data
       
    @staticmethod
    def utc_date(self,data):
        data["date"] = pd.to_datetime(data["date"],utc=True).dt.normalize()
        return data
    
    @staticmethod
    def additional_date_columns(data):
        data["year"] = data["date"].dt.year
        data["month"] = data["date"].dt.month
        data["quarter"] = data["date"].dt.quarter
        data["week"] = data["date"].dt.isocalendar().week
        return data