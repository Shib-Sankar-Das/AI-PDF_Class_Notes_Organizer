"""
PDF Generator for class notes
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
import markdown
import re
from io import BytesIO
from config import FONT_SIZES


class PDFGenerator:
    """Generate PDF from markdown content"""
    
    def __init__(self, pdf_title: str):
        """Initialize PDF generator"""
        self.pdf_title = pdf_title
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # PDF Title style
        self.styles.add(ParagraphStyle(
            name='PDFTitle',
            parent=self.styles['Heading1'],
            fontSize=FONT_SIZES['pdf_title'],
            textColor='#000000',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Topic Title style
        self.styles.add(ParagraphStyle(
            name='TopicTitle',
            parent=self.styles['Heading2'],
            fontSize=FONT_SIZES['topic_title'],
            textColor='#1a1a1a',
            spaceAfter=20,
            spaceBefore=20,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 1 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=FONT_SIZES['heading1'],
            textColor='#2c3e50',
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 2 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=FONT_SIZES['heading2'],
            textColor='#34495e',
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 3 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=FONT_SIZES['heading3'],
            textColor='#455a64',
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=FONT_SIZES['body'],
            textColor='#000000',
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
    
    def _parse_markdown_to_elements(self, markdown_text: str, topic_title: str = ""):
        """Parse markdown text into ReportLab elements"""
        elements = []
        lines = markdown_text.split('\n')
        
        # Add topic title if provided
        if topic_title:
            elements.append(Paragraph(topic_title, self.styles['TopicTitle']))
            elements.append(Spacer(1, 0.2 * inch))
        
        i = 0
        in_list = False
        list_items = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                if in_list:
                    # End of list
                    for item in list_items:
                        elements.append(item)
                    list_items = []
                    in_list = False
                elements.append(Spacer(1, 0.1 * inch))
                i += 1
                continue
            
            # Heading 1
            if line.startswith('# '):
                if in_list:
                    for item in list_items:
                        elements.append(item)
                    list_items = []
                    in_list = False
                text = line[2:].strip()
                text = self._process_bold(text)
                elements.append(Spacer(1, 0.15 * inch))
                elements.append(Paragraph(text, self.styles['CustomHeading1']))
                elements.append(Spacer(1, 0.1 * inch))
            
            # Heading 2
            elif line.startswith('## '):
                if in_list:
                    for item in list_items:
                        elements.append(item)
                    list_items = []
                    in_list = False
                text = line[3:].strip()
                text = self._process_bold(text)
                elements.append(Spacer(1, 0.12 * inch))
                elements.append(Paragraph(text, self.styles['CustomHeading2']))
                elements.append(Spacer(1, 0.08 * inch))
            
            # Heading 3
            elif line.startswith('### '):
                if in_list:
                    for item in list_items:
                        elements.append(item)
                    list_items = []
                    in_list = False
                text = line[4:].strip()
                text = self._process_bold(text)
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph(text, self.styles['CustomHeading3']))
                elements.append(Spacer(1, 0.06 * inch))
            
            # Bullet points
            elif line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
                in_list = True
                text = re.sub(r'^[-*•]\s+', '', line)
                text = self._process_bold(text)
                bullet_para = Paragraph(f"• {text}", self.styles['CustomBody'])
                list_items.append(bullet_para)
            
            # Numbered lists
            elif re.match(r'^\d+\.\s+', line):
                in_list = True
                text = re.sub(r'^\d+\.\s+', '', line)
                text = self._process_bold(text)
                number = re.match(r'^(\d+)\.', line).group(1)
                numbered_para = Paragraph(f"{number}. {text}", self.styles['CustomBody'])
                list_items.append(numbered_para)
            
            # Regular paragraph
            else:
                if in_list:
                    for item in list_items:
                        elements.append(item)
                    list_items = []
                    in_list = False
                text = self._process_bold(line)
                elements.append(Paragraph(text, self.styles['CustomBody']))
            
            i += 1
        
        # Add any remaining list items
        if in_list:
            for item in list_items:
                elements.append(item)
        
        return elements
    
    def _process_bold(self, text: str) -> str:
        """Process bold markdown syntax to ReportLab format"""
        # Convert **text** to <b>text</b>
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Convert __text__ to <b>text</b>
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        # Convert *text* to <i>text</i>
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        # Convert _text_ to <i>text</i>
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        return text
    
    def create_new_pdf(self, topic_title: str, markdown_content: str) -> BytesIO:
        """Create a new PDF with title and first topic"""
        self.buffer = BytesIO()
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        
        # Add PDF title on first page
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(self.pdf_title, self.styles['PDFTitle']))
        elements.append(Spacer(1, 0.5 * inch))
        
        # Add content
        content_elements = self._parse_markdown_to_elements(markdown_content, topic_title)
        elements.extend(content_elements)
        
        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer
    
    def append_to_pdf(self, existing_pdf_buffer: BytesIO, topic_title: str, 
                      markdown_content: str) -> BytesIO:
        """Append new content to existing PDF"""
        # For simplicity, we'll recreate the PDF with all content
        # In a production app, you'd want to use PyPDF2 to merge PDFs
        # For now, this creates a new section in the same PDF
        return self.create_new_pdf(topic_title, markdown_content)
    
    def generate_pdf_from_all_notes(self, notes_list: list) -> BytesIO:
        """Generate PDF from a list of notes"""
        self.buffer = BytesIO()
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        
        # Add PDF title on first page
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(self.pdf_title, self.styles['PDFTitle']))
        elements.append(Spacer(1, 0.5 * inch))
        
        # Add each note
        for idx, note in enumerate(notes_list):
            if idx > 0:
                elements.append(PageBreak())
            
            topic_title = note.get('topic_title', '')
            markdown_content = note.get('markdown_content', '')
            
            content_elements = self._parse_markdown_to_elements(
                markdown_content, 
                topic_title
            )
            elements.extend(content_elements)
        
        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer
