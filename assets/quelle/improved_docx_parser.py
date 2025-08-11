#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Word Document Parser for Strinz Margarethä Chronicle
Creates better structured Markdown files with logical groupings
"""

import xml.etree.ElementTree as ET
import re
import os
import shutil
from pathlib import Path
from collections import defaultdict

class ImprovedDocxParser:
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
    
    def is_major_heading(self, text):
        """Check if text represents a major section heading"""
        text = text.strip()
        
        # Check for major section indicators
        major_indicators = [
            "chronik", "geschichte", "einleitung", "vorwort", "entstehung",
            "mittelalter", "neuzeit", "weltkrieg", "nachkriegszeit",
            "glossar", "begriffe", "sagen", "märchen", "erzählungen",
            "wappen", "gemeinde", "kirche", "schule", "bergbau", "steinbruch",
            "bräuche", "traditionen", "feste", "handwerk", "berufe", "mühle",
            "brunnen", "personen", "familien", "namen", "wahlen", "politik"
        ]
        
        text_lower = text.lower()
        for indicator in major_indicators:
            if indicator in text_lower:
                return True
        
        # Check for year ranges that might indicate major periods
        if re.match(r'^\d{3,4}.*\d{3,4}', text):
            return True
            
        # Check for very short titles that might be major sections
        if len(text) < 50 and any(char.isupper() for char in text):
            return True
            
        return False
    
    def categorize_content(self, text):
        """Categorize content into logical groups"""
        text_lower = text.lower()
        
        # Historical periods
        if re.search(r'\b(vor.*christi|antike|römer|germanen|kelten)\b', text_lower):
            return "01_prehistory_ancient"
        elif re.search(r'\b(mittelalter|1[0-4]\d{2})\b', text_lower):
            return "02_medieval"
        elif re.search(r'\b(1[5-7]\d{2}|reformation|renaissance)\b', text_lower):
            return "03_early_modern"
        elif re.search(r'\b(1[8-9]\d{2}|napoleon|kaiser|reich)\b', text_lower):
            return "04_modern"
        elif re.search(r'\b(19[0-4]\d|weltkrieg|weimar|nazi)\b', text_lower):
            return "05_world_wars"
        elif re.search(r'\b(19[5-9]\d|20\d{2}|nachkrieg|bundesrepublik)\b', text_lower):
            return "06_contemporary"
        
        # Thematic categories
        elif re.search(r'\b(wappen|gemeinde|verwaltung|politik|wahl|bürgermeister)\b', text_lower):
            return "10_administration"
        elif re.search(r'\b(kirche|pfarrer|religion|gott|heilig|margareth)\b', text_lower):
            return "11_religion"
        elif re.search(r'\b(schule|lehrer|bildung|unterricht)\b', text_lower):
            return "12_education"
        elif re.search(r'\b(bergbau|steinbruch|mühle|handwerk|beruf|bäcker|schmied)\b', text_lower):
            return "13_economy_trades"
        elif re.search(r'\b(brunnen|wasser|straße|gebäude|haus|bau)\b', text_lower):
            return "14_infrastructure"
        elif re.search(r'\b(fest|brauch|tradition|kerb|hochzeit|fastnacht)\b', text_lower):
            return "15_customs_traditions"
        elif re.search(r'\b(sage|märchen|erzählung|geschichte|schinderhannes)\b', text_lower):
            return "16_stories_legends"
        elif re.search(r'\b(person|familie|name|hausname|bewohner)\b', text_lower):
            return "17_people_families"
        elif re.search(r'\b(begriffe|glossar|erklärung|bedeutung|geld|währung)\b', text_lower):
            return "18_glossary_terms"
        elif re.search(r'\b(dank|ende|schluss|nachwort)\b', text_lower):
            return "19_conclusion"
        
        # Default to miscellaneous
        return "99_miscellaneous"
    
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
            
            # Group content by categories
            categorized_content = defaultdict(list)
            current_section = {
                'title': 'Introduction',
                'content': [],
                'images': []
            }
            
            # Process each paragraph
            for para in root.findall('.//w:p', self.namespaces):
                text = self.extract_text_from_element(para).strip()
                images = self.extract_images_from_paragraph(para)
                
                if not text and not images:
                    continue
                
                # Check if this is a major heading
                if text and (self.is_major_heading(text) or len(text) < 100):
                    # Save current section if it has content
                    if current_section['content'] or current_section['images']:
                        category = self.categorize_content(current_section['title'])
                        categorized_content[category].append(current_section)
                    
                    # Start new section
                    current_section = {
                        'title': text,
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
                category = self.categorize_content(current_section['title'])
                categorized_content[category].append(current_section)
            
            return categorized_content
            
        except Exception as e:
            print(f"Error parsing document: {e}")
            return {}
    
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
    
    def generate_markdown_files(self, categorized_content, output_dir="structured_markdown"):
        """Generate structured Markdown files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create images directory
        self.create_images_directory(output_dir)
        
        # Category names mapping
        category_names = {
            "01_prehistory_ancient": "Vorgeschichte und Antike",
            "02_medieval": "Mittelalter",
            "03_early_modern": "Frühe Neuzeit",
            "04_modern": "Neuzeit bis 1900",
            "05_world_wars": "Weltkriege und Zwischenkriegszeit",
            "06_contemporary": "Nachkriegszeit bis heute",
            "10_administration": "Verwaltung und Politik",
            "11_religion": "Kirche und Religion",
            "12_education": "Bildung und Schule",
            "13_economy_trades": "Wirtschaft und Handwerk",
            "14_infrastructure": "Infrastruktur und Gebäude",
            "15_customs_traditions": "Bräuche und Traditionen",
            "16_stories_legends": "Sagen und Erzählungen",
            "17_people_families": "Personen und Familien",
            "18_glossary_terms": "Begriffe und Glossar",
            "19_conclusion": "Schluss und Danksagung",
            "99_miscellaneous": "Verschiedenes"
        }
        
        # Generate files for each category
        file_list = []
        for category, sections in sorted(categorized_content.items()):
            if not sections:
                continue
                
            category_name = category_names.get(category, category.replace('_', ' ').title())
            filename = f"{category}.md"
            filepath = output_path / filename
            
            file_list.append({
                'filename': filename,
                'title': category_name,
                'sections_count': len(sections),
                'category': category
            })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {category_name}\n\n")
                
                for section in sections:
                    # Write section heading
                    f.write(f"## {section['title']}\n\n")
                    
                    # Write content
                    for content in section['content']:
                        if content.strip():
                            f.write(f"{content}\n\n")
                    
                    # Write images
                    for image in section['images']:
                        f.write(f"![Image](images/{image})\n\n")
                    
                    f.write("---\n\n")  # Section separator
        
        # Generate main index file
        self.write_index_file(file_list, categorized_content, output_path)
        
        return file_list
    
    def write_index_file(self, file_list, categorized_content, output_path):
        """Write main index file"""
        index_path = output_path / "README.md"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Chronik von Strinz Margarethä\n\n")
            f.write("Diese Chronik dokumentiert die Geschichte von Strinz Margarethä von den Anfängen bis zur Gegenwart. ")
            f.write("Der Inhalt wurde aus dem ursprünglichen Word-Dokument extrahiert und thematisch strukturiert.\n\n")
            
            f.write("## Inhaltsverzeichnis\n\n")
            
            for file_info in file_list:
                f.write(f"- [{file_info['title']}]({file_info['filename']}) ({file_info['sections_count']} Abschnitte)\n")
            
            f.write(f"\n## Statistiken\n\n")
            f.write(f"- Anzahl Hauptkategorien: {len(file_list)}\n")
            
            total_sections = sum(len(sections) for sections in categorized_content.values())
            f.write(f"- Gesamtanzahl Abschnitte: {total_sections}\n")
            
            # Count images
            total_images = sum(
                len(section['images']) 
                for sections in categorized_content.values() 
                for section in sections
            )
            f.write(f"- Gesamtanzahl Bilder: {total_images}\n")
            
            f.write(f"\n## Hinweise zur Nutzung\n\n")
            f.write("- Alle Bilder sind im `images/` Ordner gespeichert\n")
            f.write("- Die Chronik ist thematisch und chronologisch geordnet\n")
            f.write("- Jede Kategorie-Datei enthält verwandte Abschnitte\n")
            f.write("- Abschnitte sind durch Trennlinien (`---`) getrennt\n")

def main():
    parser = ImprovedDocxParser("docx_extracted")
    print("Parsing Word document with improved structure...")
    
    categorized_content = parser.parse_document()
    print(f"Found {len(categorized_content)} categories")
    for category, sections in categorized_content.items():
        print(f"  {category}: {len(sections)} sections")
    
    print("Generating structured Markdown files...")
    file_list = parser.generate_markdown_files(categorized_content)
    print(f"Generated {len(file_list)} structured Markdown files")
    
    print("Extraction complete!")
    print("Files created in 'structured_markdown' directory")

if __name__ == "__main__":
    main()
