import streamlit as st
import requests
from bs4 import BeautifulSoup
import html
import random
import time

# Page Config
st.set_page_config(page_title="Operations Financieres", page_icon="🕵️‍♂️")

# --- Blackjack Logic ---

def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [{'rank': r, 'suit': s} for s in suits for r in ranks]
    random.shuffle(deck)
    return deck

def get_card_value(card):
    if card['rank'] in ['J', 'Q', 'K']:
        return 10
    elif card['rank'] == 'A':
        return 11
    else:
        return int(card['rank'])

def calculate_score(hand):
    score = sum(get_card_value(card) for card in hand)
    num_aces = sum(1 for card in hand if card['rank'] == 'A')
    
    while score > 21 and num_aces > 0:
        score -= 10
        num_aces -= 1
    return score

# --- Session State Initialization ---

if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False

if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'deck' not in st.session_state:
    st.session_state.deck = []
if 'player_hand' not in st.session_state:
    st.session_state.player_hand = []
if 'dealer_hand' not in st.session_state:
    st.session_state.dealer_hand = []
if 'game_message' not in st.session_state:
    st.session_state.game_message = ""
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# --- Main UI ---

st.title("🕵️‍♂️ Operations Financieres")

# If access is NOT granted, show Blackjack Game
if not st.session_state.access_granted:
    st.markdown("### 🔒 Security Check")
    st.write("The mainframe is locked. You must beat the dealer at **Blackjack** to gain access.")
    st.divider()

    # URL Input Phase
    url_input = st.text_input("Enter Locked Article URL", placeholder="https://operationsfinancieres.com/...", key="url_key")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        if not st.session_state.game_active and not st.session_state.game_over:
            if st.button("Start Security Override", type="primary"):
                # Reset Game
                st.session_state.deck = create_deck()
                st.session_state.player_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
                st.session_state.dealer_hand = [st.session_state.deck.pop(), st.session_state.deck.pop()]
                st.session_state.game_active = True
                st.session_state.game_over = False
                st.session_state.game_message = ""
                st.rerun()

    # Verify URL is present before playing seriously
    if not url_input and st.session_state.game_active:
         st.warning("⚠️ Warning: You are playing without a target URL. You can still play, but you'll need to enter the URL later.")

    # Game Area
    if st.session_state.game_active or st.session_state.game_over:
        
        # Display Dealer Hand
        st.subheader("Dealer's Hand")
        dealer_display_cols = st.columns(10) # many columns for cards
        
        if st.session_state.game_active:
            # Show first card, hide second
            with dealer_display_cols[0]:
                st.markdown(f"<div style='border:1px solid #ccc; border-radius:5px; padding:10px; text-align:center; font-size:20px; background-color:white; color:black;'>{st.session_state.dealer_hand[0]['rank']}{st.session_state.dealer_hand[0]['suit']}</div>", unsafe_allow_html=True)
            with dealer_display_cols[1]:
                st.markdown(f"<div style='border:1px solid #ccc; border-radius:5px; padding:10px; text-align:center; font-size:20px; background-color:#aaa; color:#aaa;'>?</div>", unsafe_allow_html=True)
        else:
            # Show all dealer cards
            for idx, card in enumerate(st.session_state.dealer_hand):
                 with dealer_display_cols[idx]:
                    color = "red" if card['suit'] in ['♥', '♦'] else "black"
                    st.markdown(f"<div style='border:1px solid #ccc; border-radius:5px; padding:10px; text-align:center; font-size:20px; background-color:white; color:{color};'>{card['rank']}{card['suit']}</div>", unsafe_allow_html=True)
            
            st.caption(f"Dealer Score: {calculate_score(st.session_state.dealer_hand)}")

        st.divider()

        # Display Player Hand
        st.subheader("Your Hand")
        player_display_cols = st.columns(10)
        for idx, card in enumerate(st.session_state.player_hand):
            with player_display_cols[idx]:
                color = "red" if card['suit'] in ['♥', '♦'] else "black"
                st.markdown(f"<div style='border:1px solid #ccc; border-radius:5px; padding:10px; text-align:center; font-size:20px; background-color:white; color:{color};'>{card['rank']}{card['suit']}</div>", unsafe_allow_html=True)
        
        player_score = calculate_score(st.session_state.player_hand)
        st.caption(f"Your Score: {player_score}")

        st.divider()

        # Game Controls
        if st.session_state.game_active:
            # Check for immediate Blackjack
            if player_score == 21:
                st.session_state.game_active = False
                st.session_state.game_over = True
                st.session_state.game_message = "BLACKJACK! You Win!"
                st.session_state.access_granted = True
                st.rerun()

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Hit"):
                    st.session_state.player_hand.append(st.session_state.deck.pop())
                    if calculate_score(st.session_state.player_hand) > 21:
                        st.session_state.game_active = False
                        st.session_state.game_over = True
                        st.session_state.game_message = "BUST! You went over 21. Access Denied."
                    st.rerun()
            with c2:
                if st.button("Stand"):
                    st.session_state.game_active = False
                    st.session_state.game_over = True
                    
                    # Dealer Play Logic
                    while calculate_score(st.session_state.dealer_hand) < 17:
                        st.session_state.dealer_hand.append(st.session_state.deck.pop())
                    
                    d_score = calculate_score(st.session_state.dealer_hand)
                    p_score = calculate_score(st.session_state.player_hand)

                    if d_score > 21:
                        st.session_state.game_message = "Dealer BUSTS! You Win!"
                        st.session_state.access_granted = True
                    elif d_score > p_score:
                         st.session_state.game_message = "Dealer Wins. Access Denied."
                    elif d_score < p_score:
                        st.session_state.game_message = "You Win! Access Granted."
                        st.session_state.access_granted = True
                    else:
                        st.session_state.game_message = "Push (Tie). Access Denied." # House edge: tie usually means no win, or strict 'BEAT'
                    st.rerun()

        # Game Over Message
        if st.session_state.game_over:
            if st.session_state.access_granted:
                st.success(f"🎉 {st.session_state.game_message}")
                if st.button("Proceed to Article"):
                    st.rerun()
            else:
                st.error(f"❌ {st.session_state.game_message}")
                if st.button("Try Again"):
                    # Reset
                    st.session_state.game_active = False
                    st.session_state.game_over = False
                    st.rerun()

