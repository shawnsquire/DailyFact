import streamlit as st
import sqlite3
from langchain.llms import OpenAI  # Correct import based on our assumption
import datetime

# Initialize the language model using a secure API key from Streamlit secrets
llm = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Database setup
conn = sqlite3.connect('subscribers.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS subscribers
(email TEXT UNIQUE, topic TEXT)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS content
(email TEXT, fact TEXT, date_sent DATE)
''')
conn.commit()

def generate_facts(topic, num_samples=3):
    responses = []
    for _ in range(num_samples):
        prompt = f"Generate three fascinating facts about {topic}. Keep each fact to a sentence. Do not say anything other than the facts."
        response = llm(prompt=prompt, max_tokens=100)
        responses.append(response.text.strip())
    return responses

st.title('Daily Fact Subscription')

email = st.text_input("Enter your email")
topic = st.text_input("What topic are you interested in?")

if st.button('Generate Facts'):
    if not email or not topic:
        st.error("Please fill out all fields")
    else:
        samples = generate_facts(topic)
        st.write("Here are some sample facts based on your topic:")
        for i, sample in enumerate(samples, start=1):
            st.text(f"Sample {i}: {sample}")

        if st.button('Confirm Subscription'):
            try:
                c.execute("INSERT INTO subscribers (email, topic) VALUES (?, ?)", (email, topic))
                conn.commit()
                for fact in samples:
                    c.execute("INSERT INTO content (email, fact) VALUES (?, ?)", (email, fact))
                conn.commit()
                st.success("You're subscribed! You'll receive daily facts starting tomorrow.")
            except sqlite3.IntegrityError:
                st.error("You're already subscribed with this email. Please use a different email or topic.")

# Close the connection on app rerun to avoid DB locks
st.session_state['conn'] = conn
def on_close():
    st.session_state['conn'].close()
st.sidebar.button("Close connection", on_click=on_close)
