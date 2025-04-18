import streamlit as st
import google.generativeai as genai
import json
import random
from datetime import datetime

# Page configuration
st.set_page_config(page_title="AI Language Learning", layout="wide")

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vocab_list" not in st.session_state:
    st.session_state.vocab_list = None
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "current_card" not in st.session_state:
    st.session_state.current_card = 0
if "saved_vocab" not in st.session_state:
    st.session_state.saved_vocab = {}
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_total" not in st.session_state:
    st.session_state.quiz_total = 0
if "last_settings" not in st.session_state:
    st.session_state.last_settings = {}

# Sidebar Inputs
st.sidebar.title("Language Learning Settings")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")
target_language = st.sidebar.selectbox("Target Language", ["Spanish", "French", "German", "Japanese", "Mandarin", "Italian", "Portuguese", "Russian", "Korean", "Arabic"])
skill_level = st.sidebar.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"])
learning_focus = st.sidebar.selectbox("Learning Focus", ["General", "Travel", "Business", "Academic", "Medical", "Technology"])

# Track settings changes
current_settings = {"target_language": target_language, "skill_level": skill_level, "learning_focus": learning_focus}
settings_changed = current_settings != st.session_state.last_settings

# Save current settings
st.session_state.last_settings = current_settings.copy()

# Set API Key
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

def gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def parse_vocab_list(raw_text):
    """Parse vocabulary list from Gemini's response"""
    try:
        lines = raw_text.strip().split('\n')
        vocab_items = []
        
        current_item = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Handle different list formats
            if line.startswith(('- ', '* ', '• ')):
                line = line[2:]
            
            # Handle numbered lists
            if line[0].isdigit() and '. ' in line[:5]:
                line = line[line.find('. ')+2:]
                
            # Check for word and definition pattern
            if ':' in line:
                parts = line.split(':', 1)
                word = parts[0].strip()
                meaning = parts[1].strip()
                vocab_items.append({"word": word, "meaning": meaning})
            elif ' - ' in line:
                parts = line.split(' - ', 1)
                word = parts[0].strip()
                meaning = parts[1].strip()
                vocab_items.append({"word": word, "meaning": meaning})
            elif ' – ' in line:
                parts = line.split(' – ', 1)
                word = parts[0].strip()
                meaning = parts[1].strip()
                vocab_items.append({"word": word, "meaning": meaning})
        
        return vocab_items
    except Exception as e:
        st.error(f"Error parsing vocabulary list: {e}")
        return []

def generate_quiz(vocab_items, num_questions=5):
    """Generate a quiz from vocabulary items"""
    if not vocab_items or len(vocab_items) < 3:
        return []
    
    quiz = []
    selected_items = random.sample(vocab_items, min(num_questions, len(vocab_items)))
    
    for item in selected_items:
        question_type = random.choice(["multiple_choice", "fill_blank"])
        
        if question_type == "multiple_choice":
            # Create wrong options
            wrong_options = []
            all_meanings = [v["meaning"] for v in vocab_items if v != item]
            if len(all_meanings) >= 3:
                wrong_options = random.sample(all_meanings, 3)
            else:
                wrong_options = all_meanings
                
            options = wrong_options + [item["meaning"]]
            random.shuffle(options)
            
            quiz.append({
                "type": "multiple_choice",
                "question": f"What does '{item['word']}' mean?",
                "options": options,
                "correct_answer": item["meaning"]
            })
        else:
            quiz.append({
                "type": "fill_blank",
                "question": f"Translate: {item['meaning']}",
                "correct_answer": item["word"]
            })
    
    return quiz

st.title("🌍 AI-Powered Language Learning (Gemini)")

# Tabs for separating features
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧠 Vocabulary & Sentences",
    "🗣️ Pronunciation",
    "💬 Chat with AI",
    "📝 Writing Practice",
    "🎮 Quiz & Games",
    "ℹ️ About"
])

with tab1:
    st.header("🧠 Personalized Vocabulary List")
    
    # Generate new vocab or use saved
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Generate New Vocabulary") or (settings_changed and st.session_state.vocab_list is None):
            vocab_prompt = f"""Create a {skill_level.lower()} vocabulary list (10 words) for someone learning {target_language} with a focus on {learning_focus.lower()}. 
            Include English meanings. Format each entry as 'word - meaning' for easy parsing."""
            
            vocab_response = gemini_response(vocab_prompt)
            st.session_state.vocab_list = vocab_response
            parsed_vocab = parse_vocab_list(vocab_response)
            st.session_state.flashcards = parsed_vocab
    
    with col2:
        if st.button("Save Vocabulary List"):
            date_key = datetime.now().strftime("%Y-%m-%d %H:%M")
            if st.session_state.vocab_list:
                st.session_state.saved_vocab[date_key] = {
                    "text": st.session_state.vocab_list,
                    "language": target_language,
                    "level": skill_level,
                    "focus": learning_focus
                }
                st.success("Vocabulary list saved!")
    
    # Display vocabulary
    if st.session_state.vocab_list:
        st.markdown(st.session_state.vocab_list)
    
    # Example sentences
    st.header("✍️ Example Sentences")
    
    if st.button("Generate Example Sentences"):
        sentence_prompt = f"""Give 5 {skill_level.lower()} level example sentences in {target_language} with English translations.
        These should be useful for someone focusing on {learning_focus.lower()} topics.
        Format each as: 
        - [Target Language Sentence]
        - [English Translation]
        (add a blank line between different examples)"""
        
        sentences = gemini_response(sentence_prompt)
        st.markdown(sentences)

    # Saved vocabulary
    if st.session_state.saved_vocab:
        st.header("📚 Saved Vocabulary Lists")
        selected_date = st.selectbox("Select saved list", list(st.session_state.saved_vocab.keys()))
        if selected_date:
            saved_item = st.session_state.saved_vocab[selected_date]
            st.markdown(f"**Language:** {saved_item['language']} | **Level:** {saved_item['level']} | **Focus:** {saved_item['focus']}")
            st.markdown(saved_item['text'])

