"""
Class Note Organizer - Streamlit App
"""
import streamlit as st
from config import get_gemini_api_key
from langgraph_agent import NoteOrganizerAgent
from pdf_generator import PDFGenerator
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Class Note Organizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1557a0;
    }
    .pdf-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'notes_collection' not in st.session_state:
        st.session_state.notes_collection = []
    if 'current_markdown' not in st.session_state:
        st.session_state.current_markdown = ""
    if 'pdf_buffer' not in st.session_state:
        st.session_state.pdf_buffer = None
    if 'pdf_title' not in st.session_state:
        st.session_state.pdf_title = ""
    if 'show_editor' not in st.session_state:
        st.session_state.show_editor = False
    if 'edited_content' not in st.session_state:
        st.session_state.edited_content = ""
    if 'agent' not in st.session_state:
        api_key = get_gemini_api_key()
        if api_key and api_key != "your-gemini-api-key-here":
            st.session_state.agent = NoteOrganizerAgent(api_key)
        else:
            st.session_state.agent = None


def display_pdf(pdf_buffer: BytesIO):
    """Display PDF in the viewer"""
    if pdf_buffer:
        pdf_buffer.seek(0)
        base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
        pdf_display = f'''
            <iframe src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" height="800" type="application/pdf">
            </iframe>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)


def main():
    """Main application"""
    initialize_session_state()
    
    st.markdown('<h1 class="main-header">📚 Class Note Organizer</h1>', 
                unsafe_allow_html=True)
    
    # Check if API key is configured
    if not st.session_state.agent:
        st.error("⚠️ Gemini API key not configured!")
        st.info("""
        Please add your Gemini API key to `.streamlit/secrets.toml`:
        
        ```toml
        GEMINI_API_KEY = "your-api-key-here"
        ```
        
        For Streamlit Cloud: Add the key in App Settings > Secrets
        """)
        return
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input Section")
        
        # PDF Title Input (persists across topics)
        pdf_title = st.text_input(
            "PDF Title (Main Document Title)",
            value=st.session_state.pdf_title,
            placeholder="Enter the main PDF title...",
            help="This appears on the first page with the largest font size"
        )
        if pdf_title:
            st.session_state.pdf_title = pdf_title
        
        # Topic Title Input
        topic_title = st.text_input(
            "Topic Title",
            placeholder="Enter the topic title...",
            help="Title for this specific topic/section"
        )
        
        # Content Text Area
        content = st.text_area(
            "Topic Content",
            height=300,
            placeholder="Paste your class notes here...",
            help="Paste the content for this topic"
        )
        
        # Optional User Prompt
        with st.expander("🔧 Optional: Custom Modifications", expanded=False):
            user_prompt = st.text_area(
                "Custom Prompt (Optional)",
                height=100,
                placeholder="E.g., 'Make the content more concise' or 'Add more structure'...",
                help="Optional: Specify custom modifications to apply to your notes"
            )
        
        # Generate Button
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            generate_btn = st.button("🚀 Generate Markdown", type="primary")
        
        # Process content when Generate is clicked
        if generate_btn:
            if not pdf_title:
                st.error("Please enter a PDF title!")
            elif not topic_title:
                st.error("Please enter a topic title!")
            elif not content:
                st.error("Please enter some content!")
            else:
                with st.spinner("Processing your notes..."):
                    try:
                        # Process notes through LangGraph agent
                        result = st.session_state.agent.process_notes(
                            content=content,
                            user_prompt=user_prompt if 'user_prompt' in locals() else ""
                        )
                        
                        # Check for errors
                        if result.get('error'):
                            # Show warning for rate limits but continue with fallback
                            if result.get('rate_limited', False):
                                st.warning(result['error'])
                                st.info("📝 Using fallback formatting (basic structure detection). The output may be less refined but still functional.")
                            else:
                                st.error(f"Error: {result['error']}")
                        
                        # Show success even with fallback
                        if result.get('markdown_output'):
                            st.session_state.current_markdown = result['markdown_output']
                            st.session_state.edited_content = result['markdown_output']
                            st.session_state.show_editor = False
                            
                            if result.get('fallback_used', False):
                                st.success("✅ Markdown generated using fallback formatting!")
                                st.info("💡 Tip: You can still edit the output and generate PDF. To get AI-enhanced formatting, wait for your API quota to reset or upgrade your plan.")
                            else:
                                st.success("✅ Markdown generated successfully!")
                        else:
                            st.error("Failed to generate markdown output")
                            
                    except Exception as e:
                        st.error(f"Error processing notes: {str(e)}")
                        st.info("💡 Tip: If you're seeing rate limit errors, the app will automatically use fallback formatting.")
        
        # Display Markdown Output
        if st.session_state.current_markdown:
            st.markdown("---")
            st.subheader("📄 Generated Markdown")
            st.markdown(st.session_state.current_markdown)
            
            # Text Editor Button
            if st.button("✏️ Open Text Editor"):
                st.session_state.show_editor = True
            
            # Text Editor
            if st.session_state.show_editor:
                st.markdown("### Text Editor")
                st.info("Edit your markdown below. You can use all markdown syntax including **bold**, *italic*, headings, lists, etc.")
                
                edited_content = st.text_area(
                    "Edit Content",
                    value=st.session_state.edited_content,
                    height=400,
                    key="editor"
                )
                st.session_state.edited_content = edited_content
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Save Changes"):
                        st.session_state.current_markdown = edited_content
                        st.session_state.show_editor = False
                        st.success("Changes saved!")
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel"):
                        st.session_state.show_editor = False
                        st.rerun()
            
            # Generate PDF Button
            if not st.session_state.show_editor:
                if st.button("📄 Generate PDF", type="primary"):
                    with st.spinner("Generating PDF..."):
                        try:
                            # Store the current note
                            current_note = {
                                'topic_title': topic_title,
                                'markdown_content': st.session_state.current_markdown
                            }
                            st.session_state.notes_collection.append(current_note)
                            
                            # Generate PDF with all notes
                            pdf_gen = PDFGenerator(st.session_state.pdf_title)
                            pdf_buffer = pdf_gen.generate_pdf_from_all_notes(
                                st.session_state.notes_collection
                            )
                            st.session_state.pdf_buffer = pdf_buffer
                            
                            st.success("✅ PDF generated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        st.subheader("📑 PDF Viewer")
        
        if st.session_state.pdf_buffer:
            # Display PDF
            display_pdf(st.session_state.pdf_buffer)
            
            # Download button
            st.session_state.pdf_buffer.seek(0)
            st.download_button(
                label="⬇️ Download PDF",
                data=st.session_state.pdf_buffer,
                file_name=f"{st.session_state.pdf_title.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            
            # Add More Notes Button
            st.markdown("---")
            if st.button("➕ Add Another Topic", type="secondary"):
                # Clear input fields but keep PDF title and PDF viewer
                st.session_state.current_markdown = ""
                st.session_state.show_editor = False
                st.session_state.edited_content = ""
                st.success("Ready to add another topic!")
                st.rerun()
        else:
            st.info("PDF will appear here after generation")
            st.markdown("""
                <div class="pdf-container">
                    <h3 style="text-align: center; color: #666;">
                        📄 No PDF Generated Yet
                    </h3>
                    <p style="text-align: center; color: #888;">
                        Enter your notes and click "Generate PDF" to see the preview here
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📖 How to Use")
        st.markdown("""
        1. **Enter PDF Title**: Main document title (largest font)
        2. **Enter Topic Title**: Title for this section
        3. **Paste Content**: Add your class notes
        4. **(Optional)** Add custom modifications in the prompt box
        5. **Generate**: Click to process and organize notes
        6. **Edit** (Optional): Use the text editor to modify output
        7. **Generate PDF**: Create PDF from the formatted notes
        8. **Add More**: Click "Add Another Topic" to append more content
        
        ---
        
        ### 🎯 Features
        - ✨ AI-powered note organization
        - 📝 Markdown formatting
        - ✏️ Built-in text editor
        - 📄 PDF generation & preview
        - ➕ Multi-topic support
        - ⬇️ Download functionality
        
        ---
        
        ### 🤖 AI Capabilities
        The AI automatically:
        - **Bolds** important keywords (sparingly)
        - Identifies **headings** (with : or -)
        - Preserves **bullets** & **numbering** (only if they exist)
        - Keeps **paragraphs** as paragraphs (no unwanted lists)
        - Manages **spacing** & **font sizes**
        - Maintains **original structure** (unless custom prompt provided)
        
        **Special Note:**
        - If your content has only paragraphs, they stay as paragraphs
        - Lists are created only where they already exist
        - Natural text flow is preserved
        
        ---
        
        ### ⚠️ API Rate Limits
        **Free Tier**: 50 requests/day
        
        If you exceed the limit:
        - ✅ **Fallback mode** activates automatically
        - 📝 Basic formatting still works
        - ✏️ Text editor available for refinement
        - 📄 PDF generation unaffected
        
        **Options**:
        - Wait 24 hours for quota reset
        - Upgrade to paid tier
        - Use fallback + manual editing
        
        [Monitor Usage](https://ai.dev/usage?tab=rate-limit) | 
        [Rate Limits Info](https://ai.google.dev/gemini-api/docs/rate-limits)
        """)
        
        # Show notes count
        if st.session_state.notes_collection:
            st.markdown("---")
            st.metric("Topics Added", len(st.session_state.notes_collection))
            
            if st.button("🔄 Start New Document"):
                st.session_state.notes_collection = []
                st.session_state.current_markdown = ""
                st.session_state.pdf_buffer = None
                st.session_state.pdf_title = ""
                st.session_state.show_editor = False
                st.rerun()


if __name__ == "__main__":
    main()
