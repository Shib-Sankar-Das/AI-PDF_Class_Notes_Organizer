# 📚 Class Note Organizer

A powerful Streamlit application that uses LangGraph with Google's Gemini API to intelligently organize, format, and export class notes into professional PDFs.

## ✨ Features

### Core Functionality
- 🤖 **AI-Powered Organization**: Uses Gemini 2.5 Pro with LangGraph for intelligent note processing
- 📝 **Markdown Conversion**: Automatically converts notes to well-formatted markdown
- ✏️ **Built-in Text Editor**: Edit generated content with full markdown support
- 📄 **PDF Generation**: Export notes to professional PDFs with proper formatting
- 👁️ **Live PDF Preview**: View generated PDFs directly in the browser using `streamlit-pdf-viewer` (works on Streamlit Cloud!)
- ➕ **Multi-Topic Support**: Add multiple topics to a single PDF document

### Smart Features
- 🛡️ **Fallback Mode**: Automatic rule-based formatting when API limits are reached (no API calls needed!)
- 🔄 **Model Fallback Chain**: Tries multiple Gemini models automatically (2.5-pro → 2.0-flash-exp → 1.5-pro-latest → etc.)
- 📖 **Help Interface**: Comprehensive tabbed help guide with examples and troubleshooting
- 🎨 **Paragraph Preservation**: Keeps paragraphs as paragraphs - never converts them to lists unless they already are

### Smart Formatting
- Automatic heading detection (using colons `:` and dashes `-`)
- Bold important keywords (especially CAPITALIZED terms)
- Preserves bullet points and numbered lists
- Proper spacing and font sizing
- Hierarchical structure (Title → H1 → H2 → H3 → Body)
- Natural text flow preservation

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd "New folder"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:

Create or edit `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-actual-gemini-api-key-here"
```

### Running Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🌐 Deploying to Streamlit Cloud

1. **Push to GitHub**:
   - Create a new GitHub repository
   - Push your code to the repository

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Choose `app.py` as the main file
   - Click "Deploy"

3. **Add Secrets**:
   - In your Streamlit Cloud dashboard, go to App Settings
   - Navigate to "Secrets"
   - Add your secrets:
   ```toml
   GEMINI_API_KEY = "your-actual-gemini-api-key-here"
   ```

4. **Save and Restart**: Your app will automatically redeploy with the secrets

## 📖 How to Use

### Quick Start
1. **Enter PDF Title**: The main title for your document (appears on first page with largest font)
2. **Enter Topic Title**: Title for the current section/topic
3. **Paste Content**: Add your class notes in the text area
4. **(Optional)** Custom Modifications: Add specific instructions if you want to modify the content
5. **Generate Markdown**: Click to process and format your notes
6. **Edit (Optional)**: Use the text editor to manually adjust the output
7. **Generate PDF**: Create the PDF with your formatted notes
8. **Add More Topics**: Click "Add Another Topic" to append more content to the same PDF
9. **Download**: Download the final PDF document

### Interface Modes

The app has two interface modes accessible via sidebar dropdown:

#### 📝 Create Notes (Main Interface)
- Two-column layout: Input section (left) + PDF viewer (right)
- Full note creation and PDF generation workflow
- Document statistics when topics are added

#### 📖 Help & Guidelines (Help Interface)
- Full-screen tabbed help interface with 8 comprehensive sections:
  - **How to Use**: Step-by-step workflow guide
  - **AI Capabilities**: What AI does and doesn't do
  - **Markdown Syntax**: Complete formatting reference
  - **Text Editor**: Editor usage and tips
  - **Rate Limits**: Understanding and handling API quotas
  - **Best Practices**: Optimization strategies
  - **Troubleshooting**: Common problems and solutions
  - **Examples**: Real-world usage scenarios with input/output

### Content Formatting Tips

For best results, format your notes like this:

```text
Introduction:
This is the main topic content here.

Key Concepts:
- First important point
- Second important point
- Third important point

Details:
1. First numbered item
2. Second numbered item

Important Terms:
MACHINE LEARNING - automated learning
NEURAL NETWORKS - brain-inspired computing
```

