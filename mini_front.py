import streamlit as st
import requests
import pandas as pd
from service.MySQLDatabase import DBConnectionManager, ExecuteQuery
from pathlib import Path
from os import getcwd
import base64
import logging
import time

assets_path = Path(getcwd()) / "assets"

BG_LIGHT = "#FFFFFF"
BG_MEDIUM = "#F5F8FF"
TEXT_DARK = "#000000"
DARK_BLUE = "#10218B"
TEXT_LIGHT = "#4E4E4E"
ACCENT_BLUE = "#0E56E8"
ACCENT_GREEN = "#008F00"
ACCENT_RED = "#B31E1E"
ACCENT_ORANGE = "#F2B251"
GREY = "#E0E0E0"

st.set_page_config(page_title="EPSON Loyalty Intelligence - Query Assistant", page_icon="./assets/ELI.png", layout="wide")

st.markdown(f"""
<style>
    h1, h2, h3, p, span, div, button, input, select, li {{
        font-family: 'Helvetica'; !important
    }}
    .stApp {{
        background-color: {BG_LIGHT};
    }}
    .stButton>button {{
        background-color: {ACCENT_BLUE};
        border-radius: 8px;
        p {{
            color: white;
            font-weight: 400;
            font-size: 1rem;
        }}
    }}
    .stColumn:has(> .stButton>button) {{
        max-width: 130px;
    }}
    .stButton>button:hover {{
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);  # Efeito hover
    }}
    .stHeading h3 {{
        color: {DARK_BLUE};
        font-weight: 700;
        span {{
            display: none;
        }}
    }}
    .stTextInput>div>div>input {{
        background-color: {BG_MEDIUM};
    }}
    .stSpinner>div>div {{
        border-top-color: {ACCENT_BLUE};
    }}
    .stAlert {{
        background-color: {BG_MEDIUM};
        color: {TEXT_DARK};
    }}
    .stDataFrame {{
        border: 1px solid {DARK_BLUE};
    }}
    .stMarkdown p {{
        color: {TEXT_LIGHT};
    }}
    .stAppViewContainer {{
        background-color: {BG_MEDIUM};
        .stMain {{
            background-color: {BG_LIGHT};
            border-radius: 28px 28px 0 0;
            margin: 60px 50px 0;
            box-shadow: 0px -10px 30px 6px #0027751A;
        }}
    }}
    .stAppHeader {{
        top: 60px;
        right: 50px;
        background-color: transparent;
        .stDecoration {{
            display: none;
        }}
    }}
    .stMainBlockContainer {{
        overflow: hidden;
        > div {{
            overflow-y: auto;
            overflow-x: hidden;
            height: calc(100vh - 210px);
        }}
        > div:hover {{
            &::-webkit-scrollbar-thumb {{
                background: {DARK_BLUE};
            }}
        }}
    }}
    ::-webkit-scrollbar {{
        background: {GREY};
        width: 4px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {DARK_BLUE};
        border-radius: 100px;

    }}

    .logo-container {{
        # top: 80px;
        # left: 80px;
        # position: absolute;
        position: unset;
    }}
    

</style>
""", unsafe_allow_html=True)

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

headers = {'Content-Type': 'application/json'}
base_url = 'https://k9tfd4slid.execute-api.us-east-1.amazonaws.com/lrn-ai-queryGenerator-beta/'
generate_query = f'{base_url}generate_query'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s| %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_generated_query(question, archetype='doc_ddl', k=3, model_id='amazon.nova-pro-v1:0'):
    try: 
        params = {
            'question': question,
            'archetype': archetype,
            'return_prompt': False,
            'model_id': model_id,
            'k_doc': 3,
            'k_ddl': k
        }

        response = requests.get(generate_query, json=params, headers=headers)
        if response.status_code == 200 and 'query' in response.json():
           return response.json()['query']
        
        else:
            print(f"Failed request for query: {question}")
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)
            print()

    except Exception as e:
        print(f"Error while making request for question: {question}")
        print(e)

