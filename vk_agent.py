import vk_api
from vk_api import VkUpload
import json
import os
import sys

# Paths to tokens (found in .openclaw/Keys)
GROUP_TOKEN_PATH = r'C:\Users\Igor\.openclaw\Keys\vk_group_token.txt'
USER_TOKEN_PATH = r'C:\Users\Igor\.openclaw\Keys\vk_token.txt' # Using vk_token.txt or vk_user_token.txt
GROUP_ID = 236370925

def load_token(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read().strip()
            # Remove prefix if present
            if 'VK_TOKEN=' in content:
                content = content.replace('VK_TOKEN=', '')
            return content
    return None

class VKAgent:
    def __init__(self):
        self.group_token = load_token(GROUP_TOKEN_PATH)
        self.user_token = load_token(USER_TOKEN_PATH)
        
        if not self.group_token:
            print(f"Error: Group token not found at {GROUP_TOKEN_PATH}")
            sys.exit(1)
            
        self.vk_group_session = vk_api.VkApi(token=self.group_token)
        self.vk_group = self.vk_group_session.get_api()
        
        # We need user session for wall/comment reading and PHOTO UPLOAD due to VK API restrictions
        if self.user_token:
            self.vk_user_session = vk_api.VkApi(token=self.user_token)
            self.vk_user = self.vk_user_session.get_api()
            self.upload = VkUpload(self.vk_user_session) # Upload via USER
        else:
            self.vk_user = self.vk_group # Fallback
            self.upload = VkUpload(self.vk_group_session)

    def get_recent_messages(self, count=5):
        """Fetches recent direct messages."""
        try:
            conversations = self.vk_group.messages.getConversations(count=count, filter='all')
            return conversations.get('items', [])
        except Exception as e:
            return f"Error fetching messages: {e}"

    def get_wall_comments(self, count=10):
        """Fetches recent comments on wall posts using USER token."""
        try:
            # Using vk_user for reading wall and comments
            posts = self.vk_user.wall.get(owner_id=-GROUP_ID, count=5)
            comments_all = []
            for post in posts.get('items', []):
                comments = self.vk_user.wall.getComments(owner_id=-GROUP_ID, post_id=post['id'], count=5, sort='desc')
                for c in comments.get('items', []):
                    c['post_id'] = post['id']
                    comments_all.append(c)
            return comments_all
        except Exception as e:
            return f"Error fetching comments: {e}"

    def post_to_wall(self, message, image_path=None):
        """Creates a post on the wall, optionally with an image."""
        attachment = None
        if image_path and os.path.exists(image_path):
            try:
                photo = self.upload.photo_wall(photos=image_path, group_id=GROUP_ID)
                attachment = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
            except Exception as e:
                print(f"Error uploading photo: {e}")
        
        try:
            res = self.vk_group.wall.post(
                owner_id=-GROUP_ID,
                message=message,
                attachments=attachment,
                from_group=1
            )
            return res
        except Exception as e:
            return f"Error posting to wall: {e}"

    def get_detailed_stats(self, count=10):
        """Fetches group subscribers and detailed wall stats (likes, views, etc.)."""
        stats = {
            "group_info": {},
            "posts": []
        }
        try:
            # 1. Get Group Info (subscribers/members)
            group_res = self.vk_group.groups.getById(group_id=GROUP_ID, fields='members_count,status,description')
            if group_res:
                stats["group_info"] = {
                    "id": group_res[0]['id'],
                    "name": group_res[0].get('name', ''),
                    "members_count": group_res[0].get('members_count', 0),
                    "status": group_res[0].get('status', ''),
                }

            # 2. Get Recent Posts with metrics
            posts_res = self.vk_user.wall.get(owner_id=-GROUP_ID, count=count)
            for item in posts_res.get('items', []):
                post_data = {
                    "id": item['id'],
                    "text": item['text'][:100] + '...' if len(item['text']) > 100 else item['text'],
                    "date": item['date'],
                    "likes": item.get('likes', {}).get('count', 0),
                    "comments": item.get('comments', {}).get('count', 0),
                    "reposts": item.get('reposts', {}).get('count', 0),
                    "views": item.get('views', {}).get('count', 0)
                }
                stats["posts"].append(post_data)
            
            return stats
        except Exception as e:
            return {"error": str(e)}

    def send_message(self, peer_id, text):
        """Sends a direct message."""
        from vk_api.utils import get_random_id
        try:
            self.vk_group.messages.send(
                peer_id=peer_id,
                message=text,
                random_id=get_random_id()
            )
            return "Success"
        except Exception as e:
            return f"Error sending message: {e}"

    def reply_to_comment(self, owner_id, post_id, comment_id, text):
        """Replies to a specific comment on the wall."""
        try:
            res = self.vk_group.wall.createComment(
                owner_id=owner_id,
                post_id=post_id,
                reply_to_comment=comment_id,
                message=text,
                from_group=GROUP_ID # Posting as the group
            )
            return res
        except Exception as e:
            return f"Error replying to comment: {e}"

if __name__ == "__main__":
    import time
    # Internal CLI for Antigravity to use
    agent = VKAgent()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            stats = agent.get_detailed_stats(5)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        elif cmd == "post":
            # Call: python vk_agent.py post "Message or FilePath" "Optional Image Path"
            input_val = sys.argv[2]
            img = sys.argv[3] if len(sys.argv) > 3 else None
            
            # Check if input is a path to a text file
            if os.path.exists(input_val) and input_val.endswith('.txt'):
                with open(input_val, 'r', encoding='utf-8') as f:
                    msg = f.read()
            else:
                msg = input_val
                
            res = agent.post_to_wall(msg, img)
            print(json.dumps(res, indent=2, ensure_ascii=False))
        elif cmd == "comment":
            # Call: python vk_agent.py comment owner_id post_id comment_id "Text"
            owner_id = int(sys.argv[2])
            post_id = int(sys.argv[3])
            comment_id = int(sys.argv[4])
            text = sys.argv[5]
            print(agent.reply_to_comment(owner_id, post_id, comment_id, text))
    else:
        print("VK Agent Bridge ready.")

