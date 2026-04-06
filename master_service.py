import vk_api
from vk_api import VkUpload
import requests
import os
import json
from news_service import NewsService # Ensure news_service.py is in the same directory

# Configuration
GROUP_TOKEN = 'YOUR_GROUP_TOKEN'
GROUP_ID = 'YOUR_GROUP_ID'

class MasterService:
    def __init__(self, token, group_id):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.upload = VkUpload(self.vk_session)
        self.group_id = int(group_id)
        self.news_service = NewsService()

    def upload_photo_to_wall(self, file_path):
        """Uploads a photo to VK wall and returns the attachment string."""
        photo = self.upload.photo_wall(
            photos=file_path,
            group_id=self.group_id
        )
        return f"photo{photo[0]['owner_id']}_{photo[0]['id']}"

    def create_post_with_news(self, news_item):
        """Creates a VK post from news item, including an image if available."""
        message = self.news_service.summarize_news(news_item)
        
        # In a real workflow:
        # 1. Ask the AI agent (me) to generate an image based on news_item['title']
        # 2. Save the image to a file
        # 3. Upload the image to VK
        
        # Placeholder for image generation logic:
        image_path = f"post_image_{int(time.time())}.jpg"
        # In this master script, we'll assume the image has been generated and saved locally
        
        attachment = None
        if os.path.exists(image_path):
            attachment = self.upload_photo_to_wall(image_path)
        
        try:
            self.vk.wall.post(
                owner_id=-self.group_id,
                message=message,
                attachments=attachment
            )
            print(f"Post created successfully for: {news_item['title']}")
        except Exception as e:
            print(f"Error creating post: {e}")

if __name__ == "__main__":
    import time
    service = MasterService(GROUP_TOKEN, GROUP_ID)
    
    # Example execution Loop
    while True:
        print("Checking for news...")
        latest_news = service.news_service.fetch_latest_news()
        if latest_news:
            for item in latest_news:
                # To avoid spam, only post the most recent or filter them
                print(f"Processing: {item['title']}")
                service.create_post_with_news(item)
                # Mark as seen to avoid duplicates
                service.news_service.seen_guids.add(item['link'])
                time.sleep(3600) # Wait an hour between posts
        else:
            print("No news. Sleeping for 1 hour.")
            time.sleep(3600)
