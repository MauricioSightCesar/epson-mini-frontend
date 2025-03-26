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
BG_GREY = "#F6F6F6"
TEXT_DARK = "#000000"
DARK_BLUE = "#10218B"
TEXT_LIGHT = "#4E4E4E"
ACCENT_BLUE = "#0E56E8"
ACCENT_GREEN = "#008F00"
ACCENT_RED = "#B31E1E"
ACCENT_ORANGE = "#F2B251"
GREY = "#E0E0E0"
DARK_GREY = "#4E4E4E"

st.set_page_config(page_title="EPSON Loyalty Intelligence - Query Assistant", page_icon="./assets/ELI.png", layout="wide")

st.markdown(f"""
<style>
    #root {{
        h1, h2, h3, p, span, div, button, input, select, li {{
            font-family: 'Helvetica'; !important
        }}
        h1 {{
            font-size: 1.5rem;
            margin-top: 0.2rem;
        }}
        h3 {{
            color: {DARK_BLUE};
            font-weight: 700;
            span {{
                display: none;
            }}
        }}
        .tips {{
            font-size: 1.4rem;
            padding-bottom: 5px;
        }}
        li {{
            list-style: none;
            display: flex;
            align-items: flex-start;
            gap: 5px;
            margin: 10px 0;
        }}
    }}
    .stTextInput {{
        :has(div[class^="st-"], div[class*=" st-"]) {{ 
            border-color: {BG_LIGHT};
            :focus {{
                border-color: #e2e2e2;
            }}
        }}
    }}
    #text_input_1 {{
        border: 1px solid #F5F8FF;
    }}
    #text_input_1:focus {{
        border: 1px solid #7e828a;
        border-radius: 8px;
        box-shadow: 5px 0px 0px #7E828A;
    }}
    div[data-testid^="InputInstructions"] {{
        display: none;
    }}
    .stApp {{
        background-color: {BG_LIGHT};
    }}
    .stButton>button {{
        background-color: {ACCENT_BLUE};
        border-radius: 8px;
        transition: transform 200ms, opacity 200ms, background-color 200ms;
        p {{
            color: white;
            font-weight: 400;
            font-size: 1rem;
        }}
    }}
    .stButton>button:visited,
    .stButton>button:focus,
    .stButton>button:hover {{
        border: none;
    }}
    .stButton>button:hover {{
        background-color: #174fbf;
        transition: transform 200ms, opacity 200ms, background-color 200ms;
    }}
    .stButton>button:active {{
        background-color: {DARK_BLUE};
    }}
    .stButton>button:hover {{
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
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
            margin: 140px auto 0;
            box-shadow: 0px -10px 30px 6px #0027751A;
            width: 90vw;
            max-width: 1034px;
        }}
    }}
    .stAppHeader {{
        top: 10px;
        right: 50px;
        background-color: transparent;
        .stDecoration {{
            display: none;
        }}
    }}
    .stMainBlockContainer {{
        overflow: hidden;
        padding-left: 0;
        padding-right: 0;
        padding-top: 30px;
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
    .stHorizontalBlock:has(.logo-container) {{
        display: flex;
        justify-content: flex-start;
        align-items: flex-start;
        gap: 5px;
        position: fixed;
        top: 50px;
    }}
    .stColumn:has(.alert-icon) {{
        background-color: {BG_MEDIUM};
        box-shadow: 0 3px 10px #00000033;
        border-radius: 10px;
        padding: 10px 20px;
        margin-bottom: 25px;
    }}
    .alert-icon img {{
        min-width: 24px;
        max-width: 24px;
        transform: rotate(180deg);
    }}
    .stElementContainer:has(hr) {{
        display: none;
    }}
    .intro-text {{
        padding-bottom: 8px;
    }}
    .intro-text, .tips {{
        border-bottom: 1.8px dashed {DARK_GREY};
    }}
    .example {{
        margin-left: 5px; !important
    }}
    .stAppToolbar {{
        margin-top: -8px;
    }}
    .fade {{
        content: '';
        height: 5px;
        background: linear-gradient(to bottom, rgba(251, 251, 251, 1) 0%, rgba(251, 251, 251, 0) 100%);
        position: fixed;
        margin: 140px auto 0;
        width: 90vw;
        max-width: 1028px;
        z-index: 99999;
        border-radius: 40px 40px 0 0;
        box-shadow: none;
        top: 29px;
    }}
    .stVerticalBlock:has(.intro-text) {{
        margin-top: -15px;
    }}
    #epson-loyalty-intelligence {{
        color: {DARK_BLUE};
    }}
</style>
""", unsafe_allow_html=True)

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

