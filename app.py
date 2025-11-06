"""
Class Note Organizer - Streamlit App
"""
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
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


def display_pdf(pdf_buffer: BytesIO, filename: str = "class_notes.pdf"):
    """Display PDF using streamlit-pdf-viewer with professional controls - Based on structure-vision implementation"""
    if pdf_buffer:
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.read()
        
        # Add custom CSS for PDF viewer border and styling
        st.markdown("""
            <style>
            /* Style the PDF viewer container */
            iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"] {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin: 10px 0;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # PDF Viewer Controls - Professional Implementation
        with st.expander("🎛️ PDF Viewer Controls", expanded=False):
            st.markdown("### Display Settings")
            
            # Text rendering toggle
            enable_text = st.toggle(
                'Render text in PDF', 
                value=True,
                help="Enable the selection and copy-paste on the PDF"
            )
            
            st.markdown("### Annotations")
            annotation_thickness = st.slider(
                label="Annotation boxes border thickness", 
                min_value=1, 
                max_value=6, 
                value=1
            )
            
            pages_vertical_spacing = st.slider(
                label="Pages vertical spacing", 
                min_value=0, 
                max_value=10, 
                value=2
            )
            
            st.markdown("### Height and Width")
            resolution_boost = st.slider(
                label="Resolution boost", 
                min_value=1, 
                max_value=10, 
                value=1,
                help="Higher values increase PDF rendering quality"
            )
            
            size_in_pixel = st.toggle(
                'Size in pixels', 
                value=False,  # Default to percentage (responsive)
                help="Use pixel-based sizing or percentage (responsive)"
            )
            
            if size_in_pixel:
                width = st.slider(
                    label="PDF width (px)", 
                    min_value=100, 
                    max_value=1000, 
                    value=450
                )
                height = st.slider(
                    label="PDF height (px)", 
                    min_value=-1, 
                    max_value=10000, 
                    value=530,
                    help="Set to -1 for auto height (shows all pages)"
                )
            else:
                width = st.slider(
                    label="PDF width (%)", 
                    min_value=50, 
                    max_value=100, 
                    value=95,  # 95% of container width (responsive)
                    help="Percentage of available container width"
                )
                width = str(width) + "%"
                height = -1  # Auto height (shows all pages) for responsive mode
        
        try:
            # Professional PDF viewer implementation (structure-vision style)
            with st.spinner("Rendering PDF document..."):
                pdf_viewer(
                    input=pdf_bytes,
                    width=width,
                    height=height,
                    pages_vertical_spacing=pages_vertical_spacing,
                    annotation_outline_size=annotation_thickness,
                    render_text=enable_text,
                    resolution_boost=resolution_boost,
                    key=f"pdf_viewer_{id(pdf_buffer)}"
                )
            
            # Feature info
            st.info("💡 **PDF Viewer**: Scroll to navigate • Select & copy text (if enabled) • Adjust settings in controls above")
            
        except Exception as e:
            st.warning(f"PDF viewer unavailable: {str(e)}")
            st.info("💡 Use the download button below to view your PDF.")
        
        # Download button
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="Download your formatted PDF document"
        )




def main():
    """Main application"""
    initialize_session_state()
    
    # Sidebar - Interface Selector Only
    with st.sidebar:
        st.header("⚙️ Interface")
        
        # Interface selector dropdown
        interface_mode = st.selectbox(
            "Select View:",
            ["📝 Create Notes", "📖 Help & Guidelines"],
            index=0,
            key="main_interface_selector"
        )
        
        st.markdown("---")
        
        # Show quick stats only for Create Notes mode
        if interface_mode == "📝 Create Notes":
            if st.session_state.notes_collection:
                st.metric("📊 Topics Added", len(st.session_state.notes_collection))
                
                if st.button("🔄 Start New Document"):
                    st.session_state.notes_collection = []
                    st.session_state.current_markdown = ""
                    st.session_state.pdf_buffer = None
                    st.session_state.pdf_title = ""
                    st.session_state.show_editor = False
                    st.rerun()
    
    # Main content area - conditional based on interface mode
    if interface_mode == "📖 Help & Guidelines":
        # Show Help & Guidelines Interface
        show_help_interface()
        return
    
    # Otherwise show Create Notes Interface
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
            # Display PDF with download option
            pdf_filename = f"{st.session_state.pdf_title.replace(' ', '_')}.pdf" if st.session_state.pdf_title else "class_notes.pdf"
            display_pdf(st.session_state.pdf_buffer, pdf_filename)
            
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


def show_help_interface():
    """Display Help & Guidelines interface in main content area"""
    st.markdown('<h1 class="main-header">📖 Help & Guidelines</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the **Class Note Organizer** help center! This guide will help you understand 
    all features and get the most out of this tool.
    """)
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🎯 How to Use",
        "🤖 AI Capabilities", 
        "📝 Markdown Syntax",
        "✏️ Text Editor",
        "⚠️ Rate Limits",
        "💡 Best Practices",
        "🔧 Troubleshooting",
        "📚 Examples"
    ])
    
    with tab1:
        st.header("🎯 How to Use")
        st.markdown("""
        ### Step-by-Step Process
        
        #### 1. **PDF Title** - Enter the main document title
        - Appears on the first page
        - Uses the largest font size
        - Example: *"Biology Class Notes"* or *"Physics Semester 1"*
        
        #### 2. **Topic Title** - Enter section title
        - For each topic/chapter you want to add
        - Example: *"Cell Biology"* or *"Newton's Laws"*
        
        #### 3. **Content** - Paste your notes
        - Copy from any source (Word, Google Docs, web pages, etc.)
        - Can include headings, lists, paragraphs
        - Keep natural formatting
        
        #### 4. **Generate** - Click to process
        - AI analyzes and organizes content
        - Creates formatted markdown
        - Preserves your original structure
        
        #### 5. **Edit** (Optional) - Refine output
        - Use the text editor to make manual changes
        - Modify formatting, add/remove sections
        - Complete markdown control
        
        #### 6. **Generate PDF** - Create document
        - Professional formatting applied
        - Preview appears in right panel
        - Hierarchical font sizing
        
        #### 7. **Add More** - Append topics
        - Add multiple sections to the same document
        - Each with its own topic title
        - All combined in one PDF
        
        #### 8. **Download** - Save your work
        - Download button appears after PDF generation
        - Save to your computer
        - Ready to print or share
        """)
    
    with tab2:
        st.header("🤖 AI Capabilities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✨ What AI Does Automatically")
            st.markdown("""
            - **Identifies Keywords**: Bolds important terms in CAPS
            - **Detects Headings**: Recognizes headings with `:` or `-`
            - **Preserves Lists**: Keeps numbered and bullet lists intact
            - **Maintains Paragraphs**: Keeps paragraph flow natural
            - **Manages Spacing**: Appropriate spacing between sections
            - **Font Sizing**: Hierarchical sizing (Title → H1 → H2 → H3)
            - **Structure**: Maintains your original organization
            """)
        
        with col2:
            st.subheader("🎯 Special Behaviors")
            st.markdown("""
            - **Paragraph-Only Content**: Stays as paragraphs, never converted to lists
            - **List Detection**: Lists preserved only where they exist
            - **No Hallucination**: Never adds information not in original
            - **Structure Respect**: No unwanted transformations
            - **Natural Flow**: Text reads naturally, not artificially formatted
            """)
        
        st.markdown("---")
        st.subheader("📜 Strict Rules AI Follows")
        st.info("""
        🚫 **What AI Will NOT Do:**
        - Does NOT add new information
        - Does NOT modify original content meaning
        - Does NOT create fake lists from paragraphs
        - Does NOT change your intended structure
        - ONLY enhances and organizes existing content
        """)
    
    with tab3:
        st.header("📝 Markdown Syntax Guide")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Text Formatting")
            st.code("""
**Bold Text**        → Bold Text
*Italic Text*        → Italic Text  
***Bold Italic***    → Bold Italic
`Code Text`          → Code Text
            """, language="markdown")
            
            st.subheader("Headings")
            st.code("""
# Heading 1          → Largest (16pt)
## Heading 2         → Large (14pt)
### Heading 3        → Medium (12pt)
#### Heading 4       → Small (11pt)
            """, language="markdown")
        
        with col2:
            st.subheader("Lists")
            st.code("""
Bullet List:
- Item 1
- Item 2
  - Sub-item 2.1
  - Sub-item 2.2

Numbered List:
1. First item
2. Second item
3. Third item
            """, language="markdown")
            
            st.subheader("Links & Images")
            st.code("""
[Link Text](URL)     → Clickable link
![Alt Text](URL)     → Embedded image
            """, language="markdown")
        
        st.markdown("---")
        st.subheader("Line Breaks & Paragraphs")
        st.code("""
Two spaces at end  
creates line break

Blank line between text

creates new paragraph
        """, language="markdown")
    
    with tab4:
        st.header("✏️ Text Editor Tips")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📖 How to Use the Editor")
            st.markdown("""
            1. **Open Editor**: Click "Open Text Editor" button
            2. **Edit Content**: Modify markdown directly in text area
            3. **Use Syntax**: Apply markdown formatting (see Syntax tab)
            4. **Preview**: Check output in markdown preview
            5. **Save**: Click "Save Changes" when satisfied
            6. **Cancel**: Discard changes if needed
            """)
            
            st.subheader("⚡ Pro Tips")
            st.markdown("""
            - **Test incrementally**: Make small changes and save
            - **Use preview**: Always check before generating PDF
            - **Keep clean**: Maintain proper markdown syntax
            - **Save frequently**: Changes only persist when saved
            - **Backup**: Copy content before major edits
            """)
        
        with col2:
            st.subheader("🔧 Common Edits")
            st.markdown("""
            **Make text bold:**
            ```markdown
            **your text here**
            ```
            
            **Change heading size:**
            ```markdown
            # Largest
            ## Large  
            ### Medium
            #### Small
            ```
            
            **Convert to list:**
            ```markdown
            - Bullet item
            1. Numbered item
            ```
            
            **Add spacing:**
            ```markdown
            Insert blank lines
            
            between paragraphs
            ```
            
            **Fix formatting:**
            - Check for missing symbols
            - Balance opening/closing marks
            - Verify proper spacing
            """)
    
    with tab5:
        st.header("⚠️ API Rate Limits")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📊 Free Tier Limits")
            st.markdown("""
            - **50 requests per day** on free Google Gemini API
            - **Resets**: Every 24 hours automatically
            - **Monitor**: [AI Studio Usage Dashboard](https://aistudio.google.com/app/apikey)
            - **Tracking**: Check your usage anytime
            """)
            
            st.subheader("🔄 When Quota Exceeded")
            st.success("""
            **✅ Fallback Mode (Automatic)**
            
            The app automatically switches to rule-based processing:
            - Basic formatting still works
            - No API calls needed
            - Unlimited processing
            - All features remain functional
            """)
        
        with col2:
            st.subheader("📝 What Still Works in Fallback")
            st.markdown("""
            ✅ **Full Functionality:**
            - Note processing and organization
            - Markdown generation (rule-based)
            - Text editor with full control
            - PDF generation and preview
            - Multi-topic support
            - Download capabilities
            
            ⚡ **Performance:**
            - Actually faster (no API wait time)
            - No rate limiting
            - Completely offline-capable
            """)
            
            st.subheader("🎯 Your Options")
            st.markdown("""
            1. **Wait** - Free, quota resets in 24 hours
            2. **Use Fallback** - Free, works immediately
            3. **Upgrade API** - Paid plans with higher limits
            4. **Manual Edit** - Free, use text editor for refinements
            
            📚 [Rate Limit Documentation](https://ai.google.dev/gemini-api/docs/rate-limits)
            """)
    
    with tab6:
        st.header("💡 Best Practices")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Content Formatting Tips")
            st.markdown("""
            **For Best AI Detection:**
            - Use **colons (`:`)** after headings
            - Use **dashes (`-`)** for bullet points
            - Number lists: `1.`, `2.`, `3.`
            - **CAPITALIZE** important terms
            - Add **blank lines** between sections
            
            **Example:**
            ```
            Introduction:
            This is the main content.
            
            Key Points:
            - First point
            - Second point
            ```
            """)
            
            st.subheader("📄 Paragraph Content")
            st.markdown("""
            - Keep **natural paragraph flow**
            - Don't force list format
            - Let AI detect structure
            - Edit manually if AI misinterprets
            - Preserve narrative text as-is
            """)
        
        with col2:
            st.subheader("🎨 Mixed Content Strategy")
            st.markdown("""
            - **Paragraphs**: For explanations and narratives
            - **Lists**: For key points and summaries
            - **Headings**: For section organization
            - **Blank lines**: For visual spacing
            - **Bold**: For emphasis on keywords
            """)
            
            st.subheader("🔧 Using Custom Prompts")
            st.markdown("""
            **When to use:**
            - Need specific modifications
            - Want different tone
            - Require special formatting
            
            **How to use:**
            - Be specific and clear
            - One request at a time
            - Examples: 
              - *"Make it more concise"*
              - *"Add more structure"*
              - *"Emphasize key terms"*
            
            **Tip**: Only use when default processing isn't sufficient
            """)
            
            st.subheader("📚 Multiple Topics Workflow")
            st.markdown("""
            1. Process one topic at a time
            2. Review output before continuing
            3. Edit if needed using text editor
            4. Generate PDF to add to document
            5. Repeat for additional topics
            6. Build complete comprehensive document
            """)
    
    with tab7:
        st.header("🔧 Troubleshooting")
        
        # Problem 1
        st.subheader("❌ Problem: API key not working")
        st.markdown("""
        **Solution:** Check `.streamlit/secrets.toml` configuration
        
        - Verify key is correct and active
        - No extra spaces or quotes
        - File in correct location: `.streamlit/secrets.toml`
        - Format: `GEMINI_API_KEY = "your-key-here"`
        
        📝 For Streamlit Cloud: Add in App Settings > Secrets
        """)
        
        st.markdown("---")
        
        # Problem 2
        st.subheader("⚠️ Problem: Rate limit error (429)")
        st.markdown("""
        **Solution:** App automatically uses fallback mode
        
        - Continues processing automatically
        - Still generates quality output
        - Edit manually for refinements
        - Wait 24 hours for quota reset
        - Consider upgrading API plan
        """)
        
        st.markdown("---")
        
        # Problem 3
        st.subheader("📄 Problem: PDF not generating")
        st.markdown("""
        **Solution:** Check markdown for errors
        
        1. Look for syntax errors in markdown
        2. Fix any malformed formatting
        3. Use text editor to correct issues
        4. Ensure headings are properly formatted
        5. Remove any problematic characters
        6. Try regenerating PDF
        """)
        
        st.markdown("---")
        
        # Problem 4
        st.subheader("🎨 Problem: Formatting wrong or unexpected")
        st.markdown("""
        **Solution:** Use text editor for manual corrections
        
        1. Click "Open Text Editor"
        2. Make manual corrections
        3. Check markdown syntax guide (tab 3)
        4. Fix formatting issues
        5. Save changes
        6. Regenerate PDF
        
        **Common fixes:**
        - Add/remove `#` for heading sizes
        - Add `**` around text for bold
        - Add `-` before items for lists
        - Add blank lines for spacing
        """)
        
        st.markdown("---")
        
        # Problem 5
        st.subheader("💾 Problem: Lost progress or changes")
        st.markdown("""
        **Solution:** Follow these practices
        
        ⚠️ **Important:**
        - Don't refresh the page
        - Use "Add Topic" button for multi-topic docs
        - Download PDFs immediately after generation
        - No auto-save feature (by design)
        - Session clears on page refresh
        
        💡 **Best practice:**
        - Complete one topic at a time
        - Generate and download PDF for each section
        - Keep local backups of important content
        """)
    
    with tab8:
        st.header("📚 Examples")
        
        st.markdown("""
        Here are some example inputs to help you understand the best way to format your notes.
        """)
        
        # Example 1
        st.subheader("📌 Example 1: Simple Notes with Lists")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Input:**")
            st.code("""
Introduction:
This is the main topic explanation 
covering the basics.

Key Points:
- First important point
- Second important point
- Third important point
            """, language="text")
        
        with col2:
            st.markdown("**Output:**")
            st.markdown("""
**Introduction:**
This is the main topic explanation covering the basics.

**Key Points:**
- First important point
- Second important point
- Third important point
            """)
        
        st.markdown("---")
        
        # Example 2
        st.subheader("📌 Example 2: Detailed Content with Structure")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Input:**")
            st.code("""
Cell Biology:

Cells are the basic units of life. 
They contain genetic material and 
organelles that perform various 
functions.

Cell Types:
1. Prokaryotic cells
2. Eukaryotic cells

These cells have distinct structures 
and functions including energy 
production and protein synthesis.
            """, language="text")
        
        with col2:
            st.markdown("**Output:**")
            st.markdown("""
## Cell Biology

Cells are the basic units of life. They contain genetic material and organelles that perform various functions.

### Cell Types:
1. Prokaryotic cells
2. Eukaryotic cells

These cells have distinct structures and functions including energy production and protein synthesis.
            """)
        
        st.markdown("---")
        
        # Example 3
        st.subheader("📌 Example 3: Mixed Format with Keywords")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Input:**")
            st.code("""
Chapter Summary:

This chapter covered multiple 
concepts in depth. The main themes 
included cellular structure and 
function.

Important Terms:
- MITOCHONDRIA - Energy production
- NUCLEUS - Genetic control center
- RIBOSOMES - Protein synthesis

Understanding these concepts is 
essential for advanced biology 
studies.
            """, language="text")
        
        with col2:
            st.markdown("**Output:**")
            st.markdown("""
## Chapter Summary

This chapter covered multiple concepts in depth. The main themes included cellular structure and function.

### Important Terms:
- **MITOCHONDRIA** - Energy production
- **NUCLEUS** - Genetic control center
- **RIBOSOMES** - Protein synthesis

Understanding these concepts is essential for advanced biology studies.
            """)
        
        st.markdown("---")
        st.success("""
        💡 **Key Takeaways from Examples:**
        - Headings with colons are detected automatically
        - Lists (bullets and numbered) are preserved
        - CAPITALIZED terms are bolded
        - Paragraph structure is maintained
        - Natural flow is kept intact
        """)


if __name__ == "__main__":
    main()
