#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word Document Parser for Strinz Margarethä Chronicle
Extracts content from Word document XML and converts to structured Markdown
"""

import xml.etree.ElementTree as ET
import re
import os
import shutil
from pathlib import Path

class DocxParser:
    def __init__(self, extracted_path):
        self.extracted_path = Path(extracted_path)
        self.document_xml = self.extracted_path / "word" / "document.xml"
        self.media_path = self.extracted_path / "word" / "media"
        self.rels_xml = self.extracted_path / "word" / "_rels" / "document.xml.rels"
        
        # Word namespaces
        self.namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
            'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture'
        }
        
        # Image relationships mapping
        self.image_rels = {}
        self.load_relationships()
        
    def load_relationships(self):
        """Load image relationships from document.xml.rels"""
        try:
            tree = ET.parse(self.rels_xml)
            root = tree.getroot()
            
            for rel in root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                rel_id = rel.get('Id')
                target = rel.get('Target')
                if target and target.startswith('media/'):
                    self.image_rels[rel_id] = target.replace('media/', '')
        except Exception as e:
            print(f"Error loading relationships: {e}")
    
    def extract_text_from_element(self, element):
        """Extract text content from XML element"""
        text_parts = []
        
        # Get text from w:t elements
        for t_elem in element.findall('.//w:t', self.namespaces):
            if t_elem.text:
                text_parts.append(t_elem.text)
        
        return ''.join(text_parts)
    
    def is_heading(self, paragraph):
        """Check if paragraph is a heading based on style"""
        style_elem = paragraph.find('.//w:pStyle', self.namespaces)
        if style_elem is not None:
            style_val = style_elem.get('{' + self.namespaces['w'] + '}val', '')
            return 'heading' in style_val.lower() or 'title' in style_val.lower()
        
        # Check for bold formatting as potential heading
        bold_elem = paragraph.find('.//w:b', self.namespaces)
        if bold_elem is not None:
            text = self.extract_text_from_element(paragraph).strip()
            # Short bold text might be a heading
            if len(text) < 100 and text:
                return True
        
        return False
    
    def get_heading_level(self, paragraph):
        """Determine heading level"""
        style_elem = paragraph.find('.//w:pStyle', self.namespaces)
        if style_elem is not None:
            style_val = style_elem.get('{' + self.namespaces['w'] + '}val', '')
            # Try to extract number from heading style
            match = re.search(r'(\d+)', style_val)
            if match:
                return min(int(match.group(1)), 6)  # Max heading level 6
        
        return 1  # Default to h1
    
    def extract_images_from_paragraph(self, paragraph):
        """Extract image references from paragraph"""
        images = []
        
        # Look for drawing elements
        for drawing in paragraph.findall('.//w:drawing', self.namespaces):
            # Find blip elements that reference images
            for blip in drawing.findall('.//a:blip', self.namespaces):
                embed_id = blip.get('{' + self.namespaces['r'] + '}embed')
                if embed_id and embed_id in self.image_rels:
                    image_file = self.image_rels[embed_id]
                    images.append(image_file)
        
        return images
    
    def parse_document(self):
        """Parse the main document and extract structured content"""
        try:
            tree = ET.parse(self.document_xml)
            root = tree.getroot()
            
            content_sections = []
            current_section = {
                'title': 'Introduction',
                'level': 1,
                'content': [],
                'images': []
            }
            
            # Process each paragraph
            for para in root.findall('.//w:p', self.namespaces):
                text = self.extract_text_from_element(para).strip()
                images = self.extract_images_from_paragraph(para)
                
                if not text and not images:
                    continue
                
                if self.is_heading(para) and text:
                    # Save current section if it has content
                    if current_section['content'] or current_section['images']:
                        content_sections.append(current_section)
                    
                    # Start new section
                    level = self.get_heading_level(para)
                    current_section = {
                        'title': text,
                        'level': level,
                        'content': [],
                        'images': []
                    }
                else:
                    # Add content to current section
                    if text:
                        current_section['content'].append(text)
                    if images:
                        current_section['images'].extend(images)
            
            # Add final section
            if current_section['content'] or current_section['images']:
                content_sections.append(current_section)
            
            return content_sections
            
        except Exception as e:
            print(f"Error parsing document: {e}")
            return []
    
    def create_images_directory(self, output_dir):
        """Create images directory and copy all images"""
        images_dir = Path(output_dir) / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Copy all images from media directory
        if self.media_path.exists():
            for image_file in self.media_path.glob("*"):
                if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    shutil.copy2(image_file, images_dir / image_file.name)
        
        return images_dir
    
    def generate_markdown_files(self, content_sections, output_dir="markdown_output"):
        """Generate structured Markdown files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create images directory
        self.create_images_directory(output_dir)
        
        # Group sections by main headings (level 1)
        file_sections = []
        current_file = None
        
        for section in content_sections:
            if section['level'] == 1:
                if current_file:
                    file_sections.append(current_file)
                current_file = {
                    'title': section['title'],
                    'filename': self.sanitize_filename(section['title']),
                    'sections': [section]
                }
            elif current_file:
                current_file['sections'].append(section)
        
        if current_file:
            file_sections.append(current_file)
        
        # Generate individual markdown files
        for file_info in file_sections:
            self.write_markdown_file(file_info, output_path)
        
        # Generate main index file
        self.write_index_file(file_sections, output_path)
        
        return file_sections
    
    def sanitize_filename(self, title):
        """Convert title to valid filename"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.lower()
        # Limit length
        if len(filename) > 50:
            filename = filename[:50]
        return filename + '.md'
    
    def write_markdown_file(self, file_info, output_path):
        """Write individual markdown file"""
        filepath = output_path / file_info['filename']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {file_info['title']}\n\n")
            
            for section in file_info['sections']:
                # Write heading
                heading_prefix = '#' * min(section['level'], 6)
                f.write(f"{heading_prefix} {section['title']}\n\n")
                
                # Write content
                for content in section['content']:
                    if content.strip():
                        f.write(f"{content}\n\n")
                
                # Write images
                for image in section['images']:
                    f.write(f"![Image](images/{image})\n\n")
    
    def write_index_file(self, file_sections, output_path):
        """Write main index file"""
        index_path = output_path / "README.md"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Strinz Margarethä Chronicle\n\n")
            f.write("This is the complete chronicle of Strinz Margarethä, extracted and organized from the original Word document.\n\n")
            f.write("## Table of Contents\n\n")
            
            for i, file_info in enumerate(file_sections, 1):
                f.write(f"{i}. [{file_info['title']}]({file_info['filename']})\n")
            
            f.write(f"\n\n## Statistics\n\n")
            f.write(f"- Total sections: {len(file_sections)}\n")
            
            # Count images
            total_images = sum(len(section['images']) for file_info in file_sections for section in file_info['sections'])
            f.write(f"- Total images: {total_images}\n")

def main():
    parser = DocxParser("docx_extracted")
    print("Parsing Word document...")
    
    content_sections = parser.parse_document()
    print(f"Found {len(content_sections)} sections")
    
    print("Generating Markdown files...")
    file_sections = parser.generate_markdown_files(content_sections)
    print(f"Generated {len(file_sections)} Markdown files")
    
    print("Extraction complete!")
    print("Files created in 'markdown_output' directory")

if __name__ == "__main__":
    main()