with tab2:
    st.header("🗣️ Pronunciation Guide")
    
    # Create tabs for different pronunciation features
    pronun_tabs = st.tabs(["Learning Materials", "Interactive Tools", "Audio Lab", "Visual Aids"])
    
    with pronun_tabs[0]:
        pronunciation_type = st.radio("Select pronunciation focus", 
                                    ["General Tips", "Common Sounds", "Tongue Twisters", "Rhythm & Intonation", "Regional Accents"])
        
        if st.button("Generate Pronunciation Guide"):
            with st.spinner("Generating pronunciation content..."):
                if pronunciation_type == "General Tips":
                    pronounce_prompt = f"""Provide 5 essential pronunciation tips for a {skill_level.lower()} learner in {target_language}.
                    Focus on general rules, common mistakes to avoid, and provide specific examples for each tip."""
                elif pronunciation_type == "Common Sounds":
                    pronounce_prompt = f"""Explain how to pronounce 5 difficult sounds in {target_language} for {skill_level.lower()} students.
                    Include examples, English approximations where possible, and describe the exact mouth positioning for each sound."""
                elif pronunciation_type == "Tongue Twisters":
                    pronounce_prompt = f"""Create 3 progressively difficult tongue twisters in {target_language} for {skill_level.lower()} students 
                    with translations, pronunciation notes, and the specific sounds they help practice."""
                elif pronunciation_type == "Rhythm & Intonation":
                    pronounce_prompt = f"""Explain the rhythm, stress patterns, and intonation rules of {target_language} for {skill_level.lower()} learners.
                    Include 3 practice sentences with marked stress and intonation patterns."""
                else:  # Regional Accents
                    pronounce_prompt = f"""Describe 3 major regional accents or dialects in {target_language}.
                    Highlight their key pronunciation differences, provide example words showing these differences, and explain where these accents are spoken."""
                    
                pronunciation = gemini_response(pronounce_prompt)
                st.markdown(pronunciation)
        
        # Phonetic chart
        st.subheader("📊 Phonetic Chart")
        if st.button("Show Phonetic Chart"):
            with st.spinner("Generating phonetic chart..."):
                phonetic_prompt = f"""Create a comprehensive phonetic chart for {target_language} showing all the main sounds.
                For each sound, provide:
                1. The IPA symbol
                2. Example words in {target_language}
                3. Closest English approximation if any
                
                Format this as a well-organized markdown table."""
                
                phonetic_chart = gemini_response(phonetic_prompt)
                st.markdown(phonetic_chart)
    
    with pronun_tabs[1]:
        st.subheader("🔄 Interactive Pronunciation Tools")
        
        # Minimal pairs practice
        st.write("### Minimal Pairs Practice")
        if st.button("Generate Minimal Pairs"):
            with st.spinner("Generating minimal pairs..."):
                minimal_pairs_prompt = f"""Create 5 sets of minimal pairs in {target_language} that {skill_level.lower()} learners often struggle with.
                For each pair:
                1. Show the two words
                2. Provide their meanings
                3. Explain the exact sound difference
                4. Give a tip on distinguishing them
                
                Format this information clearly in markdown."""
                
                minimal_pairs = gemini_response(minimal_pairs_prompt)
                st.markdown(minimal_pairs)
        
        # Sentence stress analyzer
        st.write("### Sentence Stress Analyzer")
        input_sentence = st.text_area("Enter a sentence in the target language to analyze its stress pattern:", 
                                     placeholder=f"Type a sentence in {target_language} here...")
        
        if st.button("Analyze Stress Pattern") and input_sentence:
            with st.spinner("Analyzing stress pattern..."):
                stress_prompt = f"""Analyze the following sentence in {target_language} and mark the stressed syllables and intonation pattern:
                
                "{input_sentence}"
                
                Provide:
                1. The sentence with stressed syllables marked in UPPERCASE
                2. Intonation pattern (rising, falling, etc.)
                3. Tips for proper pronunciation"""
                
                stress_analysis = gemini_response(stress_prompt)
                st.markdown(stress_analysis)
        
        # Syllable breakdown tool
        st.write("### Syllable Breakdown Tool")
        word_to_break = st.text_input("Enter a word to break into syllables:", 
                                     placeholder=f"Type a word in {target_language}...")
        
        if st.button("Break into Syllables") and word_to_break:
            with st.spinner("Breaking into syllables..."):
                syllable_prompt = f"""Break the {target_language} word "{word_to_break}" into syllables.
                
                Provide:
                1. Each syllable separated by hyphens
                2. Which syllables are stressed (primary and secondary stress if applicable)
                3. Pronunciation guide for each syllable
                4. Any special pronunciation rules that apply to this word"""
                
                syllable_breakdown = gemini_response(syllable_prompt)
                st.markdown(syllable_breakdown)
    
    with pronun_tabs[2]:
        st.subheader("🎵 Interactive Audio Lab")
        
        # Mock audio player with playback speed control
        st.write("### Audio Examples with Variable Speed")
        audio_type = st.selectbox("Choose audio example type:", 
                                ["Common Phrases", "Difficult Sounds", "Pronunciation Drills", "Tone Patterns"])
        
        speed_options = {0.5: "Slow (0.5x)", 0.75: "Slower (0.75x)", 1.0: "Normal (1.0x)", 1.25: "Faster (1.25x)"}
        playback_speed = st.select_slider("Playback Speed:", 
                                        options=[0.5, 0.75, 1.0, 1.25],
                                        format_func=lambda x: speed_options[x],
                                        value=1.0)
        
        if st.button("Generate Audio Examples"):
            with st.spinner("Generating audio content..."):
                audio_prompt = f"""Generate {3} {audio_type.lower()} in {target_language} for {skill_level.lower()} learners.
                
                For each example, provide:
                1. The text in {target_language}
                2. English translation
                3. Detailed pronunciation notes"""
                
                audio_examples = gemini_response(audio_prompt)
                st.markdown(audio_examples)
                
                # Mock audio player UI
                for i in range(3):
                    cols = st.columns([1, 8, 1])
                    with cols[0]:
                        st.button("▶️", key=f"play_{i}")
                    with cols[1]:
                        st.progress(0)
                    with cols[2]:
                        st.write(f"{speed_options[playback_speed]}")
        
        # Voice comparison tool mockup
        st.write("### Speech Analysis Tool")
        st.write("Record your pronunciation and compare it to a native speaker")
        
        # Mock recording interface
        cols = st.columns([2, 1])
        with cols[0]:
            st.text_input("Phrase to practice:", placeholder="Type a phrase to practice...")
        with cols[1]:
            st.button("🎙️ Record", type="primary")
        
        # Mock comparison results
        with st.expander("View detailed pronunciation feedback"):
            st.write("This tool would provide visualization of your speech compared to native pronunciation, with:")
            st.write("- Waveform comparison")
            st.write("- Pitch and intonation graphs")
            st.write("- Specific feedback on problem sounds")
            st.write("- Accuracy score and improvement suggestions")
    
    with pronun_tabs[3]:
        st.subheader("👁️ Visual Pronunciation Aids")
        
        # Language inputs
        native_language = st.selectbox("Your Native Language:", ["English", "Hindi", "Mandarin", "Spanish", "Other"])
        target_language = st.selectbox("Target Language:", ["English", "French", "German", "Japanese", "Other"])
        
        # Articulation diagrams
        st.write("### Mouth & Tongue Position Diagrams")
        sound_to_show = st.selectbox("Select a sound to visualize:", 
                                    ["Vowels", "Consonants", "Diphthongs", "Special Sounds"])
        
        if st.button("Show Articulation Diagrams"):
            with st.spinner("Generating diagrams..."):
                diagram_prompt = f"""Create a detailed explanation of how to position the mouth, tongue, and lips for {sound_to_show.lower()} in {target_language}.
                
                Include:
                1. Step-by-step instructions for proper articulation
                2. Common mistakes made by {native_language} speakers
                3. Practice exercises focused on these specific sounds"""
                
                diagrams = gemini_response(diagram_prompt)
                st.markdown(diagrams)
                
                # Mock diagram display
                st.write("Visualization would show cross-section diagrams of the mouth showing proper tongue and lip positions")
                cols = st.columns(3)
                for i in range(3):
                    with cols[i]:
                        st.markdown(f"#### Sound {i+1}")
                        st.text("Diagram would appear here")
        
        # IPA interactive chart
        st.write("### Interactive IPA Chart")
        st.write("Explore the International Phonetic Alphabet (IPA) symbols used in your target language")

        
        # Create a simple mock IPA interactive chart
        cols = st.columns(4)
        ipa_examples = {
            "a": "father", "e": "bed", "i": "see", 
            "o": "go", "u": "blue", "ə": "about",
            "ʃ": "ship", "ʒ": "vision", "θ": "think",
            "ð": "this", "ʧ": "chair", "ʤ": "judge"
        }
        
        for i, (symbol, example) in enumerate(ipa_examples.items()):
            with cols[i % 4]:
                if st.button(f"{symbol}", key=f"ipa_{i}"):
                    st.session_state.selected_ipa = symbol
        
        if st.session_state.get("selected_ipa"):
            symbol = st.session_state.selected_ipa
            st.markdown(f"### IPA Symbol: [{symbol}]")
            
            with st.spinner("Generating information..."):
                ipa_prompt = f"""Provide information about the IPA symbol [{symbol}] as it relates to {target_language} pronunciation.
                
                Include:
                1. How it's pronounced in {target_language}
                2. Example words containing this sound
                3. How it differs from similar sounds in English
                4. Tips for mastering this sound"""
                
                ipa_info = gemini_response(ipa_prompt)
                st.markdown(ipa_info)