headers = {'Content-Type': 'application/json'}
base_url = 'https://k9tfd4slid.execute-api.us-east-1.amazonaws.com/lrn-ai-queryGenerator-beta/'
generate_query = f'{base_url}generate_query'
save_feedback = f'{base_url}user_feedback'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s| %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_generated_query(question, model_name='Amazon Nova Pro'):
        params = {
            'question': question,
            'model_name': model_name,
        }
        response = requests.get(generate_query, json=params, headers=headers)
        if response.status_code == 200 and 'query' in response.json():
           return response.json()
        
def post_feedback(feedback, log_id):
    try:
        params = {
            'feedback': feedback,
            'log_id': log_id,
        }
        response = requests.get(save_feedback, json=params, headers=headers)
        return response.status_code == 200
    except Exception as e:
        logger.exception(f"Error posting feedback: {e}")
        return False
    
def get_results(query_executor, user_question, model_name='Amazon Nova Pro'):    
    attempts = 0
    success = False
    queries_attempted = []  # Store queries for each attempt

    while attempts < 1 and not success:
        start_time = time.time()  # Start the timer

        # Gen query
        response = get_generated_query(user_question, model_name=model_name)
        query = response['query']
        log_id = response['log_id']
        if 'i don\'t know' in query.lower():
            raise Exception("I don't know")

        # Execute query
        execution_result = query_executor.execute(query)
        end_time = time.time()  # End the timer
        attempts += 1
        queries_attempted.append((attempts, query))

        if 'error' not in execution_result:
            success = True
                    
        query_generation_time = end_time - start_time

    return {
        'success': success,
        'log_id': log_id,
        'query': query,
        'queries_attempted': queries_attempted,
        'execution_result': execution_result,
        'query_generation_time': query_generation_time,
    }

