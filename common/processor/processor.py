import pandas as pd

# Purpose: This class provides static methods for data preprocessing tasks, such as 
# standardizing column names, converting date formats to UTC, and extracting additional 
# date-related features for analysis.
class Processor(object):

    # Purpose: Converts column names to lowercase and replaces spaces with underscores 
    # to standardize the format.
    # Inputs:
    # - data (DataFrame): A Pandas DataFrame containing the data to be processed.
    # Returns:
    # - The DataFrame with updated column names.
    @staticmethod
    def lower_column(data):
        for col in data.columns:
            data = data.rename(columns={col: col.replace(" ", "_").lower()})
        return data
    
    # Purpose: Converts the "date" column in the DataFrame to a UTC datetime format and normalizes 
    # the time to midnight for consistency.
    # Inputs:
    # - data (DataFrame): A Pandas DataFrame containing a "date" column in string format.
    # Returns:
    # - The DataFrame with the "date" column converted to UTC datetime format.
    @staticmethod
    def utc_date(data):
        data["date"] = pd.to_datetime(data["date"], utc=True).dt.normalize()
        return data
    
    # Purpose: Adds new columns to the DataFrame based on the "date" column, including year, month, 
    # quarter, and ISO week for enhanced temporal analysis.
    # Inputs:
    # - data (DataFrame): A Pandas DataFrame containing a "date" column in datetime format.
    # Returns:
    # - The DataFrame with additional date-related columns: "year", "month", "quarter", "week".
    @staticmethod
    def additional_date_columns(data):
        data["year"] = data["date"].dt.year
        data["month"] = data["date"].dt.month
        data["quarter"] = data["date"].dt.quarter
        data["week"] = data["date"].dt.isocalendar().week
        data["day"] = data["date"].dt.dayofyear
        data["weekday"] = data["date"].dt.weekday
        return data