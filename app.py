import streamlit as st
from groq import Groq
import urllib.parse
import random

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(page_title="AI Content Assistant", page_icon="🚀", layout="wide")

# ----------------- SESSION STATE SETUP -----------------
# We use session states to remember the generated content when the user interacts with buttons
if 'post_content' not in st.session_state:
    st.session_state.post_content = None
if 'hashtags' not in st.session_state:
    st.session_state.hashtags = None
if 'img1_url' not in st.session_state:
    st.session_state.img1_url = None
if 'img2_url' not in st.session_state:
    st.session_state.img2_url = None
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None

# ----------------- SIDEBAR & API KEY -----------------
st.sidebar.title("⚙️ Configuration")
api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")
st.sidebar.markdown("[Get your free Groq API key here](https://console.groq.com/keys)")

# ----------------- MAIN UI -----------------
st.title("🚀 AI Content & Image Assistant")
st.markdown("Generate platform-specific content, SEO hashtags, and pick your favorite AI-generated graphic.")

# Input Form
with st.form("content_form"):
    col1, col2 = st.columns(2)
    with col1:
        content_type = st.selectbox("Content Type", ["Social Media Post", "Blog Intro", "Ad Copy", "Newsletter Snippet"])
        platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Twitter / X", "Facebook", "TikTok"])
    with col2:
        audience = st.text_input("Target Audience", placeholder="e.g., Tech enthusiasts, Small business owners")
        tone = st.selectbox("Tone", ["Professional", "Casual", "Humorous", "Inspirational", "Persuasive"])
    
    topic = st.text_area("Topic / Brief", placeholder="What is the post exactly about?")
    
    submit_button = st.form_submit_button("✨ Generate Post & Images")

# ----------------- GENERATION LOGIC -----------------
if submit_button:
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar.")
    elif not topic or not audience:
        st.warning("Please provide a Topic and Target Audience.")
    else:
        with st.spinner("Brainstorming content and generating graphics..."):
            try:
                # Initialize Groq Client
                client = Groq(api_key=api_key)
                
                # Strict prompt to force the LLM into returning a parseable format
                prompt = f"""
                You are a top-tier social media manager. Generate a {content_type} for {platform} targeting {audience} about: {topic}. 
                Tone: {tone}.
                
                Respond EXACTLY in this format with no extra text:
                [CAPTION]
                (Write the complete post caption here)
                
                [HASHTAGS]
                (Write SEO optimized hashtags here)
                
                [IMAGE_PROMPT_1]
                (Write a highly detailed, descriptive text-to-image prompt for a relevant image)
                
                [IMAGE_PROMPT_2]
                (Write a completely DIFFERENT but relevant detailed text-to-image prompt for a second option)
                """
                
                # Call Groq API
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="openai/gpt-oss-20b",
                    temperature=0.7,
                )
                
                response_text = chat_completion.choices[0].message.content
                
                # Parse the exact sections from the response
                caption = response_text.split("[CAPTION]")[1].split("[HASHTAGS]")[0].strip()
                hashtags = response_text.split("[HASHTAGS]")[1].split("[IMAGE_PROMPT_1]")[0].strip()
                prompt1 = response_text.split("[IMAGE_PROMPT_1]")[1].split("[IMAGE_PROMPT_2]")[0].strip()
                prompt2 = response_text.split("[IMAGE_PROMPT_2]")[1].strip()
                
                # Save to session state
                st.session_state.post_content = caption
                st.session_state.hashtags = hashtags
                
                # We use free Pollinations.ai for images. We add a random seed so duplicate prompts yield new images.
                seed1, seed2 = random.randint(1, 10000), random.randint(1, 10000)
                st.session_state.img1_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt1)}?width=1024&height=1024&nologo=true&seed={seed1}"
                st.session_state.img2_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt2)}?width=1024&height=1024&nologo=true&seed={seed2}"
                st.session_state.selected_image = None  # Reset any previous selection
                
            except IndexError:
                st.error("The AI returned a malformed response. Please click Generate again.")
            except Exception as e:
                st.error(f"Error: {e}")

# ----------------- RESULTS & UI LOGIC -----------------
if st.session_state.post_content:
    st.divider()
    st.subheader("📝 Your Content")
    st.write(st.session_state.post_content)
    st.write(f"**{st.session_state.hashtags}**")
    
    st.divider()
    st.subheader("🎨 Select Your Image")
    
    # If the user has already chosen an image, display the final result
    if st.session_state.selected_image:
        st.success("✅ Image selected! Here is your final post preview:")
        st.image(st.session_state.selected_image, width=600)
        
        # Option to undo selection
        if st.button("🔄 Choose the other image"):
            st.session_state.selected_image = None
            st.rerun()
            
    # Otherwise, show both image choices
    else:
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.image(st.session_state.img1_url, use_column_width=True, caption="Option 1")
            # When clicked, update state and rerun the script to hide the other image
            if st.button("Select Option 1", key="btn1", use_container_width=True):
                st.session_state.selected_image = st.session_state.img1_url
                st.rerun()
                
        with col_img2:
            st.image(st.session_state.img2_url, use_column_width=True, caption="Option 2")
            if st.button("Select Option 2", key="btn2", use_container_width=True):
                st.session_state.selected_image = st.session_state.img2_url
                st.rerun()