import streamlit as st
import requests
from bs4 import BeautifulSoup
import html

# Page Config
st.set_page_config(page_title="Operations Financieres", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Operations Financieres")
st.write("Paste the locked article URL below to bypass the blockage.")

# Input
url = st.text_input("Article URL", placeholder="https://operationsfinancieres.com/...")

if st.button("Unlock Article"):
    if not url:
        st.warning("Please enter a URL first.")
    else:
        # Extract Slug
        slug = url.strip().rstrip('/').split('/')[-1]
        
        with st.spinner(f"Hacking into mainframe for: {slug}..."):
            api_url = "https://operationsfinancieres.com/wp-json/wp/v2/posts"
            params = {'slug': slug, '_embed': 'true'}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
            }

            try:
                response = requests.get(api_url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200 and response.json():
                    post = response.json()[0]
                    title = html.unescape(post['title']['rendered'])
                    date = post['date']
                    raw_html = post['content']['rendered']
                    
                    # Clean HTML to Markdown
                    soup = BeautifulSoup(raw_html, 'html.parser')
                    
                    # Convert bold/italic to Markdown
                    for tag in soup.find_all(['strong', 'b']):
                        tag.replace_with(f"**{tag.get_text().strip()}**")
                    for tag in soup.find_all(['em', 'i']):
                        tag.replace_with(f"*{tag.get_text().strip()}*")
                    
                    # Clean paragraphs
                    clean_paragraphs = []
                    for p in soup.find_all(['p', 'h1', 'h2', 'h3']):
                        text = " ".join(p.get_text().split())
                        if text:
                            clean_paragraphs.append(text)
                            
                    final_text = "\n\n".join(clean_paragraphs)

                    # Display
                    st.success("Access Granted!")
                    st.divider()
                    st.header(title)
                    st.caption(f"Published: {date}")
                    st.markdown(final_text) # Streamlit renders the **bold** automatically
                    st.divider()
                    
                else:
                    st.error("❌ Could not find the article. Check the link or the site has patched the API.")
                    
            except Exception as e:
                st.error(f"Error: {e}")