def main():
    db_manager = DBConnectionManager(logger=logger)
    query_executor = ExecuteQuery(db_manager, logger=logger)
    col_title, col_logo = st.columns([5, 1])
    
    with col_title:
        st.title("EPSON Loyalty Intelligence", help="Powered by CESAR")

    with col_logo:
        st.markdown("""
        <style>
        .logo-container {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            gap: 20px;
            position: initial;
        }
        .stHorizontalBlock:has(.logo-container), .stHorizontalBlock:has(h1) {
            width: 100%;
            margin-left: 10px;
            max-width: 1000px;
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


    col1, col2, col3 = st.columns([1, 20, 1])
    with col2:
        # Initialize the selected model with session state to persist between interactions
        if "selected_model" not in st.session_state:
            st.session_state.selected_model = "Amazon Nova Pro"
        
        # Create a row with the model selection on the left and the title on the right
        col_title, col_model_select = st.columns([9.5, 0.5])
        
        with col_title:
            st.subheader("Information Assistant")
        
        with col_model_select:
            # Create a small, unobtrusive dropdown for model selection
            with st.popover("⋮", help="Settings"):
                st.session_state.selected_model = st.radio(
                    "Model:",
                    options=["Amazon Nova Pro", "gpt-4o-mini"],
                    index=0 if st.session_state.selected_model == "Amazon Nova Pro" else 1,
                    horizontal=True,
                    label_visibility="collapsed"
                )
            
        st.markdown(f"""
        <p class="intro-text" style='color: {TEXT_LIGHT};'>
        Welcome to the EPSON Loyalty Intelligence - Information Assistant. This tool helps you find 
        information about the EPSON Loyalty + Rewards program using simple questions. Just type your 
        question below, and we'll do our best to provide the answer.
        </p>
        """, unsafe_allow_html=True)

        # Remove the previous model selection UI that was here
        st.markdown("**Enter your question:**")

        if 'query_results' not in st.session_state:
            st.session_state.query_results = None
        
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            user_question = st.text_input(
                "What would you like to know about the EPSON Loyalty + Rewards program?", 
                placeholder="e.g., Which companies have earned the most points in the last 3 months?",
                max_chars=200,
                label_visibility="collapsed"
            )

        with col_btn:
            if st.button("Get answer", use_container_width=True):
                st.session_state.query_results = None

        # If the user has asked a question and the query is ready to run, execute the query
        if user_question:
            with st.spinner("Finding your answer..."):
                try:
                    # If the query results haven't been fetched yet, get them
                    if st.session_state.query_results is None:
                        st.session_state.query_results = get_results(query_executor, user_question, model_name=st.session_state.selected_model)

                    # If the query was successful, display the results
                    if st.session_state.query_results and st.session_state.query_results['success']:
                        log_id = st.session_state.query_results['log_id']
                        query = st.session_state.query_results['query']
                        execution_result = st.session_state.query_results['execution_result']
                        attempts = len(st.session_state.query_results['queries_attempted'])
                    
                        st.success("Here's what we found:")
                                    
                        with st.expander("View the technical details"):
                            st.subheader("SQL Queries for Each Attempt:")
                            for attempt_num, attempted_query in st.session_state.query_results['queries_attempted']:
                                st.text(f"Attempt {attempt_num}:")
                                st.code(attempted_query, language="sql")

                        col_result, col_thumbs_up, col_thumbs_down = st.columns([9, 0.5, 0.5])

                        with col_result:
                            st.subheader("Results:")

                        if 'feedback' not in st.session_state.query_results:
                            with col_thumbs_up:
                                if st.button("👍", key=f"thumbs_up_{log_id}", disabled=('feedback' in st.session_state.query_results)):
                                    post_feedback("positive", log_id)
                                    st.session_state.query_results['feedback'] = "positive"
                                    st.rerun()

                            with col_thumbs_down:
                                if st.button("👎", key=f"thumbs_down_{log_id}", disabled=('feedback' in st.session_state.query_results)):
                                    post_feedback("negative", log_id)
                                    st.session_state.query_results['feedback'] = "positive"
                                    st.rerun()

                        df = pd.DataFrame(execution_result['rows'], columns=execution_result['columns'])
                        df = df[[col for col in df.columns if '_id' not in col.lower() and '_pk' not in col.lower()]]
                        df = df.reset_index(drop=True)
                        st.dataframe(df, use_container_width=True, hide_index=True)

                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col1:
                            st.info(f"Found {execution_result['row_count']} results in {execution_result['execution_time']:.2f} seconds")
                        with col2:
                            st.info(f"Time to find answer: {st.session_state.query_results['query_generation_time']:.2f} seconds")
                        with col3:
                            st.info(f"Attempts taken: {attempts}")
                        
                        if 'LIMIT' in query.upper():
                            st.info(f"ℹ️ Note: We've limited the results to {len(df)} item{'s' if len(df) != 1 else ''}. There may be more data available.")

                    # If the query was unsuccessful, display an error message
                    elif st.session_state.query_results and st.session_state.query_results['success'] is False:
                        st.error("We're sorry, but we couldn't find an answer to your question. Could you try rephrasing it?")
                        st.info(f"Attempts taken: {attempts}")
                        if query:
                            with st.expander("Technical details"):
                                st.code(query, language="sql")

                except Exception as e:
                    if str(e) == "I don't know":
                        st.info(
                            "I'm sorry, but I couldn't generate a valid query for your question. This might be because:\n\n"
                            "- The question isn't related to the available database,\n"
                            "- Some important information is missing,\n"
                            "- Or it's a type of request the system isn't able to handle.\n\n"
                            "Feel free to try rephrasing your question or providing more details!"
                        )

                    else:
                        st.error("We're sorry, but something went wrong. Please try again later.")
                        with open('error_log.csv', 'a') as f:
                            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},{user_question},{e}\n")
        
        # If the user hasn't asked a question yet, display a warning
        else:
            st.warning("Please enter a question to get started.")
    

    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 20, 1])
    with col2:
        st.markdown("""
        <h3 class="tips">Tips for asking good questions</h3>
        <ul>
        <li>
            <div class="alert-icon">
                <img src="data:image/png;base64,{}" width="24">
            </div>
            Be specific about what information you need from the EPSON Loyalty + Rewards program</li>
        <li>
            <div class="alert-icon">
                <img src="data:image/png;base64,{}" width="24">
            </div>
            Include time periods or other details in your question when relevant</li>
        </ul>
        
        <p class="example" style="margin-left: 15px"><em>Example: "How many companies were registered last year?"</em></p>
        """.format(
            get_image_base64(str(assets_path / "alert-circle.png")),
            get_image_base64(str(assets_path / "alert-circle.png"))
        ), unsafe_allow_html=True)

st.markdown(f"""
    <div class="fade"></div>
""", unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()