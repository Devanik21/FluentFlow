import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="LingoGem", layout="centered")

# ─────────────────────────────────────────────────────
# 🌐 MAIN APP SETTINGS (Tab 1 & 2)
# ─────────────────────────────────────────────────────
st.sidebar.title("General Language Settings")
main_api_key = st.sidebar.text_input("Gemini API Key (for vocab, sentences, pronunciation)", type="password", key="main_api_key")
target_language = st.sidebar.selectbox("Target Language", ["Spanish", "French", "German", "Japanese", "Mandarin"], key="lang")
skill_level = st.sidebar.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"], key="level")

# Tabs
tab1, tab2, tab3 = st.tabs(["📘 Learn", "🗣️ Pronunciation", "💬 AI Chatbot"])

# Helper: Setup Gemini
def setup_gemini(key):
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-2.0-flash")

# Helper: Get response
def gemini_response(model, prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# ─────────────────────────────────────────────────────
# 📘 TAB 1 — Vocabulary & Sentences
# ─────────────────────────────────────────────────────
with tab1:
    st.header("🧠 Vocabulary & Sentences")
    if not main_api_key:
        st.warning("Enter your Gemini API key in the sidebar.")
        st.stop()

    if "learn_model" not in st.session_state:
        st.session_state.learn_model = setup_gemini(main_api_key)

    if "vocab_done" not in st.session_state:
        vocab_prompt = f"Create a {skill_level.lower()} vocabulary list (10 words) for someone learning {target_language}. Include English meanings."
        vocab_list = gemini_response(st.session_state.learn_model, vocab_prompt)
        st.session_state.vocab_text = vocab_list
        st.session_state.vocab_done = True

    st.subheader("Vocabulary List")
    st.markdown(st.session_state.vocab_text)

    if "sentence_done" not in st.session_state:
        sentence_prompt = f"Give 5 {skill_level.lower()} level example sentences in {target_language} with English translations."
        sentences = gemini_response(st.session_state.learn_model, sentence_prompt)
        st.session_state.sentences_text = sentences
        st.session_state.sentence_done = True

    st.subheader("Example Sentences")
    st.markdown(st.session_state.sentences_text)

# ─────────────────────────────────────────────────────
# 🗣️ TAB 2 — Pronunciation Guide
# ─────────────────────────────────────────────────────
with tab2:
    st.header("🗣️ Pronunciation Guide")
    if not main_api_key:
        st.warning("Enter your Gemini API key in the sidebar.")
        st.stop()

    if "pronounce_done" not in st.session_state:
        model = setup_gemini(main_api_key)
        pronounce_prompt = f"Provide pronunciation tips for a {skill_level.lower()} learner in {target_language}."
        st.session_state.pronounce_text = gemini_response(model, pronounce_prompt)
        st.session_state.pronounce_done = True

    st.markdown(st.session_state.pronounce_text)

# ─────────────────────────────────────────────────────
# 💬 TAB 3 — Isolated AI Chatbot
# ─────────────────────────────────────────────────────
with tab3:
    st.header("💬 Practice Conversation")

    chat_api_key = st.text_input("Gemini API Key (for chat)", type="password", key="chat_api_key")
    
    if chat_api_key:
        if "chat_model" not in st.session_state:
            st.session_state.chat_model = setup_gemini(chat_api_key)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input("You:", key="chat_input")

        if user_input:
            convo_prompt = f"Let's have a conversation in {target_language}. I am a {skill_level.lower()} learner. Respond to: {user_input}"
            ai_reply = gemini_response(st.session_state.chat_model, convo_prompt)

            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", ai_reply))

        for speaker, message in st.session_state.chat_history:
            st.markdown(f"**{speaker}:** {message}")
    else:
        st.info("Please enter a Gemini API key for the chatbot.")
