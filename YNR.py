import time
import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '🦝'

st.write('# Your Next Read')

# Button to restart the session
if st.button('Restart Session'):
    st.session_state.clear()
    st.experimental_rerun()

# Initialize chat history and AI response flag
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'gemini_history' not in st.session_state:
    st.session_state.gemini_history = []

if 'ai_responded' not in st.session_state:
    st.session_state.ai_responded = False

st.session_state.model = genai.GenerativeModel('gemini-pro')
st.session_state.chat = st.session_state.model.start_chat(
    history=st.session_state.gemini_history
)

# Define possible book genres
genres = [
    'Science Fiction', 'Fantasy', 'Mystery', 'Thriller', 'Romance',
    'Non-fiction', 'Historical Fiction', 'Horror', 'Biography', 'Self-Help',
    'Adventure', 'Classics', 'Poetry', 'Graphic Novels', 'Young Adult',
    'Dystopian', 'Memoir', 'Psychological Thriller', 'Contemporary Fiction',
    'Literary Fiction', 'Crime', 'Humor', 'Spirituality', 'Philosophy',
    'Travel', 'Science', 'Technology', 'Art', 'Cookbooks', 'Drama', 
    'Short Stories', 'Children Literature', 'Western', 'Chick Lit',
    'Political Fiction', 'War', 'True Crime', 'New Adult', 'Urban Fantasy'
]

# Step 1: Ask the user for their desired genres
selected_genres = st.multiselect(
    'Select your preferred book genres:',
    options=genres,
    disabled=st.session_state.ai_responded
)

# Step 2: Ask the user if they want to skip entering read books
if selected_genres:
    skip_readlist = st.checkbox("I haven't read any books in these genres", disabled=st.session_state.ai_responded)

    if not skip_readlist:
        readlist = st.text_area(
            "Enter a list of books you have already read:",
            disabled=st.session_state.ai_responded
        )
    else:
        readlist = None

    # Add an "Enter" button to submit the readlist
    if st.button('Submit Readlist', disabled=st.session_state.ai_responded):
        read_books = []
        if readlist:
            # Convert readlist into a list of book titles if provided
            read_books = [book.strip() for book in readlist.split(',')]

        # Initial prompt based on user-selected genres and readlist
        initial_prompt = (
            f"You are 'Your Next Read', an AI book recommender. The user is interested in the following genres: {', '.join(selected_genres)}. "
        )

        if read_books:
            initial_prompt += f"They have already read the following books: {', '.join(read_books)}. "
        else:
            initial_prompt += "They haven't read any books in these genres yet. "

        initial_prompt += "Based on this information, recommend books they might enjoy, providing brief descriptions and relevant details for each suggestion."

        # Send the initial prompt to the AI
        response = st.session_state.chat.send_message(
            initial_prompt,
            stream=True,
        )

        # Display AI response
        with st.chat_message(
            name=MODEL_ROLE,
            avatar=AI_AVATAR_ICON,
        ):
            message_placeholder = st.empty()
            full_response = ''
            assistant_response = response

            # Streams in a chunk at a time
            for chunk in response:
                for ch in chunk.text.split(' '):
                    full_response += ch + ' '
                    time.sleep(0.05)
                    message_placeholder.write(full_response + '▌')
            message_placeholder.write(full_response)

        # Add the interaction to the chat history
        st.session_state.messages.append(
            dict(
                role='user',
                content=initial_prompt,
            )
        )
        st.session_state.messages.append(
            dict(
                role=MODEL_ROLE,
                content=full_response,
                avatar=AI_AVATAR_ICON,
            )
        )

        # Store the entire session history for context
        st.session_state.gemini_history.extend([
            dict(role='user', content=initial_prompt),
            dict(role=MODEL_ROLE, content=full_response)
        ])

        # Disable further input after AI response
        st.session_state.ai_responded = True

else:
    st.write("Please select at least one genre to get started.")
