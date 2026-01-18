import time
import random
import os
import urllib.parse
from datetime import datetime
import db_manager
import feedparser
import google.generativeai as genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json
import image_processor


# Load environment variables
load_dotenv()

# --- Constants ---
RSS_FEED_URL = "https://cointelegraph.com/rss"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")


def clean_html(html_content):
    """Removes HTML tags from the string."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_rss_news():
    """Fetches news from Cointelegraph RSS feed."""
    print(f"Fetching news from {RSS_FEED_URL}...")
    
    feed = feedparser.parse(RSS_FEED_URL)
    
    if feed.bozo:
        print("Error parsing RSS feed")
        return []
    
    news_items = []
    # Fetch top 10 items for AI selection
    for entry in feed.entries[:10]:
        
        # Try to find an existing image or use placeholder
        image_url = "https://via.placeholder.com/1024x1024?text=News+Image"
        
        if 'media_content' in entry:
            image_url = entry.media_content[0]['url']
        elif 'links' in entry:
            for link in entry.links:
                if link.get('type') in ['image/jpeg', 'image/png']:
                    image_url = link['href']
                    break
        
        # Clean the summary
        clean_summary = clean_html(entry.summary)

        news_items.append({
            "title": entry.title,
            "url": entry.link,
            "summary": clean_summary,
            "published": entry.published,
            "image_url": image_url
        })
        
    print(f"Fetched {len(news_items)} items.")
    return news_items

def select_interesting_news(news_items, top_n=3):
    """
    Uses Gemini AI to select the most interesting news items.
    Returns: List of top N interesting news items
    """
    if not GEMINI_API_KEY or not news_items:
        # Fallback: return first N items
        return news_items[:top_n]
    
    print(f"Using Gemini AI to select top {top_n} interesting news...")
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a prompt with all news items
        news_list = ""
        for i, item in enumerate(news_items, 1):
            news_list += f"{i}. {item['title']}\n   Summary: {item['summary'][:150]}...\n\n"
        
        prompt = f"""
        You are a crypto news curator for a Thai audience interested in blockchain and cryptocurrency.
        
        From the following {len(news_items)} news items, select the top {top_n} most interesting and important stories.
        Consider: impact, relevance, novelty, and reader interest.
        
        News Items:
        {news_list}
        
        Return ONLY a JSON array of the numbers (1-{len(news_items)}) of the top {top_n} stories.
        Example: [3, 7, 1]
        """
        
        response = model.generate_content(prompt)
        
        # Parse response
        selected_indices = json.loads(response.text.strip())
        
        # Convert to 0-indexed and get selected items
        selected_news = [news_items[idx - 1] for idx in selected_indices if 1 <= idx <= len(news_items)]
        
        print(f"Selected {len(selected_news)} interesting news items")
        return selected_news[:top_n]
        
    except Exception as e:
        print(f"AI selection error: {e}")
        # Fallback
        return news_items[:top_n]

def generate_thai_content(original_title, original_summary):
    """
    Uses Gemini to generate Thai headline and content.
    Returns: (thai_headline, thai_content)
    """
    if not GEMINI_API_KEY:
        return f"[NO KEY] {original_title}", f"[NO KEY] {original_summary}"
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        คุณเป็นนักเขียนข่าว crypto/blockchain สำหรับชาวไทย
        
        ข่าวต้นฉบับ (ภาษาอังกฤษ):
        หัวข้อ: {original_title}
        สรุป: {original_summary}
        
        กรุณาสร้าง:
        1. HEADLINE: หัวข้อภาษาไทยสั้นๆ กระชับ น่าสนใจ (ไม่เกิน 50 ตัวอักษร)
        2. CONTENT: เนื้อหาภาษาไทยที่ละเอียด อ่านง่าย เข้าใจง่าย น่าสนใจ สำหรับโพสต์ Facebook 
           - ยาว 200-300 คำ
           - อธิบายรายละเอียดให้ครบถ้วน
           - มีข้อมูลที่น่าสนใจ
           - เหมาะสำหรับคนที่สนใจ crypto
        
        ตอบกลับในรูปแบบ JSON:
        {{
          "headline": "หัวข้อภาษาไทย",
          "content": "เนื้อหาภาษาไทยแบบยาว ละเอียด"
        }}
        """
        
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        
        return result.get("headline", original_title), result.get("content", original_summary)
        
    except Exception as e:
        print(f"Thai content generation error: {e}")
        return f"[ERROR] {original_title}", f"[ERROR] {original_summary}"

def process_news_item(news_item):
    """
    Processes a single news item: generates Thai content and branded image.
    Returns: (thai_headline, thai_content, image_path)
    """
    print(f"Processing: {news_item['title']}")
    
    # Generate Thai content
    thai_headline, thai_content = generate_thai_content(news_item['title'], news_item['summary'])
    
    # Create branded image with Thai headline
    image_path = None
    try:
        image_path = image_processor.add_headline_to_image(
            news_item['image_url'],
            thai_headline,
            output_path=None  # Auto-generate path
        )
        print(f"Generated branded image: {image_path}")
    except Exception as e:
        print(f"Image processing error: {e}")
        # Fallback to original image
        image_path = news_item['image_url']
    
    return thai_headline, thai_content, image_path

def trigger_news_workflow(auto_post=False):
    """Orchestrates the enhanced news workflow."""
    # 1. Fetch news
    raw_news = fetch_rss_news()
    
    if not raw_news:
        print("No news fetched")
        return 0
    
    # 2. AI selects interesting news
    selected_news = select_interesting_news(raw_news, top_n=3)
    
    # 3. Process each selected item
    count = 0
    for item in selected_news:
        try:
            thai_headline, thai_content, image_path = process_news_item(item)
            
            # Rate limiting for Gemini Free Tier
            if GEMINI_API_KEY:
                time.sleep(20)  # Conservative delay for free tier
            
            status = 'posted' if auto_post else 'pending'
            
            db_manager.add_news_item(
                title=thai_headline,  # Use Thai headline as title
                summary=thai_content,  # Thai content as summary
                image_path=image_path,  # Branded image path
                url=item['url'],
                status=status
            )
            count += 1
            
        except Exception as e:
            print(f"Error processing news item: {e}")
            continue
        
    return count

if __name__ == "__main__":
    count = trigger_news_workflow(auto_post=False)
    print(f"Processed {count} news items.")