**Best Practices:**
- Use colons (`:`) or dashes (`-`) after headings
- CAPITALIZE important keywords for auto-bolding
- Use `-` or `*` for bullet points
- Use `1.`, `2.`, etc. for numbered lists
- Add blank lines between sections
- Keep paragraphs as paragraphs (AI won't convert them to lists)

## 🎯 AI Processing Rules

The Gemini AI follows strict guidelines to ensure quality output:

### What AI Does:
- ✅ Identifies and bolds important keywords (especially CAPITALIZED terms)
- ✅ Detects headings (marked by colons `:` or dashes `-`)
- ✅ Preserves existing bullet points and numbered lists
- ✅ Manages proper spacing and font hierarchy
- ✅ Maintains paragraph structure naturally
- ✅ Organizes content logically

### What AI Does NOT Do:
- ❌ Add extra information or points not in original
- ❌ Modify the meaning of your content
- ❌ Convert paragraphs into lists (unless they already are lists)
- ❌ Change headings or create fake structure
- ❌ Hallucinate or invent content

### Special Feature: Paragraph Preservation
The AI is specifically trained to **preserve paragraph structure**. If your content consists only of paragraphs with no lists, it will stay that way. Lists are only created where they already exist in your input.

**Example:**
- Input: "This is a paragraph. Another sentence here."
- Output: Stays as a paragraph (bolded keywords only)
- NOT converted to: "- This is a paragraph\n- Another sentence here"

This ensures natural text flow and readability.

## 📂 Project Structure

```
New folder/
├── .streamlit/
│   └── secrets.toml          # API keys and secrets
├── app.py                    # Main Streamlit application
├── langgraph_agent.py        # LangGraph agent for note processing
├── pdf_generator.py          # PDF generation functionality
├── config.py                 # Configuration and constants
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔧 Configuration

### Font Sizes (in `config.py`)

```python
FONT_SIZES = {
    'pdf_title': 24,      # Main PDF title
    'topic_title': 18,    # Topic titles
    'heading1': 16,       # Main headings
    'heading2': 14,       # Subheadings
    'heading3': 12,       # Sub-subheadings
    'body': 10,           # Body text
}
```

## 🛠️ Technologies Used

- **Streamlit**: Web application framework
- **LangGraph**: Workflow orchestration for AI agents
- **Google Gemini API 2.5 Pro**: Advanced language model
- **LangChain**: LLM integration framework
- **ReportLab**: PDF generation
- **Python-Markdown**: Markdown processing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### API Key Issues
- Ensure your Gemini API key is correctly added to `secrets.toml`
- For Streamlit Cloud, verify the secrets are added in App Settings

### Rate Limit Errors (429)

When you exceed the free tier limit (50 requests/day), the app automatically switches to **fallback mode**:

#### What Still Works in Fallback Mode:
- ✅ Heading detection (lines ending with `:` or `-`)
- ✅ Bullet point and numbered list identification  
- ✅ Keyword bolding (CAPITALIZED words)
- ✅ Basic structure organization
- ✅ Markdown conversion
- ✅ PDF generation
- ✅ Text editor
- ✅ All features remain functional!

#### Your Options:
1. **Wait 24 hours** - Free tier resets daily
2. **Use fallback mode** - Continues working automatically, just format your notes well
3. **Upgrade API plan** - Get higher limits (paid)
4. **Manual editing** - Use the built-in text editor for refinements

#### Monitoring Usage:
- Check usage at: [Google AI Studio Usage Dashboard](https://aistudio.google.com/app/apikey)
- Free tier: 50 requests/day
- Each "Generate" uses ~3 API calls (analyze + modify + format)
- Approximately 16 notes per day on free tier

**Pro Tip**: Format your input well (use CAPS for keywords, `:` for headings) for better fallback results!

See the built-in Help & Guidelines interface for detailed rate limit documentation.

### PDF Generation Issues
- Check that all required packages are installed
- Ensure proper markdown formatting in the content

### LangGraph Errors
- Verify you have the correct version of langgraph installed
- Check your internet connection for API calls

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ❤️ using Streamlit and Google Gemini API
