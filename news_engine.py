import time
import random
from datetime import datetime
import db_manager

# --- Mock Constants ---
MOCK_HEADLINES = [
    "Lakers Secure Tight Win Over Warriors",
    "Mbappe Set to Join Real Madrid This Summer",
    "Novak Djokovic Advances to Australian Open Final",
    "Ferrari Unveils 2026 F1 Car Concept",
    "Caitlin Clark Breaks WNBA Scoring Record"
]

MOCK_SUMMARIES = [
    "In a thrilling encounter at the Crypto.com Arena, the Lakers edged out the Warriors 112-110.",
    "The transfer saga finally comes to an end as reports confirm Mbappe has signed a pre-contract.",
    "The world number one showed dominance in the semi-final, winning in straight sets.",
    "The Italian team reveals a radical new design aimed at reclaiming the championship title.",
    "The rookie sensation continues to rewrite history books with a 45-point performance."
]

def fetch_rss_news():
    """Mocks fetching news from RSS feeds."""
    print("Fetching news from RSS feeds...")
    # Simulate network delay
    time.sleep(1)
    
    news_items = []
    for i in range(3):
        idx = random.randint(0, len(MOCK_HEADLINES) - 1)
        news_items.append({
            "title": MOCK_HEADLINES[idx],
            "url": f"https://example.com/sports-news-{random.randint(1000, 9999)}"
        })
    return news_items

def generate_ai_content(original_title):
    """Mocks generating AI rewritten content and status."""
    print(f"Generating AI content for: {original_title}")
    # Simulate AI processing
    time.sleep(1.5)
    
    idx = random.randint(0, len(MOCK_SUMMARIES) - 1)
    rewritten_summary = f"AI BREAKING: {MOCK_SUMMARIES[idx]} (Rewritten from '{original_title}')"
    
    # Mock image path (in a real app, this would be a path to a generated file)
    mock_image_url = f"https://picsum.photos/seed/{random.randint(1, 1000)}/800/600"
    
    return rewritten_summary, mock_image_url

def post_to_facebook(item_id, content, image_url):
    """Mocks posting to Facebook API."""
    print(f"Posting item {item_id} to Facebook...")
    # Simulate API call
    time.sleep(2)
    
    # In a real scenario, you'd use requests to hit FB Graph API
    # requests.post(f"https://graph.facebook.com/v19.0/me/feed", data={...})
    
    return True

def trigger_news_workflow(auto_post=False):
    """Orchestrates the fetching, generating, and saving process."""
    raw_news = fetch_rss_news()
    
    for item in raw_news:
        summary, image_path = generate_ai_content(item['title'])
        
        status = 'posted' if auto_post else 'pending'
        
        db_manager.add_news_item(
            title=item['title'],
            summary=summary,
            image_path=image_path,
            url=item['url'],
            status=status
        )
        
        if status == 'posted':
            # Get the newly added item's ID (this is simplified)
            # In a real app, get the ID from the cursor after insertion
            print(f"Automatically posted: {item['title']}")
            # In this mock, we just proceed as if it's posted

    return len(raw_news)

if __name__ == "__main__":
    # Test workflow
    count = trigger_news_workflow(auto_post=False)
    print(f"Processed {count} news items.")
