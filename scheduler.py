import schedule
import time
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import news_engine
import db_manager

load_dotenv()

def post_news():
    """
    Scheduled job to fetch and post news automatically.
    Runs at 9am, 3pm, and 9pm daily.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"🤖 AUTO-POST TRIGGERED at {current_time}")
    print(f"{'='*60}\n")
    
    try:
        # Run the news workflow with auto_post=True
        count = news_engine.trigger_news_workflow(auto_post=True)
        
        print(f"\n✅ Successfully processed and posted {count} news items")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error during auto-post: {e}")
        print(f"{'='*60}\n")

def run_scheduler():
    """
    Sets up and runs the scheduler for automatic posting.
    Posts 3 times daily: 9am, 3pm (15:00), 9pm (21:00)
    """
    # Schedule jobs
    schedule.every().day.at("09:00").do(post_news)
    schedule.every().day.at("15:00").do(post_news)
    schedule.every().day.at("21:00").do(post_news)
    
    print("\n" + "="*60)
    print("📅 SCHEDULER STARTED")
    print("="*60)
    print("⏰ Auto-posting schedule:")
    print("   - 09:00 (9am)")
    print("   - 15:00 (3pm)")
    print("   - 21:00 (9pm)")
    print("="*60 + "\n")
    print("Press Ctrl+C to stop the scheduler\n")
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("🛑 Scheduler stopped by user")
        print("="*60 + "\n")
        sys.exit(0)