# Add this to your session state initialization code at the beginning of the app
if 'selected_ipa' not in st.session_state:
    st.session_state.selected_ipa = None

import streamlit as st
from datetime import datetime
# Assume gemini_response is defined elsewhere for calling the Gemini API

# Initialize session state
if 'writing_history' not in st.session_state:
    st.session_state.writing_history = []
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None

with st.container():
    st.header("📝 Writing Practice")
    st.markdown("Select an exercise type and customize your session below.")

    # Exercise configuration
    col1, col2 = st.columns([2, 1])
    with col1:
        writing_type = st.selectbox(
            "Writing Exercise Type", 
            ["Guided Composition", "Translation", "Fill-in-the-Blanks", "Creative Writing"]
        )
        num_items = st.slider("Number of Prompts/Exercises", min_value=1, max_value=5, value=3)
        time_limit = st.slider("Time Limit (minutes)", 1, 30, 10)
    with col2:
        st.metric("Exercises Created", len(st.session_state.writing_history))
        if st.button("Clear History"):
            st.session_state.writing_history = []
            st.success("History cleared!")

    # Start timer
    if st.button("Start Writing Timer"):
        st.session_state.timer_start = datetime.now()
        st.info(f"Timer started at {st.session_state.timer_start.strftime('%H:%M:%S')}")

    # Show timer
    if st.session_state.timer_start:
        elapsed = datetime.now() - st.session_state.timer_start
        st.write(f"⏱️ Time elapsed: {elapsed.seconds // 60}m {elapsed.seconds % 60}s")

    st.divider()

    # Exercise generation
    if writing_type == "Guided Composition":
        prompt = (f"Generate {num_items} {skill_level.lower()}-level guided composition topics in {target_language} "
                  f"for {learning_focus.lower()} learners.")
        topics = gemini_response(prompt)
        st.markdown(topics)

    elif writing_type == "Translation":
        if st.button("Generate Translation Exercises"):
            prompt = (f"Create {num_items} {skill_level.lower()}-level English to {target_language} "
                      f"translation sentences relevant to {learning_focus.lower()}.")
            content = gemini_response(prompt)
            st.markdown(content)

    elif writing_type == "Fill-in-the-Blanks":
        if st.button("Generate Fill-in-the-Blanks"):
            prompt = (f"Create {num_items} {skill_level.lower()}-level fill-in-the-blanks exercises in {target_language} "
                      f"about {learning_focus.lower()}, each with a paragraph and blanks.")
            fill = gemini_response(prompt)
            # Extract answers section
            st.markdown(fill)
            with st.expander("Show Answers/Hints"):
                answers = gemini_response(prompt + "\nProvide answers and one-sentence hints for each blank.")
                st.markdown(answers)

    elif writing_type == "Creative Writing":
        if st.button("Generate Creative Prompts"):
            prompt = (f"Create {num_items} imaginative creative writing prompts for {skill_level.lower()} "
                      f"students in {target_language}, themed around {learning_focus.lower()}.")
            prompts = gemini_response(prompt)
            st.markdown(prompts)

    # Writing submission area
    st.divider()
    st.subheader("✍️ Write Below")
    user_input = st.text_area(
        "Your writing (draft here):", height=200
    )

    # Word count and readability
    if user_input:
        words = len(user_input.split())
        st.write(f"Word Count: {words}")
        if st.button("Analyze Readability"):
            read_prompt = f"Analyze the readability of this text: {user_input}"  
            read_feedback = gemini_response(read_prompt)
            st.markdown("**Readability Analysis**")
            st.markdown(read_feedback)

    # Feedback
    if user_input and st.button("Get Feedback & Suggestions"):
        fb_prompt = (
            f"Provide detailed feedback on this {skill_level.lower()} {target_language} writing sample: \"{user_input}\""
            "Include grammar corrections, vocabulary improvements, style tips, and a model answer."
        )
        feedback = gemini_response(fb_prompt)
        st.markdown("### Feedback & Model Answer")
        st.markdown(feedback)

        # Store history
        st.session_state.writing_history.append({
            'timestamp': datetime.now().isoformat(),
            'input': user_input,
            'feedback': feedback
        })

    # Download history
    if st.session_state.writing_history:
        st.divider()
        st.subheader("📚 Session History")
        for entry in st.session_state.writing_history[::-1]:
            st.markdown(f"**{entry['timestamp']}**")
            st.text(entry['input'])
            st.markdown(entry['feedback'])
        if st.download_button(
            "Download History as JSON", 
            data=str(st.session_state.writing_history), 
            file_name="writing_history.json"
        ):
            st.success("Downloaded! 🎉")


