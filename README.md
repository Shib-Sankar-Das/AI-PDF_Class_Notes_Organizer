# 📚 Class Note Organizer

A powerful Streamlit application that uses LangGraph with Google's Gemini API 2.5 Pro to organize, format, and export class notes into professional PDFs.

## ✨ Features

- 🤖 **AI-Powered Organization**: Uses Gemini API 2.5 Pro with LangGraph for intelligent note processing
- 📝 **Markdown Conversion**: Automatically converts notes to well-formatted markdown
- ✏️ **Built-in Text Editor**: Edit generated content with full markdown support
- 📄 **PDF Generation**: Export notes to professional PDFs with proper formatting
- 👁️ **Live PDF Preview**: View generated PDFs directly in the browser
- ➕ **Multi-Topic Support**: Add multiple topics to a single PDF document
- 🛡️ **Fallback Mode**: Automatic rule-based formatting when API limits are reached
- 🎨 **Smart Formatting**: 
  - Automatic heading detection (using colons and dashes)
  - Bold important keywords
  - Bullet points and numbering
  - Proper spacing and font sizing
  - Hierarchical structure

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

1. **Enter PDF Title**: The main title for your document (appears on first page)
2. **Enter Topic Title**: Title for the current section/topic
3. **Paste Content**: Add your class notes in the text area
4. **(Optional)** Custom Modifications: Add specific instructions in the prompt box if you want to modify the content
5. **Generate Markdown**: Click to process and format your notes
6. **Edit (Optional)**: Use the text editor to manually adjust the output
7. **Generate PDF**: Create the PDF with your formatted notes
8. **Add More Topics**: Click "Add Another Topic" to append more content to the same PDF
9. **Download**: Download the final PDF document

## 🎯 AI Processing Rules

The Gemini AI follows strict guidelines:

- ✅ Identifies and bolds important keywords
- ✅ Detects headings (marked by colons `:` or dashes `-`)
- ✅ Organizes content with bullets and numbering
- ✅ Manages proper spacing and font hierarchy
- ✅ Preserves original content exactly
- ❌ Does NOT add extra information or points
- ❌ Does NOT modify headings or content (unless custom prompt provided)

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
- **Free Tier**: 50 requests/day limit
- **Solution 1**: Wait 24 hours for quota reset
- **Solution 2**: Use automatic fallback mode (still works!)
- **Solution 3**: Upgrade to paid API plan
- **Monitor Usage**: https://ai.dev/usage?tab=rate-limit

See `RATE_LIMIT_GUIDE.md` for detailed solutions.

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
