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
model = genai.GenerativeModel("gemini-2.0-flash")

def gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

st.title("🌍 AI-Powered Language Learning (Gemini)")

# Tabs for separating features
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 Vocabulary & Sentences",
    "🗣️ Pronunciation",
    "💬 Chat with AI",
    "ℹ️ About"
])

with tab1:
    st.header("🧠 Personalized Vocabulary List")
    vocab_prompt = f"Create a {skill_level.lower()} vocabulary list (10 words) for someone learning {target_language}. Include English meanings."
    vocab_list = gemini_response(vocab_prompt)
    st.markdown(vocab_list)

    st.header("✍️ Example Sentences")
    sentence_prompt = f"Give 5 {skill_level.lower()} level example sentences in {target_language} with English translations."
    sentences = gemini_response(sentence_prompt)
    st.markdown(sentences)

with tab2:
    st.header("🗣️ Pronunciation Guide")
    pronounce_prompt = f"Provide pronunciation tips for a {skill_level.lower()} learner in {target_language}."
    pronunciation = gemini_response(pronounce_prompt)
    st.markdown(pronunciation)

with tab3:
    st.header("💬 Practice Conversation with AI")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You:", "")
    if user_input:
        convo_prompt = f"Let's have a conversation in {target_language}. I am a {skill_level.lower()} learner. Respond to this input: {user_input}"
        ai_reply = gemini_response(convo_prompt)

        # Add to history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", ai_reply))

    for speaker, message in st.session_state.chat_history:
        st.markdown(f"**{speaker}:** {message}")

with tab4:
    st.markdown("""
    ## About
    This app helps you learn languages using Google's Gemini AI.
    - Generates personalized vocabulary
    - Example sentences with translations
    - Pronunciation tips
    - Practice chatting with an AI

    Built with ❤️ using Streamlit + Gemini.
    """)