def main():
    db_manager = DBConnectionManager(logger=logger)
    connection = db_manager.get_connection()
    query_executor = ExecuteQuery(connection, logger=logger)

    st.markdown("""
    <style>
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        position: initial;
    }

    @supports (animation-timeline: view()) {
        @keyframes scale-a-lil {
            from {
                transform: scale(1);
            }
            to {
                transform: scale(0.8);
            }
        }
    }
    .logo-container {
        animation: scale-a-lil linear both;
        animation-timeline: scroll();
        animation-range: 0% 100px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="logo-container">
        <img src="data:image/png;base64,{}" width="80">
        <img src="data:image/png;base64,{}" width="80">
    </div>
    """.format(
        get_image_base64(str(assets_path / "cesar.png")),
        get_image_base64(str(assets_path / "epson.png"))
    ), unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.title("EPSON Loyalty Intelligence", help="Powered by CESAR")
        st.subheader("Information Assistant")
        st.markdown(f"""
        <p style='color: {TEXT_LIGHT};'>
        Welcome to the EPSON Loyalty Intelligence - Information Assistant. This tool helps you find 
        information about the EPSON Loyalty + Rewards program using simple questions. Just type your 
        question below, and we'll do our best to provide the answer.
        </p>
        """, unsafe_allow_html=True)

        col_input, col_btn = st.columns([3, 1])
        with col_input:
            user_question = st.text_input(
                "What would you like to know about the EPSON Loyalty + Rewards program?", 
                placeholder="e.g., Which companies have earned the most points in the last 3 months?",
                max_chars=200,
                label_visibility="collapsed"  # Opcional: remove o label se quiser mais espaço
            )

        with col_btn:
            get_answer = st.button("Get answer", use_container_width=True)

        if user_question:
            with st.spinner("Finding your answer..."):
                try:
                    attempts = 0
                    success = False
                    ks = [3, 5, 8]
                    queries_attempted = []  # Store queries for each attempt

                    while attempts < 3 and not success:
                        start_time = time.time()  # Start the timer
                        query = get_generated_query(user_question, k=ks[attempts])
                        execution_result = query_executor.execute(query)
                        end_time = time.time()  # End the timer
                        attempts += 1
                        queries_attempted.append((attempts, ks[attempts-1], query))

                        if 'error' not in execution_result:
                            success = True
                    
                    query_generation_time = end_time - start_time

                    if query and execution_result and success:
                        st.success("✅ Here's what we found:")
                        
                        with st.expander("🔍 View the technical details"):
                            st.subheader("📜 SQL Queries for Each Attempt:")
                            for attempt_num, k_value, attempted_query in queries_attempted:
                                st.text(f"Attempt {attempt_num} (k={k_value}):")
                                st.code(attempted_query, language="sql")

                        st.subheader("📊 Results:")
                        df = pd.DataFrame(execution_result['rows'], columns=execution_result['columns'])
                        st.dataframe(df, use_container_width=True)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.info(f"⏱️ Time to find answer: {query_generation_time:.2f} seconds")
                        with col2:
                            st.info(f"📈 Found {execution_result['row_count']} results in {execution_result['execution_time']:.2f} seconds")
                        with col3:
                            st.info(f"🔄 Attempts taken: {attempts}")
                        
                        if 'LIMIT' in query.upper():
                            st.info(f"ℹ️ Note: We've limited the results to {len(df)} item{'s' if len(df) != 1 else ''}. There may be more data available.")

                    else:
                        st.error("We're sorry, but we couldn't find an answer to your question. Could you try rephrasing it?")
                        st.info(f"🔄 Attempts taken: {attempts}")
                        if query:
                            with st.expander("🐛 Technical details"):
                                st.code(query, language="sql")
                except Exception as e:
                    st.error("We're sorry, but something went wrong. Please try again later.")
                    st.exception(e)
        else:
            st.warning("Please enter a question to get started.")

    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        ### 💡 Tips for asking good questions:
        <ul style='color: {DARK_BLUE};'>
        <li>Be specific about what information you need from the EPSON Loyalty + Rewards program</li>
        <li>Include time periods or other details in your question when relevant</li>
        </ul>
        
        <p style='color: {ACCENT_BLUE};'><em>Example: "How many companies were registered last year?"</em></p>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()