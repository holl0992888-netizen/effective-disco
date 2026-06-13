import os
import urllib.parse

class PayManager:
    def __init__(self):
        self.pid = os.getenv("AFFILIATE_PID", "default_shop")

    def generate_affiliate_link(self, original_url: str) -> str:
        """
        Універсальний механізм конвертації посилань у реферальні для CPA-мереж.
        """
        if not original_url:
            return "https://aliexpress.com"
        
        clean_url = original_url.split('?')[0]
        encoded_url = urllib.parse.quote_plus(clean_url)
        
        if "aliexpress" in clean_url.lower():
            return f"https://aliexpress.com{self.pid}&to={encoded_url}"
        
        return f"{clean_url}?utm_source=tg_channel&utm_medium=auto_bot&utm_campaign={self.pid}"