# If access IS granted, show the original Article Logic
else:
    st.success("✅ System Hacked. Access Granted.")
    
    url = st.session_state.get("url_key", "")
    
    # Allow changing URL even after hack? Let's say yes, or keep it locked to session. 
    # For now, let's allow them to input again if it was empty, or see the one they typed.
    
    if not url:
        col1, col2 = st.columns([3, 1])
        url = col1.text_input("Article URL to Decode", key="post_unlock_url")
        if col2.button("Lock System"):
            st.session_state.access_granted = False
            st.rerun()
    else:
        st.write(f"Target: {url}")
        if st.button("Lock System / Logout"):
            st.session_state.access_granted = False
            st.rerun()

    if url:
        # Original Logic
        # Extract Slug
        slug = url.strip().rstrip('/').split('/')[-1]
        
        with st.spinner(f"Decoding content for: {slug}..."):
            api_url = "https://operationsfinancieres.com/wp-json/wp/v2/posts"
            params = {'slug': slug, '_embed': 'true'}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
            }

            try:
                # Cache checking to avoid spamming if simple refresh? Not strictly needed for this task.
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
                    st.divider()
                    st.header(title)
                    st.caption(f"Published: {date}")
                    st.markdown(final_text) 
                    st.divider()
                    
                else:
                    st.error("❌ Could not find the article. Check the link or the site has patched the API.")
                    
            except Exception as e:
                st.error(f"Error: {e}")