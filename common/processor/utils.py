import uuid
import time
from datetime import datetime, timedelta, time as dtime

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
        Return:
        - 15 minutes before market close if it's after 4:00 PM or a weekend
        - 15 minutes before now if the market is currently open
        - Otherwise, 15 minutes before prior market close, pushed back one day unless it's a weekend
        """
        if ref_date is None:
            ref_date = datetime.now()

        market_open = dtime(hour=9, minute=30)
        market_close = dtime(hour=16, minute=0)
        fifteen_minutes = timedelta(minutes=15)

        # If it's weekend, roll back to last weekday
        while ref_date.weekday() > 4:  # Saturday = 5, Sunday = 6
            ref_date -= timedelta(days=1)

        current_time = ref_date.time()

        # If after market close today, return 15 minutes before today's close
        if current_time >= market_close:
            final_date = ref_date.replace(hour=15, minute=45, second=0, microsecond=0)

        # If during market hours and after 9:45 AM, return 15 minutes before now
        elif current_time >= (datetime.combine(ref_date.date(), market_open) + fifteen_minutes).time():
            final_date = ref_date - fifteen_minutes

        # If it's before 9:45 AM, go to prior market day's close
        else:
            prev_day = ref_date - timedelta(days=1)
            while prev_day.weekday() > 4:
                prev_day -= timedelta(days=1)
            final_date = prev_day.replace(hour=15, minute=45, second=0, microsecond=0)

        # Push the final date back one day unless it's a weekend
        if final_date.weekday() <= 4:  # Monday to Friday
            final_date -= timedelta(days=1)

        return final_date
