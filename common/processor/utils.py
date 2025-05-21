import uuid
import time

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
        # Use the current time in milliseconds
        timestamp = int(time.time() * 1000)
        
        # Generate a UUID4 string and take the first 8 characters
        unique_id = str(uuid.uuid4())[:8]
        
        # Combine prefix, timestamp, and unique identifier
        client_order_id = f"{prefix}_{timestamp}_{unique_id}"
        return client_order_id