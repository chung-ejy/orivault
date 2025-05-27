import uuid
import time
from datetime import datetime, timedelta, time as dtime
import holidays
class Utils(object):

    @staticmethod
    def generate_client_order_id(prefix: str = "order") -> str:
        """
        Generate a unique client_order_id for Coinbase Advanced API.
        
        Parameters:
            prefix (str): An optional prefix to identify the order type or purpose.
        
        Returns:
            str: A unique client_order_id.
        """
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        client_order_id = f"{prefix}_{timestamp}_{unique_id}"
        return client_order_id


    @staticmethod
    def last_weekday(ref_date=None):
        """
        Returns:
        - The previous market close (4:00 PM on the last trading day),
          skipping weekends and bank holidays.
        """
        if ref_date is None:
            ref_date = datetime.now()

        us_holidays = holidays.US()  # List of US federal holidays

        # Roll back to last weekday if it's a weekend
        while ref_date.weekday() > 4 or ref_date in us_holidays:
            ref_date -= timedelta(days=1)

        # Move to the previous market close, ensuring no holidays
        prev_close = ref_date - timedelta(days=1)
        while prev_close.weekday() > 4 or prev_close in us_holidays:
            prev_close -= timedelta(days=1)

        # Set the previous close time to 4:00 PM
        final_date = prev_close.replace(hour=16, minute=0, second=0, microsecond=0)
        return final_date

