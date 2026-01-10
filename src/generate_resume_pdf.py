#!/usr/bin/env python3
"""
Resume PDF Generator
Converts YAML resume data to a beautifully formatted PDF
"""

import yaml
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import sys
import os

# pdfmetrics.registerFont(TTFont('Raleway-Light', 'src/fonts/Raleway/Raleway-Light.ttf'))
# pdfmetrics.registerFont(TTFont('Raleway-LightItalic', 'src/fonts/Raleway/Raleway-LightItalic.ttf'))
# pdfmetrics.registerFont(TTFont('Raleway-Medium', 'src/fonts/Raleway/Raleway-Medium.ttf'))
pdfmetrics.registerFont(TTFont('Raleway-Regular', 'src/fonts/Raleway/Raleway-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Raleway-Italic', 'src/fonts/Raleway/Raleway-Italic.ttf'))
pdfmetrics.registerFont(TTFont('Raleway-SemiBold', 'src/fonts/Raleway/Raleway-SemiBold.ttf'))

headingColor = colors.HexColor('#204E8C')
textColor = colors.black
secondaryTextColor = colors.HexColor('#4A5568')
defaultFont = 'Raleway-Regular'
boldFont = 'Raleway-SemiBold'
italicFont = 'Raleway-Italic'

class ResumeGenerator:
    """Generate a professional resume PDF from YAML data"""
    
    def __init__(self, yaml_file, resume_file="resume.pdf", bio_file="bio.pdf"):
        self.yaml_file = yaml_file
        self.resume_file = resume_file
        self.bio_file = bio_file
        self.data = self._load_yaml()
        self.styles = self._setup_styles()
        self.story = []
        
    def _load_yaml(self):
        """Load and parse YAML resume data"""
        with open(self.yaml_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_styles(self):
        """Create custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Biography style
        styles.add(ParagraphStyle(
            name='ResumeNormal',
            parent=styles['Normal'],
            fontSize=9,
            fontName=defaultFont,
            textColor=textColor,
            spaceAfter=6
        ))

        # Name style - large and bold
        styles.add(ParagraphStyle(
            name='Name',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=headingColor,
            spaceAfter=12,
            fontName=defaultFont
        ))
        
        # Contact info style
        styles.add(ParagraphStyle(
            name='Contact',
            parent=styles['ResumeNormal'],
            textColor=headingColor,
            spaceAfter=9,
        ))
        
        # Summary style
        styles.add(ParagraphStyle(
            name='Summary',
            parent=styles['Normal'],
            fontSize=10,
            textColor=headingColor, 
            spaceAfter=0,
            leading=14,
            rightIndent=100,
            fontName=italicFont
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=10,
            textColor=headingColor,
            spaceAfter=4,
            spaceBefore=8,
            fontName=defaultFont
        ))
        
        # Job title style
        styles.add(ParagraphStyle(
            name='JobTitle',
            parent=styles['ResumeNormal'],
            fontSize=10,
            spaceAfter=4,
            spaceBefore=7,
        ))
        
        # Summary line style
        styles.add(ParagraphStyle(
            name='RoleSummary',
            parent=styles['ResumeNormal'],
            textColor=secondaryTextColor,
            spaceAfter=5,
        ))
        
        # Bullet point style
        styles.add(ParagraphStyle(
            name='ResumeBullet',
            parent=styles['ResumeNormal'],
            leftIndent=14,
            firstLineIndent=-6,
            spaceAfter=4,
            leading=11,
        ))
        
        # Expertise label style
        styles.add(ParagraphStyle(
            name='Expertise',
            parent=styles['ResumeNormal'],
            spaceAfter=2,
        ))
        
        # Biography style
        styles.add(ParagraphStyle(
            name='Biography',
            parent=styles['ResumeNormal']
        ))
        
        return styles
    
    def _paragraph_with_larger_first_letter(self, text, style):
        """Format section header text with larger first letter of each word"""
        words = text.split()
        formatted_words = []
        for word in words:
            if len(word) > 0:
                # Make first letter larger (1.3x the base font size)
                first_letter = word[0].upper()
                rest = word[1:].upper() if len(word) > 1 else ''
                formatted_word = f'<font size="{style.fontSize * 1.3}">{first_letter}</font>{rest}'
                formatted_words.append(formatted_word)
        return Paragraph(' '.join(formatted_words), style)
    
    def _as_link(self, text, url):
        # Ensure URL has protocol
        return f'<link href="{url}" color="#204E8C">{text}</link>'

    def _convert_markdown_link(self, text):
        """Convert markdown link format [text](url) to ReportLab HTML link format"""
        # Pattern to match [text](url)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            # ReportLab uses <link> tag for hyperlinks
            return f'<link href="{link_url}" color="#204E8C">{link_text}</link>'
        
        return re.sub(pattern, replace_link, text)
    
    def _format_date(self, date_str):
        """Format date string to 'Month Year' format (e.g., 'May 2025')"""
        if not date_str or date_str.lower() == 'present':
            return date_str
        
        # Try to parse different date formats
        date_formats = ['%Y-%m-%d', '%Y-%m']
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(str(date_str), fmt)
                return date_obj.strftime('%B %Y')
            except ValueError:
                continue
        
        # If parsing fails, return original
        return date_str

    def _add_header(self):
        """Add name, contact info, and summary"""
        cv = self.data['cv']
        
        # Add profile picture if available
        if 'photo' in cv and os.path.exists(f'src/{cv['photo']}'):
            img = Image(f'src/{cv['photo']}', width=1.4*inch, height=1.4*inch)
            img.hAlign = 'RIGHT'
            self.story.append(img)
            self.story.append(Spacer(1, -1.5*inch))  # Move back up
        
        # Name
        name = self._paragraph_with_larger_first_letter(cv['name'], self.styles['Name'])
        self.story.append(name)
        
        # Contact info in one line
        contact_parts = []
        if 'email' in cv:
            contact_parts.append(self._as_link(cv['email'], f'mailto:{cv['email']}'))
        if 'phone' in cv:
            contact_parts.append(self._as_link(cv['phone'], f'tel:{cv['phone']}'))
        if 'website' in cv:
            contact_parts.append(self._as_link(cv['website'], f'https://{cv['website']}'))
        if 'social_networks' in cv:
            for social in cv['social_networks']:
                if social['network'] == 'LinkedIn':
                    link_url = f'https://linkedin.com/in/{social["username"]}'
                    contact_parts.append(self._as_link(social['network'], link_url))
        
        contact_text = "&nbsp;&nbsp;|&nbsp;&nbsp;".join(contact_parts)
        contact = Paragraph(contact_text, self.styles['Contact'])
        self.story.append(contact)
        
        # Summary
        if 'summary' in cv:
            summary = Paragraph(cv['summary'], self.styles['Summary'])
            self.story.append(summary)
        
        # Horizontal line
        self.story.append(Spacer(1, 0.04*inch))
    
    def _add_experience(self):
        """Add executive experience section"""
        cv = self.data['cv']
        sections = cv.get('sections', {})
        
        if 'executive_experience' not in sections:
            return
        
        # Section header
        header = self._paragraph_with_larger_first_letter("Executive Experience", self.styles['SectionHeader'])
        self.story.append(header)
        
        for job in sections['executive_experience']:
            # Keep each job together on same page
            job_elements = []
            
            # Job title and company
            title_text = f"<font name='Raleway-SemiBold'>{job['position']}</font> | "
            if 'company' in job:
                # Convert markdown links to working HTML links
                company_name = self._convert_markdown_link(job['company'])
                title_text += company_name
            
            # Add dates
            start_date = self._format_date(job.get('start_date', ''))
            end_date = self._format_date(job.get('end_date', ''))
            date_range = f"{start_date} – {end_date}"
            title_text += f" | {date_range}"
            
            title = Paragraph(title_text, self.styles['JobTitle'])
            job_elements.append(title)
            
            # Role summary
            if 'summary' in job:
                summary = Paragraph(job['summary'], self.styles['RoleSummary'])
                job_elements.append(summary)
            
            # Highlights as bullet points
            if 'highlights' in job:
                for highlight in job['highlights']:
                    bullet_text = f"• {highlight}"
                    bullet = Paragraph(bullet_text, self.styles['ResumeBullet'])
                    job_elements.append(bullet)
            
            # job_elements.append(Spacer(1, 0.06*inch))
            
            # Keep job together on same page
            self.story.append(KeepTogether(job_elements))
    
    def _add_expertise(self):
        """Add core expertise section"""
        cv = self.data['cv']
        sections = cv.get('sections', {})
        
        if 'core_expertise' not in sections:
            return
        
        # Section header
        header = self._paragraph_with_larger_first_letter("Core Expertise", self.styles['SectionHeader'])
        self.story.append(header)
        
        for item in sections['core_expertise']:
            label = Paragraph(f"<font name='Raleway-SemiBold'>{item['label']}: </font>{item['details']}", self.styles['Expertise'])
            self.story.append(label)

        self.story.append(Spacer(1, 0.05*inch))
    
    def _add_thought_leadership(self):
        """Add thought leadership section"""
        cv = self.data['cv']
        sections = cv.get('sections', {})
        
        if 'thought_leadership' not in sections:
            return
        
        # Section header
        header = self._paragraph_with_larger_first_letter("Thought Leadership", self.styles['SectionHeader'])
        self.story.append(header)
        
        for item in sections['thought_leadership']:
            # Convert markdown links to working HTML links
            details_text = self._convert_markdown_link(item['details'])
            
            text = f"<font name='Raleway-SemiBold'>{item['label']}: </font>{details_text}"
            para = Paragraph(text, self.styles['Expertise'])
            self.story.append(para)
        
        self.story.append(Spacer(1, 0.05*inch))
    
    def _add_education(self):
        """Add education section"""
        cv = self.data['cv']
        sections = cv.get('sections', {})
        
        if 'education' not in sections:
            return
        
        # Section header
        header = self._paragraph_with_larger_first_letter("Education", self.styles['SectionHeader'])
        self.story.append(header)
        
        for edu in sections['education']:
            # Convert markdown links to working HTML links
            institution = self._convert_markdown_link(edu['institution'])
            
            text = f"<font name='Raleway-SemiBold'>{edu['degree']}, {edu['area']}</font> - {institution}"
            para = Paragraph(text, self.styles['Expertise'])
            self.story.append(para)
    
    def _add_bio(self):
        """Add bio section"""
        cv = self.data['cv']
        sections = cv.get('sections', {})
        
        if 'executive_bio' not in sections:
            return
        
        # Section header
        header = self._paragraph_with_larger_first_letter("Executive Biography", self.styles['SectionHeader'])
        self.story.append(header)
        
        for executive_bio in sections['executive_bio']:
            para = Paragraph(executive_bio, self.styles['Biography'])
            self.story.append(para)
    
    def generate(self):
        """Generate the complete PDF resume"""
        # Create PDF document
        doc = SimpleDocTemplate(
            self.resume_file,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build story
        self._add_header()
        self._add_experience()
        self._add_expertise()
        self._add_thought_leadership()
        self._add_education()
        
        # Build PDF
        doc.build(self.story)
        print(f"✓ Resume PDF generated: {self.resume_file}")

        # Create PDF document
        doc = SimpleDocTemplate(
            self.bio_file,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build story
        self.story = []
        self._add_header()
        self._add_bio()
        
        # Build PDF
        doc.build(self.story)
        print(f"✓ Bio PDF generated: {self.bio_file}")


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python generate_resume_pdf.py <yaml_file> [output_file]")
        print("Example: python generate_resume_pdf.py resume.yaml my_resume.pdf bio.pdf")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    resume_file = sys.argv[2] if len(sys.argv) > 2 else "resume.pdf"
    bio_file = sys.argv[3] if len(sys.argv) > 3 else "bio.pdf"
    
    if not os.path.exists(yaml_file):
        print(f"Error: YAML file not found: {yaml_file}")
        sys.exit(1)
    
    generator = ResumeGenerator(yaml_file, resume_file, bio_file)
    generator.generate()


if __name__ == "__main__":
    main()
