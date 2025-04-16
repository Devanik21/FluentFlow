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
    
    pronunciation_type = st.radio("Select pronunciation focus", 
                                ["General Tips", "Common Sounds", "Tongue Twisters"])
    
    if st.button("Generate Pronunciation Guide"):
        if pronunciation_type == "General Tips":
            pronounce_prompt = f"""Provide pronunciation tips for a {skill_level.lower()} learner in {target_language}.
            Focus on general rules and common mistakes to avoid."""
        elif pronunciation_type == "Common Sounds":
            pronounce_prompt = f"""Explain how to pronounce 5 difficult sounds in {target_language} for {skill_level.lower()} students.
            Include examples and English approximations where possible."""
        else:
            pronounce_prompt = f"""Create 3 tongue twisters in {target_language} for {skill_level.lower()} students 
            with translations and pronunciation notes."""
            
        pronunciation = gemini_response(pronounce_prompt)
        st.markdown(pronunciation)
    
    # Audio placeholder
    st.header("🎵 Audio Examples")
    st.write("This feature would connect to a text-to-speech API to provide audio examples.")
    st.caption("Note: Audio functionality requires additional API integration.")
    
    # Pronunciation feedback
    st.header("🎤 Pronunciation Feedback")
    st.write("This feature would allow users to record their pronunciation and get feedback.")
    st.caption("Note: Speech recognition functionality requires additional API integration.")



with tab4:
    st.header("📝 Writing Practice")
    
    writing_type = st.selectbox("Writing Exercise Type", 
                   ["Guided Composition", "Translation Exercise", "Fill in the Blanks", "Creative Writing"])
    
    if writing_type == "Guided Composition":
        st.write(f"Write a short paragraph in {target_language} about one of these topics:")
        topics = gemini_response(f"Generate 3 {skill_level.lower()} level writing topics for {target_language} students interested in {learning_focus.lower()}.")
        st.markdown(topics)
    
    elif writing_type == "Translation Exercise":
        if st.button("Generate Translation Exercise"):
            translation_prompt = f"""Create a {skill_level.lower()} level translation exercise for English to {target_language}.
            Provide 3 sentences in English appropriate for {learning_focus.lower()} context.
            Then provide the correct {target_language} translations separately."""
            
            translation_exercise = gemini_response(translation_prompt)
            st.markdown(translation_exercise)
    
    elif writing_type == "Fill in the Blanks":
        if st.button("Generate Fill-in-the-Blanks Exercise"):
            fill_prompt = f"""Create a {skill_level.lower()} level fill-in-the-blanks exercise in {target_language} 
            related to {learning_focus.lower()} topics. 
            Provide a paragraph with 5 blanks, and list the correct answers separately."""
            
            fill_exercise = gemini_response(fill_prompt)
            st.markdown(fill_exercise)
    
    elif writing_type == "Creative Writing":
        st.write(f"Write a creative piece in {target_language} based on this prompt:")
        if st.button("Generate Creative Writing Prompt"):
            creative_prompt = f"Generate a creative writing prompt for {skill_level.lower()} {target_language} students."
            prompt_idea = gemini_response(creative_prompt)
            st.markdown(prompt_idea)
    
    # Writing submission
    user_writing = st.text_area("Your writing:", height=150)
    
    if user_writing and st.button("Get Feedback"):
        feedback_prompt = f"""Provide feedback on this {skill_level.lower()} {target_language} writing sample:
        
        "{user_writing}"
        
        Include:
        1. Grammar corrections
        2. Vocabulary suggestions
        3. Style improvements
        4. Overall assessment
        
        Be encouraging but thorough."""
        
        feedback = gemini_response(feedback_prompt)
        st.markdown("### Feedback")
        st.markdown(feedback)

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
                                    st.experimental_rerun()


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
