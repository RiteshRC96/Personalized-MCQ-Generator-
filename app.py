import streamlit as st
import ast
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory

# =============================================================================
# Session State Initialization for MCQ Generator
# =============================================================================
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "generate_button" not in st.session_state:
    st.session_state.generate_button = False
if "once" not in st.session_state:
    st.session_state.once = True
if "questions" not in st.session_state:
    st.session_state.questions = []
if "total" not in st.session_state:
    st.session_state.total = 0
if "done" not in st.session_state:
    st.session_state.done = False
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

# =============================================================================
# Initialize Chat Model (MCQ Generation)
# =============================================================================
chat = ChatGroq(
    temperature=0.7,
    model_name="llama3-70b-8192",
    groq_api_key="YOUR_GROQ_API_KEY"  # Replace with your actual key
)

# =============================================================================
# LLM Query Function for MCQ Generation
# =============================================================================
def query_llama3(user_query):
    topic = st.session_state.topic
    system_prompt = f"""
System Prompt: You are an expert educational assessment generator specialized in creating high-quality multiple-choice questions (MCQs) for students on the topic {topic}. Your job is to:

• Generate well-structured, relevant, and accurate MCQs strictly based on the given topic.
• Each MCQ must have exactly four options (A, B, C, D), with only one correct answer.
• Ensure the options are logically consistent and plausible to avoid obvious guessing.
• Output the MCQs in the following exact format:
  [Question, Option A, Option B, Option C, Option D, Correct Answer]
• Provide the result as a valid Python list of such lists — no extra text, no explanation.
"""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]
    try:
        response = chat.invoke(messages)
        st.session_state.memory.save_context({"input": user_query}, {"output": response.content})
        return response.content if response else "⚠️ No response."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# =============================================================================
# Page Config and Styling
# =============================================================================
st.set_page_config(page_title="🧠 QuizCrafter AI", page_icon="O.O", layout="centered")
st.markdown("""
<style>
.title {
    text-align: center;
    font-size: 3em;
    font-weight: 700;
    color: #2c3e50;
    margin-top: 20px;
    margin-bottom: 30px;
}
.question-box {
    background-color: #000000;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    color: white;
}
.stButton > button {
    margin: 8px 4px;
    width: 100%;
    border-radius: 10px;
    padding: 12px;
    font-weight: bold;
    transition: 0.3s ease;
    background-color: #3498db;
    color: white;
}
.stButton > button:hover {
    background-color: #2c80b4;
}
.score-box {
    text-align: center;
    background-color: #ecf0f1;
    padding: 20px;
    border-radius: 10px;
    font-size: 1.2em;
    color: #2c3e50;
}
</style>
""", unsafe_allow_html=True)
st.markdown("<div class='title'>QuizCrafter AI ✍️ – Crafting Questions. Empowering Minds ✨</div>", unsafe_allow_html=True)

# =============================================================================
# MCQ Generator Logic
# =============================================================================
def render_mcq_generator():
    # Initial topic input
    if st.session_state.current_question == 0 and not st.session_state.questions:
        st.session_state.topic = st.text_input("🎯 Enter a Topic to Generate MCQs:")
        if st.button("🚀 Generate MCQs"):
            st.session_state.generate_button = True

    # Generate MCQs
    if st.session_state.once and st.session_state.topic and st.session_state.generate_button:
        response_content = query_llama3(st.session_state.topic)
        try:
            st.session_state.questions = ast.literal_eval(response_content)
        except Exception as e:
            st.error("❌ Error parsing MCQ response: " + str(e))
            st.stop()
        st.session_state.total = len(st.session_state.questions)
        st.session_state.once = False
        st.session_state.done = False
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answers = []

    # Display current question
    if st.session_state.questions and not st.session_state.done:
        idx = st.session_state.current_question
        q_data = st.session_state.questions[idx]
        question_text = q_data[0]
        options = q_data[1:-1]
        correct_answer = q_data[-1]

        st.markdown(f"<div class='question-box'><strong>Q{idx+1}:</strong> {question_text}</div>", unsafe_allow_html=True)
        st.session_state.selected_option = st.radio("Choose an answer:", options, key=f"option_{idx}")

        if st.button("Next"):
            chosen = st.session_state.selected_option
            st.session_state.answers.append(chosen)
            if chosen == correct_answer:
                st.session_state.score += 1
            if st.session_state.current_question < st.session_state.total - 1:
                st.session_state.current_question += 1
                st.session_state.selected_option = None
                st.rerun()
            else:
                st.session_state.done = True
                st.rerun()

    # Final Score
    if st.session_state.done:
        st.markdown(f"""
        <div class='score-box'>
            ✅ You've completed the test!<br><br>
            🎉 Your score is <strong>{st.session_state.score}</strong> out of <strong>{st.session_state.total}</strong>.
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Start New Test"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# =============================================================================
# Run App
# =============================================================================
def main():
    render_mcq_generator()

if __name__ == "__main__":
    main()
