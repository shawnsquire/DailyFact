import streamlit as st
import sqlite3
from langchain import LLM
from langchain.schema_prompting import SchemaPrompt

# Initialize LLM
llm = LLM.openai()  # assuming OpenAI's model

# Database connection
conn = sqlite3.connect('subscribers.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS subscribers
             (email TEXT, topic TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS content
             (email TEXT, fact TEXT, date_sent DATE)''')
conn.commit()

def generate_facts(topic, num_samples=3):
    schema_prompt = SchemaPrompt(llm, {"description": topic}, num_samples=num_samples)
    return schema_prompt.generate()

st.title('Daily Fact Subscription')

email = st.text_input("Enter your email", value="", max_chars=None, key=None, type="default")
topic = st.text_input("What topic are you interested in?", value="", max_chars=None, key=None, type="default")

if st.button('Generate Facts'):
    if not email or not topic:
        st.error("Please fill out all fields")
    else:
        samples = generate_facts(topic)
        st.write("Here are some sample facts based on your topic:")
        for i, sample in enumerate(samples, start=1):
            st.text(f"Sample {i}: {sample}")

        if st.button('Confirm Subscription'):
            c.execute("INSERT INTO subscribers VALUES (?, ?)", (email, topic))
            for fact in samples:
                c.execute("INSERT INTO content VALUES (?, ?, NULL)", (email, fact))
            conn.commit()
            st.success("You're subscribed! You'll receive daily facts starting tomorrow.")

conn.close()
