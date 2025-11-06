"""
Configuration file for the Class Note Organizer
"""
import streamlit as st

def get_gemini_api_key():
    """
    Retrieve Gemini API key from Streamlit secrets
    """
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception as e:
        st.error(f"Error loading API key: {e}")
        st.error("Please add GEMINI_API_KEY to your .streamlit/secrets.toml file")
        return None

# Font sizes for PDF generation
FONT_SIZES = {
    'pdf_title': 24,
    'topic_title': 18,
    'heading1': 16,
    'heading2': 14,
    'heading3': 12,
    'body': 10,
    'subheading': 11
}

# Markdown styling
MARKDOWN_STYLES = {
    'heading1': '# ',
    'heading2': '## ',
    'heading3': '### ',
    'bullet': '• ',
    'numbered': '1. '
}
