import streamlit as st
import pandas as pd
from datetime import datetime
import db_manager
import news_engine

# Set page config
st.set_page_config(page_title="AI News Automation Dashboard", layout="wide")

# --- Initialize DB ---
db_manager.init_db()

# --- Sidebar ---
st.sidebar.title("Settings")
st.sidebar.markdown("---")

if st.sidebar.button("🚀 Trigger AI Fetch Now"):
    with st.spinner("Fetching and generating news..."):
        count = news_engine.trigger_news_workflow(auto_post=False) # Default to false for UI feedback
        st.sidebar.success(f"Added {count} new items!")
        st.rerun()

auto_post_mode = st.sidebar.checkbox("Auto-Post Mode", value=False, help="If checked, new fetches bypass approval.")

st.sidebar.markdown("---")
st.sidebar.info("Application Status: Connected to SQLite")

# --- Main Area ---
st.title("AI News Automation Dashboard")
st.write(f"Today is: {datetime.now().strftime('%B %d, %Y')}")

# Metrics Row
total, pending, posted = db_manager.get_metrics()
m1, m2, m3 = st.columns(3)
m1.metric("Total Fetched", total)
m2.metric("Pending Approval", pending, delta_color="inverse")
m3.metric("Posted", posted)

st.markdown("---")
st.subheader("News Feed")

# --- News Feed Rendering ---
news_items = db_manager.get_all_news()

if not news_items:
    st.info("No news items found. Click 'Trigger AI Fetch Now' to get started.")
else:
    for item in news_items:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            # Column 1: Image
            with col1:
                st.image(item['image_path'], use_container_width=True)
                st.caption(f"Source: [Link]({item['source_url']})")
            
            # Column 2: Content (Editable)
            with col2:
                # Use keys to identify state for each item
                edited_title = st.text_input("Headline", value=item['original_title'], key=f"title_{item['id']}")
                edited_summary = st.text_area("Summary", value=item['summary_content'], key=f"summary_{item['id']}", height=150)
                
                # Auto-save logic (simulated by checking if values changed and updating DB)
                if edited_title != item['original_title'] or edited_summary != item['summary_content']:
                    db_manager.update_news_item(item['id'], title=edited_title, summary=edited_summary)
                    # No need to rerun here, Streamlit will handle local state, but DB is updated.

            # Column 3: Actions & Status
            with col3:
                status = item['status']
                if status == 'pending':
                    st.warning("Status: Pending Approval")
                    if st.button("✅ Approve & Post", key=f"post_{item['id']}", type="primary"):
                        # Mock posting
                        if news_engine.post_to_facebook(item['id'], edited_summary, item['image_path']):
                            db_manager.update_news_item(item['id'], status='posted')
                            st.success("Posted to Facebook!")
                            st.rerun()
                elif status == 'posted':
                    st.success("Status: Posted")
                elif status == 'rejected':
                    st.error("Status: Rejected")
                
                if st.button("🗑️ Delete", key=f"del_{item['id']}"):
                    db_manager.delete_news_item(item['id'])
                    st.rerun()

# --- Custom Styling ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)
