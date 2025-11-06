"""
LangGraph Agent for processing notes with Gemini API
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import google.generativeai as genai
import re
import time


class NoteState(TypedDict):
    """State for the note processing workflow"""
    content: str
    user_prompt: str
    processed_content: str
    markdown_output: str
    error: str
    rate_limited: bool
    fallback_used: bool


class NoteOrganizerAgent:
    """LangGraph agent for organizing class notes"""
    
    def __init__(self, api_key: str):
        """Initialize the agent with Gemini API"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Try different model names in order of preference
        model_names = [
            "gemini-2.5-pro",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro-latest",
            "gemini-1.5-pro",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-pro"
        ]
        
        self.model = None
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"Successfully initialized model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to load {model_name}: {e}")
                continue
        
        if not self.model:
            raise Exception("Could not initialize any Gemini model")
        
        self.workflow = self._create_workflow()
        self.max_retries = 2
        self.retry_delay = 2  # seconds
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(NoteState)
        
        # Add nodes
        workflow.add_node("analyze_content", self._analyze_content)
        workflow.add_node("apply_user_modifications", self._apply_user_modifications)
        workflow.add_node("format_markdown", self._format_markdown)
        
        # Add edges
        workflow.set_entry_point("analyze_content")
        workflow.add_edge("analyze_content", "apply_user_modifications")
        workflow.add_edge("apply_user_modifications", "format_markdown")
        workflow.add_edge("format_markdown", END)
        
        return workflow.compile()
    
    def _call_api_with_retry(self, prompt: str, operation_name: str) -> tuple[str, str]:
        """Call Gemini API with retry logic and error handling"""
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={'temperature': 0.3}
                )
                return response.text, ""
            except Exception as e:
                error_str = str(e)
                
                # Check for rate limit errors
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    return "", f"⚠️ API Rate Limit: You've reached the free tier limit (50 requests/day). Please wait or upgrade your API plan. Using fallback formatting."
                
                # Check for other quota errors
                if "exceeded" in error_str.lower():
                    return "", f"⚠️ API Quota Exceeded: {error_str}. Using fallback formatting."
                
                # Retry on other errors
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return "", f"Error in {operation_name}: {error_str}"
        
        return "", f"Failed after {self.max_retries} attempts"
    
    def _analyze_content(self, state: NoteState) -> NoteState:
        """Analyze content and identify structure"""
        content = state["content"]
        
        # Check if already rate limited
        if state.get("rate_limited", False):
            state["processed_content"] = content
            return state
        
        prompt = f"""
You are an expert note organizer. Analyze the following content and identify its natural structure.

Content:
{content}

CRITICAL RULES:
1. DO NOT add any new information, points, or extra content
2. DO NOT modify the original content or headings
3. DO NOT convert paragraphs into bullet points unless they already are bullet points
4. ONLY identify and mark the structure that already exists in the content
5. Preserve the exact wording and format from the original text

What to identify:
- Important keywords that should be bolded (use sparingly, only truly important terms)
- Main headings (usually followed by colons : or dashes -)
- Subheadings and their hierarchy
- Bullet points (ONLY if they already exist in the content as -, •, or * lists)
- Numbered lists (ONLY if they already exist in the content as 1., 2., etc.)
- Regular paragraphs (preserve as paragraphs, do NOT convert to lists)

SPECIAL CASE - PARAGRAPH-ONLY CONTENT:
If the content consists only of paragraphs with NO bullet points or numbered lists, keep them as paragraphs.
Do NOT create lists where none exist. Preserve the natural flow of paragraph text.

Provide the analysis in a structured format marking:
- [KEYWORD: text] for important keywords (use sparingly)
- [HEADING1: text] for main headings
- [HEADING2: text] for subheadings  
- [HEADING3: text] for sub-subheadings
- [BULLET: text] ONLY for existing bullet points
- [NUMBER: text] ONLY for existing numbered points
- [PARA: text] for all regular paragraph text (preserve as-is)
"""
        
        result, error = self._call_api_with_retry(prompt, "analyze_content")
        
        if error:
            state["error"] = error
            if "Rate Limit" in error or "Quota" in error:
                state["rate_limited"] = True
                # Use fallback: basic processing
                state["processed_content"] = self._fallback_analyze(content)
                state["fallback_used"] = True
            else:
                state["processed_content"] = content
        else:
            state["processed_content"] = result
        
        return state
    
    def _fallback_analyze(self, content: str) -> str:
        """Fallback content analysis without API"""
        lines = content.split('\n')
        processed = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headings (lines ending with : or -)
            if line.endswith(':') or line.endswith('-'):
                processed.append(f"[HEADING1: {line}]")
            # Detect bullet points
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                processed.append(f"[BULLET: {line.lstrip('-•* ')}]")
            # Detect numbered lists
            elif re.match(r'^\d+\.', line):
                processed.append(f"[NUMBER: {re.sub(r'^\d+\.\s*', '', line)}]")
            # Regular paragraphs
            else:
                # Try to identify important words (capitalized, technical terms)
                words = line.split()
                formatted_words = []
                for word in words:
                    # Bold words that are all caps or start with capital
                    if word.isupper() and len(word) > 2:
                        formatted_words.append(f"[KEYWORD: {word}]")
                    else:
                        formatted_words.append(word)
                processed.append(f"[PARA: {' '.join(formatted_words)}]")
        
        return '\n'.join(processed)
    
    def _apply_user_modifications(self, state: NoteState) -> NoteState:
        """Apply user-specified modifications if provided"""
        processed_content = state["processed_content"]
        user_prompt = state.get("user_prompt", "")
        
        # Skip API call if rate limited or no user prompt
        if state.get("rate_limited", False) or not (user_prompt and user_prompt.strip()):
            return state
        
        modification_prompt = f"""
The user wants to modify their notes with the following instructions:
{user_prompt}

Original processed content:
{processed_content}

Apply ONLY the user's requested modifications. Do not make any other changes.
Maintain the structured format with markers like [HEADING1:], [KEYWORD:], etc.
"""
        
        result, error = self._call_api_with_retry(modification_prompt, "apply_modifications")
        
        if error:
            if "Rate Limit" in error or "Quota" in error:
                state["rate_limited"] = True
                state["error"] = error
            # Keep original processed content if modification fails
        else:
            state["processed_content"] = result
        
        return state
    
    def _fallback_format_markdown(self, processed_content: str) -> str:
        """Fallback markdown formatting without API"""
        lines = processed_content.split('\n')
        markdown = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Convert markers to markdown
            if line.startswith('[HEADING1:'):
                text = re.sub(r'\[HEADING1:\s*(.+?)\]', r'\1', line)
                markdown.append(f"\n# {text}\n")
            elif line.startswith('[HEADING2:'):
                text = re.sub(r'\[HEADING2:\s*(.+?)\]', r'\1', line)
                markdown.append(f"\n## {text}\n")
            elif line.startswith('[HEADING3:'):
                text = re.sub(r'\[HEADING3:\s*(.+?)\]', r'\1', line)
                markdown.append(f"\n### {text}\n")
            elif line.startswith('[BULLET:'):
                text = re.sub(r'\[BULLET:\s*(.+?)\]', r'\1', line)
                markdown.append(f"- {text}")
            elif line.startswith('[NUMBER:'):
                text = re.sub(r'\[NUMBER:\s*(.+?)\]', r'\1', line)
                markdown.append(f"1. {text}")
            elif line.startswith('[PARA:'):
                text = re.sub(r'\[PARA:\s*(.+?)\]', r'\1', line)
                # Convert [KEYWORD: text] to **text**
                text = re.sub(r'\[KEYWORD:\s*(.+?)\]', r'**\1**', text)
                markdown.append(f"{text}\n")
            else:
                # Convert any remaining keywords
                text = re.sub(r'\[KEYWORD:\s*(.+?)\]', r'**\1**', line)
                markdown.append(text)
        
        return '\n'.join(markdown)
    
    def _format_markdown(self, state: NoteState) -> NoteState:
        """Convert structured content to markdown"""
        processed_content = state["processed_content"]
        
        # Use fallback if rate limited
        if state.get("rate_limited", False):
            state["markdown_output"] = self._fallback_format_markdown(processed_content)
            return state
        
        markdown_prompt = f"""
Convert the following structured content into clean, well-formatted Markdown.

CRITICAL: Preserve the original structure. Do NOT convert paragraphs into lists.

Conversion Rules:
1. [HEADING1: text] → # text (with blank line above and below)
2. [HEADING2: text] → ## text (with blank line above and below)
3. [HEADING3: text] → ### text (with blank line above and below)
4. [KEYWORD: text] → **text** (bold the keyword)
5. [BULLET: text] → - text (bullet point) - ONLY if marked as BULLET
6. [NUMBER: text] → 1. text (numbered list) - ONLY if marked as NUMBER
7. [PARA: text] → text (regular paragraph with proper spacing) - Keep as paragraph

IMPORTANT:
- If you see only [PARA:] markers with no [BULLET:] or [NUMBER:] markers, output ONLY paragraphs
- Do NOT create bullet points or numbered lists where none are marked
- Preserve paragraph flow and readability
- Add blank lines between paragraphs for better readability

Structured content:
{processed_content}

Provide ONLY the markdown output without any explanations, code blocks, or additional text.
Ensure proper spacing between sections and headings while preserving the paragraph structure.
"""
        
        result, error = self._call_api_with_retry(markdown_prompt, "format_markdown")
        
        if error:
            state["error"] = error
            if "Rate Limit" in error or "Quota" in error:
                state["rate_limited"] = True
                state["fallback_used"] = True
            # Use fallback formatting
            state["markdown_output"] = self._fallback_format_markdown(processed_content)
        else:
            markdown_output = result.strip()
            
            # Clean up any markdown code blocks if present
            if markdown_output.startswith("```markdown"):
                markdown_output = markdown_output.replace("```markdown", "").replace("```", "").strip()
            elif markdown_output.startswith("```"):
                markdown_output = markdown_output.replace("```", "").strip()
            
            state["markdown_output"] = markdown_output
        
        return state
    
    def process_notes(self, content: str, user_prompt: str = "") -> dict:
        """Process notes through the LangGraph workflow"""
        initial_state = {
            "content": content,
            "user_prompt": user_prompt,
            "processed_content": "",
            "markdown_output": "",
            "error": "",
            "rate_limited": False,
            "fallback_used": False
        }
        
        result = self.workflow.invoke(initial_state)
        return result