import streamlit as st
from datetime import datetime, timedelta, date
import json
import random

# --------- Utility Functions ---------
def start_timer(duration_min):
    st.session_state.timer_end = datetime.now() + timedelta(minutes=duration_min)

def get_time_left():
    remaining = st.session_state.timer_end - datetime.now()
    if remaining.total_seconds() <= 0:
        return None
    return remaining

def gemini_response(prompt: str) -> str:
    # Placeholder for Gemini API call
    return f"_Gemini response for:_\n{prompt}"

def play_audio(text: str):
    # Placeholder: integrate TTS engine
    st.audio(f"https://tts.mock/{text}")

# --------- Session State Initialization ---------
for key, default in [
    ('writing_history', []),
    ('streak', 0),
    ('last_practice', None),
    ('timer_end', None),
    ('language_goals', "Improve fluency and vocabulary"),
    ('favorite_words', []),
    ('leaderboard', []),
    ('daily_prompt_date', None),
    ('daily_prompt', None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# --------- Main Interface ---------
with st.container():
    st.title("📝 Ultimate Writing Practice Hub v2.0")
    st.markdown(
        "Supercharge your writing with audio prompts, challenges, analytics, and community features! 🌐🚀"
    )

    # ----- Sidebar: Profile, Goals, Settings -----
    with st.sidebar:
        st.subheader("👤 Profile & Progress")
        username = st.text_input("Name", st.session_state.get('username', 'Learner'))
        st.session_state['username'] = username
        st.write(f"🔥 Streak: **{st.session_state.streak}** days")
        if st.session_state.last_practice:
            st.write(f"🗓️ Last Practice: {st.session_state.last_practice.strftime('%Y-%m-%d')}")
        st.divider()
        st.subheader("🎯 Learning Focus")
        target_language = st.selectbox("Language", ["French","Spanish","German","Japanese","Chinese"], index=0)
        learning_focus = st.text_input("Topic Focus", "Travel & Culture")
        skill_level = st.selectbox("Skill Level", ["Beginner","Intermediate","Advanced"], index=1)
        st.text_area("Your Goals", value=st.session_state.language_goals, key="language_goals")
        st.divider()
        st.subheader("⚙️ Session Settings")
        writing_type = st.selectbox("Exercise Type", [
            "Guided Composition","Translation","Fill-in-the-Blanks",
            "Creative Writing","Email/Letter","Story Continuation",
            "Picture Description","Summary Writing","Argument Debate"
        ])
        num_items = st.slider("Number of Prompts", 1, 10, 3)
        time_limit = st.slider("Time Limit (min)", 5, 60, 20)
        theme = st.radio("Theme", ["Light","Dark"], index=0)
        if st.button("Start Session 🚀"):
            start_timer(time_limit)
            st.session_state.session_start = datetime.now()
            st.success("Session started! Good luck ✍️")

    # Apply Dark Theme
    if theme == 'Dark':
        st.markdown(
            "<style>body{background-color:#121212;color:#E0E0E0;}" +
            ".stButton>button{background-color:#333333;color:#FFFFFF;}" +
            "</style>", unsafe_allow_html=True
        )

    # ----- Daily Challenge -----
    st.subheader("🎲 Daily Challenge")
    today = date.today()
    if st.session_state.daily_prompt_date != today:
        dprompt = gemini_response(
            f"Generate a {skill_level.lower()} daily writing challenge in {target_language} on {learning_focus}."
        )
        st.session_state.daily_prompt = dprompt
        st.session_state.daily_prompt_date = today
    st.markdown(st.session_state.daily_prompt)
    if st.button("Regenerate Daily Prompt 🔄"):
        st.session_state.daily_prompt_date = None
        st.experimental_rerun()

    st.divider()

    # ----- Timer & Progress -----
    if st.session_state.timer_end:
        remaining = get_time_left()
        if remaining:
            m, s = divmod(remaining.seconds, 60)
            progress = remaining.seconds / (time_limit*60)
            st.progress(progress)
            st.write(f"⏰ Time Left: {m}m {s}s")
        else:
            st.warning("⏳ Time's up! Wrap it up soon.")

    # ----- Exercise Generation -----
    st.subheader("🧠 Exercise Generator")
    if st.button("Generate Prompts"): 
        if writing_type == "Guided Composition":
            prompt = f"Generate {num_items} {skill_level.lower()} guided composition topics in {target_language} about {learning_focus}."
        elif writing_type == "Translation":
            prompt = f"Give {num_items} English sentences to translate into {target_language}, include audio URLs and corrections."
        elif writing_type == "Fill-in-the-Blanks":
            prompt = f"Create {num_items} {target_language} paragraphs with blanks on {learning_focus}. Provide hints."
        elif writing_type == "Creative Writing":
            prompt = f"Provide {num_items} imaginative creative writing prompts in {target_language} around {learning_focus}."
        elif writing_type == "Email/Letter":
            prompt = f"Generate {num_items} email/letter templates in {target_language} for {learning_focus}."
        elif writing_type == "Story Continuation":
            prompt = f"Create {num_items} story starters in {target_language} for students to continue with vivid details."
        elif writing_type == "Picture Description":
            prompt = f"Describe {num_items} engaging images and ask user to write {target_language} description. Include image URLs."
        elif writing_type == "Summary Writing":
            prompt = f"Provide {num_items} short English passages and ask for a {target_language} summary."
        elif writing_type == "Argument Debate":
            prompt = f"Offer {num_items} debate topics in English and ask user to construct arguments in {target_language}."
        prompts = gemini_response(prompt)
        st.markdown(prompts)

    # ----- Vocabulary Booster -----
    st.subheader("📚 Vocabulary Booster")
    if st.button("Fetch Advanced Words"):
        vb_prompt = f"List {num_items*5} advanced {target_language} words on {learning_focus}, with definitions, synonyms, and audio URLs."
        vb_list = gemini_response(vb_prompt)
        st.markdown(vb_list)
        if st.button("Save to Favorites 💖"):
            lines = vb_list.split("\n")
            st.session_state.favorite_words += lines
            st.success(f"Added {len(lines)} words!")
    if st.session_state.favorite_words:
        with st.expander("❤️ Favorite Words"):
            for w in st.session_state.favorite_words[-10:]: st.write(w)

    # ----- Writing Pad & Tools -----
    st.subheader("✍️ Write & Improve")
    user_input = st.text_area("Your Draft:", height=300)
    if user_input:
        wc = len(user_input.split())
        st.write(f"📝 Word Count: {wc}")
        # Readability placeholder
        if st.button("Analyze Readability 📊"):
            rr = gemini_response(f"Analyze readability of: {user_input}")
            st.markdown("**Readability Report**")
            st.markdown(rr)
        if st.button("Get Feedback 🧐"):
            fb = gemini_response(f"Review this text: {user_input}. Provide corrections and style suggestions.")
            st.markdown("**### Feedback & Corrections**")
            st.markdown(fb)
        if st.button("Model Answer ✅"):
            ma = gemini_response(f"Write a polished model answer for: {user_input}")
            st.markdown("**### Model Answer**")
            st.markdown(ma)
        if st.button("Save Entry 💾"):
            entry = {
                'time': datetime.now().isoformat(),
                'type': writing_type,
                'input': user_input,
                'words': wc,
                'language': target_language,
                'level': skill_level
            }
            st.session_state.writing_history.append(entry)
            # Update leaderboard (top by word count)
            st.session_state.leaderboard.append(entry)
            st.session_state.leaderboard = sorted(
                st.session_state.leaderboard, key=lambda x: x['words'], reverse=True
            )[:5]
            st.success("Entry saved and leaderboard updated!")

    # ----- Practice History & Leaderboard -----
    if st.session_state.writing_history:
        st.subheader("📜 History & Stats")
        # History
        with st.expander("View All Entries"):
            for e in reversed(st.session_state.writing_history):
                st.markdown(f"- **{e['time']}** [{e['type']}] ({e['words']} words)")
        # Leaderboard
        st.subheader("🏆 Leaderboard (Longest Entries)")
        for idx, e in enumerate(st.session_state.leaderboard, 1):
            st.write(f"{idx}. {e['time']} — {e['words']} words")
        # Export
        if st.download_button(
            "📥 Export History & Stats", json.dumps({
                'history': st.session_state.writing_history,
                'leaderboard': st.session_state.leaderboard
            }, indent=2), file_name="practice_data.json"
        ):
            st.success("Data exported!")

    # ----- Session Summary & Achievements -----
    if st.session_state.get('session_start') and not get_time_left():
        st.subheader("✔️ Session Summary")
        total = len(st.session_state.writing_history)
        total_words = sum(e['words'] for e in st.session_state.writing_history)
        avg = total_words // total if total else 0
        st.write(f"• Total Pieces: **{total}**")
        st.write(f"• Total Words: **{total_words}**")
        st.write(f"• Avg Words/Piece: **{avg}**")
        if total >= 5:
            st.balloons(); st.success("🥇 Badge: Pro Writer")
        if avg >= 100:
            st.success("🚀 Badge: Wordsmith")
        # Update streak
        today_date = date.today()
        if st.session_state.last_practice != today_date:
            st.session_state.streak += 1
            st.session_state.last_practice = today_date
        st.write(f"Streak: {st.session_state.streak} days 🔥")
        st.markdown("*Visit again tomorrow to continue your progress!* 💖")
        
        
with tab5:
    st.header("🎮 Quiz & Games")
    
    game_type = st.selectbox("Select Activity", ["Vocabulary Quiz", "Flashcards", "Word Match", "Hangman"])
    
    if game_type == "Vocabulary Quiz":
        if st.button("Generate New Quiz") or (settings_changed and not st.session_state.quiz_questions):
            # Generate vocabulary if needed
            if not st.session_state.flashcards:
                vocab_prompt = f"""Create a {skill_level.lower()} vocabulary list of 20 words for someone learning {target_language} with a focus on {learning_focus.lower()}. 
                Include English meanings. Format each entry as 'word - meaning' for easy parsing."""
                
                vocab_response = gemini_response(vocab_prompt)
                parsed_vocab = parse_vocab_list(vocab_response)
                st.session_state.flashcards = parsed_vocab
            
            # Ensure we have enough vocabulary items
            if len(st.session_state.flashcards) < 20:
                additional_prompt = f"""Create {20 - len(st.session_state.flashcards)} more {skill_level.lower()} vocabulary words for someone learning {target_language} with a focus on {learning_focus.lower()}. 
                Include English meanings. Format each entry as 'word - meaning' for easy parsing."""
                
                additional_response = gemini_response(additional_prompt)
                additional_vocab = parse_vocab_list(additional_response)
                st.session_state.flashcards.extend(additional_vocab)
            
            # Generate quiz from vocabulary - ensure 20 questions
            st.session_state.quiz_questions = generate_quiz(st.session_state.flashcards, num_questions=20)
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0
        
        # Display quiz questions
        if st.session_state.quiz_questions:
            for i, question in enumerate(st.session_state.quiz_questions):
                st.markdown(f"### Question {i+1}: {question['question']}")
                
                if question['type'] == 'multiple_choice':
                    answer = st.radio(f"Select answer for question {i+1}:", 
                                     options=question['options'],
                                     key=f"q{i}")
                    
                    if st.button(f"Check Answer #{i+1}"):
                        if answer == question['correct_answer']:
                            st.success("Correct!")
                            st.session_state.quiz_score += 1
                        else:
                            st.error(f"Incorrect. The correct answer is: {question['correct_answer']}")
                        st.session_state.quiz_total += 1
                        
                elif question['type'] == 'fill_blank':
                    answer = st.text_input(f"Your answer for question {i+1}:", key=f"q{i}")
                    
                    if st.button(f"Check Answer #{i+1}"):
                        if answer.lower().strip() == question['correct_answer'].lower().strip():
                            st.success("Correct!")
                            st.session_state.quiz_score += 1
                        else:
                            st.error(f"Incorrect. The correct answer is: {question['correct_answer']}")
                        st.session_state.quiz_total += 1
            
            # Display score
            if st.session_state.quiz_total > 0:
                st.markdown(f"### Score: {st.session_state.quiz_score}/{st.session_state.quiz_total}")
    
    elif game_type == "Flashcards":
        if not st.session_state.flashcards or st.button("Generate New Flashcards"):
            vocab_prompt = f"""Create a {skill_level.lower()} vocabulary list (10 words) for someone learning {target_language} with a focus on {learning_focus.lower()}. 
            Include English meanings. Format each entry as 'word - meaning' for easy parsing."""
            
            vocab_response = gemini_response(vocab_prompt)
            st.session_state.flashcards = parse_vocab_list(vocab_response)
            st.session_state.current_card = 0
        
        if st.session_state.flashcards:
            # Flashcard navigation
            cols = st.columns([1, 3, 1])
            with cols[0]:
                if st.button("← Previous") and st.session_state.current_card > 0:
                    st.session_state.current_card -= 1
            
            with cols[2]:
                if st.button("Next →") and st.session_state.current_card < len(st.session_state.flashcards) - 1:
                    st.session_state.current_card += 1
            
            # Display current flashcard
            current = st.session_state.current_card
            total = len(st.session_state.flashcards)
            
            st.markdown(f"### Flashcard {current + 1}/{total}")
            
            card = st.session_state.flashcards[current]
            
            # Display flashcard
            st.markdown(f"## {card['word']}")
            
            if st.button("Reveal Meaning"):
                st.markdown(f"### {card['meaning']}")
    
    elif game_type == "Word Match":
        if not st.session_state.get('word_match_generated', False) or st.button("Generate New Word Match"):
            # Generate vocabulary for matching if needed
            vocab_prompt = f"""Create a {skill_level.lower()} vocabulary list (8 words) for someone learning {target_language} with a focus on {learning_focus.lower()}. 
            Include English meanings. Format each entry as 'word - meaning' for easy parsing."""
            
            vocab_response = gemini_response(vocab_prompt)
            match_vocab = parse_vocab_list(vocab_response)
            
            # Create shuffled lists for matching
            target_words = [item['word'] for item in match_vocab]
            meanings = [item['meaning'] for item in match_vocab]
            
            import random
            shuffled_meanings = meanings.copy()
            random.shuffle(shuffled_meanings)
            
            st.session_state.word_match = {
                'words': target_words,
                'original_meanings': meanings,
                'shuffled_meanings': shuffled_meanings,
                'selected': [None] * len(target_words),
                'checked': False,
                'score': 0
            }
            st.session_state.word_match_generated = True
        
        if st.session_state.get('word_match', None):
            st.markdown("### Match the words with their meanings")
            st.markdown("Select the correct meaning for each word:")
            
            match_data = st.session_state.word_match
            
            for i, word in enumerate(match_data['words']):
                st.markdown(f"**{i+1}. {word}**")
                
                # Create dropdown for each word
                selected_meaning = st.selectbox(
                    f"Select meaning for '{word}':", 
                    options=match_data['shuffled_meanings'],
                    index=0 if match_data['selected'][i] is None else match_data['shuffled_meanings'].index(match_data['selected'][i]),
                    key=f"match_{i}"
                )
                
                # Store selection
                match_data['selected'][i] = selected_meaning
            
            if st.button("Check Answers"):
                score = 0
                for i, word in enumerate(match_data['words']):
                    correct_meaning = match_data['original_meanings'][i]
                    if match_data['selected'][i] == correct_meaning:
                        st.success(f"✓ '{word}' correctly matched with '{correct_meaning}'")
                        score += 1
                    else:
                        st.error(f"✗ '{word}' should be matched with '{correct_meaning}'")
                
                st.session_state.word_match['checked'] = True
                st.session_state.word_match['score'] = score
                
                # Display score
                st.markdown(f"### Score: {score}/{len(match_data['words'])}")
    
    elif game_type == "Hangman":
        # Initialize hangman game if needed
        if not st.session_state.get('hangman_initialized', False) or st.button("New Game"):
            # Get a random word from target language vocabulary
            if not st.session_state.get('hangman_vocab', None):
                vocab_prompt = f"""Create a {skill_level.lower()} vocabulary list (15 words) for someone learning {target_language} with a focus on {learning_focus.lower()}. 
                Include only single words (no phrases) with English meanings. Format each entry as 'word - meaning' for easy parsing."""
                
                vocab_response = gemini_response(vocab_prompt)
                hangman_vocab = parse_vocab_list(vocab_response)
                st.session_state.hangman_vocab = hangman_vocab
            
            # Select a random word
            import random
            selected_item = random.choice(st.session_state.hangman_vocab)
            
            # Initialize game state
            st.session_state.hangman = {
                'word': selected_item['word'].lower(),
                'meaning': selected_item['meaning'],
                'guessed_letters': set(),
                'max_attempts': 6,
                'attempts': 0,
                'game_over': False,
                'won': False
            }
            st.session_state.hangman_initialized = True
        
        if st.session_state.get('hangman', None):
            game = st.session_state.hangman
            
            # Display current state
            st.markdown("### Hangman Game")
            
            # Display word with blanks for unguessed letters
            display_word = ""
            all_guessed = True
            
            for letter in game['word']:
                if letter in game['guessed_letters'] or not letter.isalpha():
                    display_word += letter + " "
                else:
                    display_word += "_ "
                    all_guessed = False
            
            st.markdown(f"## {display_word}")
            
            # Display meaning as a hint
            st.markdown(f"**Hint:** {game['meaning']}")
            
            # Display guessed letters
            st.markdown(f"**Guessed letters:** {', '.join(sorted(game['guessed_letters'])) if game['guessed_letters'] else 'None'}")
            
            # Display attempts left
            attempts_left = game['max_attempts'] - game['attempts']
            st.markdown(f"**Attempts left:** {attempts_left}")
            
            # Display hangman figure
            hangman_stages = [
                """
                -----
                |   
                |   
                |   
                |   
                ------
                """,
                """
                -----
                |   O
                |   
                |   
                |   
                ------
                """,
                """
                -----
                |   O
                |   |
                |   
                |   
                ------
                """,
                """
                -----
                |   O
                |  /|
                |   
                |   
                ------
                """,
                """
                -----
                |   O
                |  /|\\
                |   
                |   
                ------
                """,
                """
                -----
                |   O
                |  /|\\
                |  / 
                |   
                ------
                """,
                """
                -----
                |   O
                |  /|\\
                |  / \\
                |   
                ------
                """
            ]
            
            st.text(hangman_stages[game['attempts']])
            
            # Check if game is over
            if all_guessed:
                st.success("🎉 Congratulations! You guessed the word!")
                game['game_over'] = True
                game['won'] = True
            elif attempts_left <= 0:
                st.error(f"😢 Game over! The word was: {game['word']}")
                game['game_over'] = True
            
            # Letter input if game is not over
            if not game['game_over']:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    letter = st.text_input("Guess a letter:", max_chars=1).lower()
                
                with col2:
                    if st.button("Guess") and letter:
                        if letter.isalpha():
                            if letter in game['guessed_letters']:
                                st.warning(f"You already guessed '{letter}'!")
                            else:
                                game['guessed_letters'].add(letter)
                                
                                if letter not in game['word']:
                                    game['attempts'] += 1
                                    if game['attempts'] >= game['max_attempts']:
                                        st.error(f"😢 Game over! The word was: {game['word']}")
                                        game['game_over'] = True
                        else:
                            st.warning("Please enter a valid letter.")
                
                # Also allow clicking on letters
                st.markdown("### Click to guess:")
                alphabet = "abcdefghijklmnopqrstuvwxyz"
                
                # Create 3 rows of letters
                for i in range(0, len(alphabet), 9):
                    cols = st.columns(min(9, len(alphabet) - i))
                    for j, col in enumerate(cols):
                        letter_idx = i + j
                        if letter_idx < len(alphabet):
                            current_letter = alphabet[letter_idx]
                            button_state = current_letter in game['guessed_letters']
                            
                            # Use a unique key for each button
                            if col.button(
                                current_letter.upper(), 
                                key=f"btn_{current_letter}", 
                                disabled=button_state or game['game_over']
                            ):
                                if current_letter not in game['guessed_letters']:
                                    game['guessed_letters'].add(current_letter)
                                    
                                    if current_letter not in game['word']:
                                        game['attempts'] += 1
                                        if game['attempts'] >= game['max_attempts']:
                                            st.error(f"😢 Game over! The word was: {game['word']}")
                                            game['game_over'] = True
                                    
                                    # Force page refresh to update UI
                                    st.rerun()


# Add this function to make sure we generate 20 questions
def generate_quiz(vocabulary, num_questions=20):
    """Generate quiz questions from vocabulary list."""
    import random
    
    # Ensure we have enough vocabulary
    if len(vocabulary) < num_questions:
        # Just in case we don't have enough vocabulary items
        return generate_quiz(vocabulary * (num_questions // len(vocabulary) + 1), num_questions)
    
    questions = []
    words_used = set()
    
    # Make sure we have exactly the requested number of questions
    while len(questions) < num_questions:
        # Select unused vocabulary items for this question
        available_items = [item for i, item in enumerate(vocabulary) if i not in words_used]
        if not available_items:  # If we've used all vocabulary items, reset
            words_used = set()
            available_items = vocabulary
            
        item = random.choice(available_items)
        words_used.add(vocabulary.index(item))
        
        # Randomly choose question type
        question_type = random.choice(['multiple_choice', 'fill_blank'])
        
        if question_type == 'multiple_choice':
            # Create multiple choice question
            question_format = random.choice([
                f"What is the meaning of '{item['word']}'?",
                f"Which translation is correct for '{item['word']}'?"
            ])
            
            # Generate options (including the correct answer)
            options = [item['meaning']]
            
            # Add incorrect options
            other_items = [v for v in vocabulary if v != item]
            random.shuffle(other_items)
            
            for other_item in other_items[:3]:  # Add 3 distractors
                if other_item['meaning'] not in options:
                    options.append(other_item['meaning'])
                if len(options) >= 4:
                    break
            
            # If we couldn't get 4 unique options, add some variations
            while len(options) < 4:
                fake_meaning = random.choice(vocabulary)['meaning'] + " (modified)"
                if fake_meaning not in options:
                    options.append(fake_meaning)
            
            random.shuffle(options)
            
            questions.append({
                'type': 'multiple_choice',
                'question': question_format,
                'options': options,
                'correct_answer': item['meaning']
            })
            
        elif question_type == 'fill_blank':
            # Create fill-in-the-blank question
            question_format = random.choice([
                f"What is the {target_language} word for '{item['meaning']}'?",
                f"Translate '{item['meaning']}' to {target_language}:"
            ])
            
            questions.append({
                'type': 'fill_blank',
                'question': question_format,
                'correct_answer': item['word']
            })
    
    # Take exactly the number of questions requested (in case we generated extras)
    return questions[:num_questions]


with tab6:
    st.markdown("""
    ## About this App
    
    This AI-powered language learning application helps you learn languages using Google's Gemini AI.
    
    ### Features:
    - Personalized vocabulary lists tailored to your level and interests
    - Example sentences with translations
    - Pronunciation guides and tips
    - Interactive conversation practice with AI
    - Writing exercises with feedback
    - Vocabulary quizzes and flashcards
    - Progress tracking and saved vocabulary lists
    
    ### How to use:
    1. Enter your Gemini API key in the sidebar
    2. Select your target language, skill level, and learning focus
    3. Explore the different tabs to practice various language skills
    4. Save vocabulary lists for future reference
    5. Practice regularly for best results
    
    ### Technical Details:
    - Built with Streamlit and Google's Gemini AI
    - Uses the gemini-2.0-flash model for fast responses
    - Features session state management for persistent data
    
    ### Future Enhancements:
    - Audio pronunciation examples
    - Speech recognition for pronunciation feedback
    - Progress tracking and spaced repetition
    - More interactive games and exercises
    
    Built with ❤️ using Streamlit + Gemini.
    """)
