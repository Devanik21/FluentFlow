import streamlit as st
import google.generativeai as genai

# Sidebar Inputs
st.sidebar.title("Language Learning Settings")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")
target_language = st.sidebar.selectbox("Target Language", ["Spanish", "French", "German", "Japanese", "Mandarin"])
skill_level = st.sidebar.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"])

# Set API Key
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")

def gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

st.title("🌍 AI-Powered Language Learning (Gemini)")

# Section 1: Vocabulary List
st.header("🧠 Personalized Vocabulary List")
vocab_prompt = f"Create a {skill_level.lower()} vocabulary list (10 words) for someone learning {target_language}. Include English meanings."
vocab_list = gemini_response(vocab_prompt)
st.markdown(vocab_list)

# Section 2: Example Sentences
st.header("✍️ Example Sentences")
sentence_prompt = f"Give 5 {skill_level.lower()} level example sentences in {target_language} with English translations."
sentences = gemini_response(sentence_prompt)
st.markdown(sentences)

# Section 3: Pronunciation Guide
st.header("🗣️ Pronunciation Guide")
pronounce_prompt = f"Provide pronunciation tips for a {skill_level.lower()} learner in {target_language}."
pronunciation = gemini_response(pronounce_prompt)
st.markdown(pronunciation)

# Section 4: AI Chatbot Conversation
st.header("💬 Practice Conversation with AI")
user_input = st.text_input("You:", "")

if user_input:
    convo_prompt = f"Let's have a conversation in {target_language}. I am a {skill_level.lower()} learner. Respond to this input: {user_input}"
    ai_reply = gemini_response(convo_prompt)
    st.markdown(f"**AI:** {ai_reply}")
