import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

# ===============================
# 🔐 Load API Key
# ===============================
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ Missing API key! Please set GOOGLE_API_KEY in your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# ===============================
# 🧠 Configure Gemini Model
# ===============================
model = genai.GenerativeModel("gemini-2.5-flash")

# ===============================
# 🏦 Define Chatbot Persona
# ===============================
PERSONA_NAME = "BankBot"
PERSONA_DESCRIPTION = """
You are BankBot, a polite and professional virtual assistant for a bank. You help customers with questions about:
- Bank opening hours
- Account creation and types
- Loan information
- Fixed deposits
- Credit/debit cards
- Internet banking
- Customer support

If someone asks something unrelated to banking, politely say:
"Sorry, I can only answer banking-related questions!"
"""

# ===============================
# 💬 Streamlit Page Configuration
# ===============================
st.set_page_config(page_title="🏦 BankBot - Your Virtual Bank Assistant", page_icon="💰", layout="centered")
st.title("🏦 BankBot - Your Virtual Banking Assistant")
st.markdown("Ask any question about our banking services, timings, loans, or account details!")

# ===============================
# 💾 Initialize Chat History
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===============================
# 💬 Display Previous Messages
# ===============================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===============================
# 🧹 Clear Chat Option
# ===============================
if st.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()

# ===============================
# 💬 User Input Section
# ===============================
if prompt := st.chat_input("Ask BankBot something..."):
    # Display user input
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Check if it's banking-related or a greeting
    allowed_topics = [
        "bank", "account", "loan", "deposit", "atm", "credit", "debit", "card",
        "balance", "interest", "timing", "hours", "branch", "ifsc", "upi",
        "internet banking", "customer care"
    ]
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]

    prompt_lower = prompt.lower()

    if any(greet in prompt_lower for greet in greetings):
        answer = "👋 Hello! How can I assist you with your banking needs today?"
    elif not any(topic in prompt_lower for topic in allowed_topics):
        answer = "Sorry, I can only answer banking-related questions!"
    else:
        # Prepare context for Gemini
        context = (
            f"{PERSONA_DESCRIPTION}\n\n"
            f"User asked: {prompt}\n\n"
            "Respond as BankBot in a clear, friendly way."
        )
        try:
            response = model.generate_content(context)
            answer = response.text.strip()
        except Exception as e:
            answer = f"⚠️ Error: {str(e)}"

    # ===============================
    # 🤖 Display Bot Reply with Typing Effect
    # ===============================
    with st.chat_message("assistant"):
        placeholder = st.empty()
        typed_text = ""
        for chunk in answer.split():
            typed_text += chunk + " "
            placeholder.markdown("💬 " + typed_text + "▌")
            time.sleep(0.03)
        placeholder.markdown(typed_text.strip())

    # Save to session state
    st.session_state.messages.append({"role": "assistant", "content": answer})
