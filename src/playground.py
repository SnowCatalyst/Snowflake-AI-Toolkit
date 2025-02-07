import streamlit as st
import json
from src.cortex_functions import *
from snowflake.snowpark.exceptions import SnowparkSQLException
from src.utils import *
from pathlib import Path

# Load the config file
config_path = Path("src/settings_config.json")
with open(config_path, "r") as f:
    config = json.load(f)


def execute_functionality(session, functionality, input_data, settings):
    """
    Executes the selected functionality in playground mode.
    
    Args:
        session: Snowflake session object for database operations
        functionality (str): The selected functionality to execute ("Complete", "Translate", etc.)
        input_data (dict): Dictionary containing input data for the selected functionality
        settings (dict): Dictionary containing settings for the selected functionality
        
    Displays the results of the executed functionality using Streamlit components.
    """
    if functionality == "Complete":
        result_json = get_complete_result(
            session, settings['model'], input_data['prompt'],
            settings['temperature'], settings['max_tokens'], settings['guardrails'], settings['system_prompt']
        )
        result_formatted = format_result(result_json)
        st.write("Completion Result")
        st.write(f"**Messages:**")
        st.success(result_formatted['messages'])

    elif functionality == "Translate":
        result = get_translation(session,input_data['text'], settings['source_lang'], settings['target_lang'])
        st.write(f"**Translated Text:** {result}")

    elif functionality == "Summarize":
        result = get_summary(session,input_data['text'])
        st.write(f"**Summary:** {result}")

    elif functionality == "Extract":
        result = get_extraction(session,input_data['text'], input_data['query'])
        st.write(f"**Extracted Answer:** {result}")

    elif functionality == "Sentiment":
        result = get_sentiment(session,input_data['text'])
        st.write(f"**Sentiment Analysis Result:** {result}")

def get_functionality_settings(functionality, config):
    """
    Returns settings based on the selected functionality from config.
    
    Args:
        functionality (str): The selected functionality ("Complete", "Translate", etc.)
        config (dict): Configuration dictionary containing default settings
        
    Returns:
        dict: Dictionary containing the settings for the selected functionality
    """
    settings = {}
    defaults = config["default_settings"]

    if functionality == "Complete":
        is_private_preview_model_shown = st.checkbox("Show private preview models", value=False)
        settings['model'] = st.selectbox("Change chatbot model:", defaults[
                "private_preview_models" if is_private_preview_model_shown else "model"
            ])
        settings['temperature'] = st.slider("Temperature:", defaults['temperature_min'], defaults['temperature_max'], defaults['temperature'])
        settings['max_tokens'] = st.slider("Max Tokens:", defaults['max_tokens_min'], defaults['max_tokens_max'], defaults['max_tokens'])
        settings['guardrails'] = st.checkbox("Enable Guardrails", value=defaults['guardrails'])
        settings['system_prompt'] = st.text_area("System Prompt (optional):", placeholder="Enter a system prompt...")

    elif functionality == "Translate":
        settings['source_lang'] = st.selectbox("Source Language", defaults['languages'])
        settings['target_lang'] = st.selectbox("Target Language", defaults['languages'])
    return settings

def get_playground_input(functionality):
    """
    Returns input data for playground mode based on selected functionality.
    
    Args:
        functionality (str): The selected functionality ("Complete", "Translate", etc.)
        
    Returns:
        dict: Dictionary containing the input data for the selected functionality
    """
    input_data = {}
    
    if functionality == "Complete":
        input_data['prompt'] = st.text_area("Enter a prompt:", placeholder="Type your prompt here...")
    elif functionality == "Translate":
        input_data['text'] = st.text_area("Enter text to translate:", placeholder="Type your text here...")
    elif functionality == "Summarize":
        input_data['text'] = st.text_area("Enter text to summarize:", placeholder="Type your text here...")
    elif functionality == "Extract":
        input_data['text'] = st.text_area("Enter the text:", placeholder="Type your text here...")
        input_data['query'] = st.text_input("Enter your query:", placeholder="Type your query here...")
    elif functionality == "Sentiment":
        input_data['text'] = st.text_area("Enter text for sentiment analysis:", placeholder="Type your text here...")

    return input_data

def display_playground(session):
    """
    Displays the playground mode interface in Streamlit.
    
    Args:
        session: Snowflake session object for database operations
        
    Creates an interactive interface allowing users to:
    - Select different functionalities (Complete, Translate, etc.)
    - Configure settings for the selected functionality
    - Input data and execute the functionality
    - View results or error messages
    """
    st.title("Playground Mode")

    # Dropdown to choose the functionality
    functionality = st.selectbox(
        "Choose functionality:",
        ["Select Functionality", "Complete", "Translate", "Summarize", "Extract", "Sentiment"]
    )

    if functionality != "Select Functionality":
        settings = get_functionality_settings(functionality, config)
        input_data = get_playground_input(functionality)

        if st.button(f"Run {functionality}"):
            try:
                execute_functionality(session, functionality, input_data, settings)
            except SnowparkSQLException as e:
                st.error(f"Error: {e}")
