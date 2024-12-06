import streamlit as st
import time
import pypdf
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(page_title="GenQ", page_icon="🧠", layout="wide")

class GenQApp:
    def __init__(self):
        
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%);
            color: white;
        }
        
        h1, h2, h3, h4 {
            color: white !important;
            font-family: 'Arial Black', sans-serif;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .card {
            background-color: rgba(255,255,255,0.2);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: scale(1.03);
        }
        
        .stButton > button {
            background-color: rgba(255,255,255,0.3) !important;
            color: white !important;
            border: 2px solid rgba(255,255,255,0.5) !important;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: rgba(255,255,255,0.4) !important;
            transform: scale(1.05);
        }
        
        * {
            color: white !important;
        }
        
        .animated-text {
            font-size: 24px;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        
        self.initialize_session_state()
        
        
        API_KEY = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=API_KEY)
    
    def initialize_session_state(self):
        """Initialize or reset session state variables"""
        default_states = {
            'page': "Home",
            'animated_text': "",
            'uploaded_pdf_text': "",
            'generated_mcqs': [],
            'generated_descriptive': [],
            'generated_tips': ""
        }
        
        for key, default_value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def animate_text(self, text):
        """Animate text letter by letter"""
        placeholder = st.empty()
        animated_text = ""
        for char in text:
            animated_text += char
            placeholder.markdown(f'<div class="animated-text">{animated_text}</div>', unsafe_allow_html=True)
            time.sleep(0.1)
        return placeholder
    
    def extract_pdf_text(self, uploaded_file):
        """Extract text from uploaded PDF"""
        try:
            pdf_reader = pypdf.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error extracting PDF text: {e}")
            return ""
    
    def generate_questions_and_tips(self, text):
        """Generate MCQs, Descriptive Questions, and Learning Tips using Gemini"""
        model = genai.GenerativeModel('gemini-pro')
        
        
        mcq_prompt = f"""Create 5 precise multiple-choice questions that test deep understanding of the core concepts in the following text. 
        Ensure each question:
        - Targets a key learning objective
        - Has a clear, concise stem
        - Includes 4 plausible and distinct answer options
        - Includes correct answer marked with a '✓'

        Text: {text[:4000]}

        Respond in this JSON format:
        [
            {{
                "Question": "Detailed question testing core concept",
                "Options": [
                    "a) Incorrect option 1", 
                    "b) Incorrect option 2", 
                    "c) Correct answer ✓", 
                    "d) Incorrect option 3"
                ]
            }}
        ]"""
        
        
        desc_prompt = f"""Generate 3 thought-provoking descriptive questions that encourage critical thinking and deep analysis. 
        For each question, provide:
        - A complex, multi-layered question
        - A comprehensive, insightful answer that explains reasoning

        Text: {text[:4000]}

        Respond in this JSON format:
        [
            [
                "Complex question that requires in-depth analysis",
                "Comprehensive answer explaining nuanced insights and reasoning"
            ]
        ]"""
        
        
        tips_prompt = f"""Generate 5-7 advanced learning tips and strategic insights that help learners deeply understand and retain the key concepts from the text.
        Focus on:
        - Metacognitive strategies
        - Practical application techniques
        - Critical thinking approaches
        
        Text: {text[:4000]}"""
        
        try:
            
            mcq_response = model.generate_content(mcq_prompt)
            st.session_state.generated_mcqs = json.loads(mcq_response.text)
            
            
            desc_response = model.generate_content(desc_prompt)
            st.session_state.generated_descriptive = json.loads(desc_response.text)
            
            
            tips_response = model.generate_content(tips_prompt)
            st.session_state.generated_tips = tips_response.text
        
        except Exception as e:
            st.error(f"Error generating content: {e}")
            st.session_state.generated_mcqs = []
            st.session_state.generated_descriptive = []
            st.session_state.generated_tips = "Unable to generate tips. Please try again."
    
    def render_navigation(self):
        """Render navigation as beautiful cards"""
        st.title("GenQ")
        
        
        self.animate_text("Generate Questions")
        
        
        nav_cols = st.columns(4)
        nav_items = [
            ("🏠 Home", "Home"),
            ("❓ MCQs", "MCQs"),
            ("📝 Descriptive", "Descriptive"),
            ("💡 Tips", "Tips")
        ]
        
        for col, (title, page) in zip(nav_cols, nav_items):
            with col:
                if st.button(title, key=title, use_container_width=True):
                    st.session_state.page = page
        
        st.write("---")
    
    def render_home(self):
        """Render the landing page with PDF upload"""
        self.render_navigation()
        
        
        st.markdown("""
        <div class="card">
            <h3>Upload PDF for Question Generation</h3>
            <p>Select a PDF file to generate learning materials automatically.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            
            st.session_state.uploaded_pdf_text = self.extract_pdf_text(uploaded_file)
            
            
            if st.button("Generate Questions"):
                with st.spinner("Generating questions..."):
                    self.generate_questions_and_tips(st.session_state.uploaded_pdf_text)
                st.success("Questions generated successfully!")
    
    def render_mcqs(self):
        """Render Multiple Choice Questions page with card styling"""
        self.render_navigation()
        
        if not st.session_state.generated_mcqs:
            st.warning("Please upload a PDF and generate questions first!")
            return
        
        for idx, mcq in enumerate(st.session_state.generated_mcqs, 1):
            st.markdown(f"""
            <div class="card">
                <h4>Question {idx}</h4>
                <p>{mcq['Question']}</p>
                <div style="margin-top: 10px;">
                    {' '.join([f'<div>{opt}</div>' for opt in mcq['Options']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            selected_option = st.radio(
                f"Select an answer for Question {idx}", 
                mcq['Options'], 
                key=f"mcq_{idx}"
            )
            st.write("---")
    
    def render_descriptive(self):
        """Render Descriptive Questions page with card styling"""
        self.render_navigation()
        
        if not st.session_state.generated_descriptive:
            st.warning("Please upload a PDF and generate questions first!")
            return
        
        for idx, (question, answer) in enumerate(st.session_state.generated_descriptive, 1):
            st.markdown(f"""
            <div class="card">
                <h4>Question {idx}</h4>
                <p>{question}</p>
            </div>
            """, unsafe_allow_html=True)
            
            
            if st.toggle(f"Reveal Answer for Question {idx}", key=f"desc_{idx}"):
                st.markdown(f"""
                <div class="card">
                    <h4>Answer</h4>
                    <p>{answer}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("---")
    
    def render_tips(self):
        """Render Learning Tips page with card styling"""
        self.render_navigation()
        
        if not st.session_state.generated_tips:
            st.warning("Please upload a PDF and generate tips first!")
            return
        
        st.markdown(f"""
        <div class="card">
            <h3>Learning Tips</h3>
            {st.session_state.generated_tips.replace('\\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the Streamlit app"""
        
        if st.session_state.page == "Home":
            self.render_home()
        elif st.session_state.page == "MCQs":
            self.render_mcqs()
        elif st.session_state.page == "Descriptive":
            self.render_descriptive()
        elif st.session_state.page == "Tips":
            self.render_tips()


def main():
    app = GenQApp()
    app.run()

if __name__ == "__main__":
    main()