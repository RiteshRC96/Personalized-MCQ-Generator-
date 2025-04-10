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

# =============================================================================
# Initialize Chat Model (MCQ Generation)
# =============================================================================
chat = ChatGroq(
    temperature=0.7,
    model_name="llama3-70b-8192",
    groq_api_key="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"
)

# =============================================================================
# LLM Query Function for MCQ Generation
# =============================================================================
def query_llama3(user_query):
    topic = st.session_state.topic  # ✅ Use dynamic topic from user input
    system_prompt = f"""
System Prompt: You are an expert educational assessment generator specialized in creating high-quality multiple-choice questions (MCQs) for students on the topic {topic}. Your job is to:

• Generate well-structured, relevant, and accurate MCQs strictly based on the given topic.
• Each MCQ must have exactly four options (A, B, C, D), with only one correct answer.
• Ensure the options are logically consistent and plausible to avoid obvious guessing.
• Output the MCQs in the following exact format:
  [Question, Option A, Option B, Option C, Option D, Correct Answer]
• Provide the result as a valid Python list of such lists — no extra text, no explanation.
• Each inner list must contain exactly 6 elements as described above.
• Do not generate imaginary or factually incorrect content.
• Ensure all questions are grammatically correct and clearly worded.
• Do not include any introduction, headers, or notes — only return the list structure.
"""
    past_chat = st.session_state.memory.load_memory_variables({}).get("chat_history", [])
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Past Chat: {past_chat}\n\nUser: {user_query}")
    ]
    try:
        response = chat.invoke(messages)
        st.session_state.memory.save_context({"input": user_query}, {"output": response.content})
        return response.content if response else "⚠️ No response."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
# =============================================================================
# Page Configuration & Modern Styling
# =============================================================================
st.set_page_config(page_title="🧠QuizCrafter AI", page_icon="O.O", layout="centered")
st.markdown("""
<style>
html, body {
    background-color: #f9f9f9;
}
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
st.markdown("<div class='title'>Crafting Questions.✍️ Empowering Minds✨</div>", unsafe_allow_html=True)

# =============================================================================
# MCQ Generator Section
# =============================================================================
def render_mcq_generator():
    # If no test in progress, show topic input and generate button
    if st.session_state.current_question == 0 and not st.session_state.questions:
        st.session_state.topic = st.text_input("🎯 Enter a Topic to Generate MCQs:", key="topic_input")
        if st.button("🚀 Generate MCQs"):
            st.session_state.generate_button = True

    # Generate MCQs (once)
    if st.session_state.once and st.session_state.topic and st.session_state.generate_button:
        response_content = query_llama3(st.session_state.topic)
        try:
            st.session_state.questions = ast.literal_eval(response_content)
        except Exception as e:
            st.error("Error parsing MCQ response: " + str(e))
            st.stop()
        st.session_state.total = len(st.session_state.questions)
        st.session_state.once = False
        st.session_state.done = False
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answers = []

    # Display current MCQ and handle answer selection
    if st.session_state.questions and not st.session_state.done:
        idx = st.session_state.current_question
        current_question_data = st.session_state.questions[idx]
        question_text = current_question_data[0]
        options = current_question_data[1:-1]
        correct_answer = current_question_data[-1]

        with st.container():
            st.markdown(f"<div class='question-box'><strong>Q{idx+1}:</strong> {question_text}</div>", unsafe_allow_html=True)
            answer = None
            for i, option in enumerate(options):
                if st.button(option, key=f"answer_{i}_{idx}"):
                    answer = option

            if answer is not None:
                st.session_state.answers.append(answer)
                if answer == correct_answer:
                    st.session_state.score += 1
                if st.session_state.current_question < st.session_state.total - 1:
                    st.session_state.current_question += 1
                    st.rerun()  # ✅ Updated here
                else:
                    st.session_state.done = True
                    st.rerun()  # ✅ Updated here

    # Completion summary
    if st.session_state.done:
        st.markdown("<div class='score-box'>✅ You've completed the test!<br><br>" +
                    f"🎉 Your score is <strong>{st.session_state.score}</strong> out of <strong>{st.session_state.total}</strong>.</div>", unsafe_allow_html=True)
        if st.button("🔄 Start New Test"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()  # ✅ Updated here

# =============================================================================
# Run App
# =============================================================================
def main():
    render_mcq_generator()

if __name__ == "__main__":
    main()
