#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Word Document Parser for Strinz Margarethä Chronicle
Creates optimally structured Markdown files with refined categorization
"""

import xml.etree.ElementTree as ET
import re
import os
import shutil
from pathlib import Path
from collections import defaultdict

class FinalDocxParser:
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
    
    def categorize_content(self, text):
        """Categorize content into logical groups with refined logic"""
        text_lower = text.lower()
        
        # Introduction and overview
        if re.search(r'\b(vorwort|einleitung|strinz.*margareth|ortsname|bedeutung.*name|weitere.*ortsname)\b', text_lower):
            return "00_introduction"
        
        # Historical periods - more precise matching
        if re.search(r'\b(vor.*christi.*geburt|antike|römer|germanen|kelten|300.*millionen.*jahr)\b', text_lower):
            return "01_prehistory_ancient"
        elif re.search(r'\b(1[0-4]\d{2}|mittelalter|strentzge|minorem)\b', text_lower) and not re.search(r'\b(19|20)\d{2}\b', text_lower):
            return "02_medieval"
        elif re.search(r'\b(1[5-7]\d{2}|reformation|renaissance)\b', text_lower) and not re.search(r'\b(18|19|20)\d{2}\b', text_lower):
            return "03_early_modern"
        elif re.search(r'\b(1[8-9]\d{2}|napoleon|kaiser.*wilhelm|reich.*1871|friedensfeier)\b', text_lower) and not re.search(r'\b(19[1-4]|20)\d{2}\b', text_lower):
            return "04_modern"
        elif re.search(r'\b(19[0-4]\d|weltkrieg|weimar|nazi|hitler|starfighter)\b', text_lower):
            return "05_world_wars"
        elif re.search(r'\b(19[5-9]\d|20\d{2}|nachkrieg|bundesrepublik|wiederaufbau)\b', text_lower):
            return "06_contemporary"
        
        # Thematic categories with better matching
        elif re.search(r'\b(wappen|gemeinde.*wahl|verwaltung|politik|wahl.*reich|bundestagswahl|bürgermeister|ortsgericht|standesamt)\b', text_lower):
            return "10_administration"
        elif re.search(r'\b(kirche|pfarrer|religion|gott|heilig|margareth.*patron|gottesdienst|einweihung)\b', text_lower):
            return "11_religion"
        elif re.search(r'\b(schule|lehrer|bildung|unterricht|rektor|volksschule)\b', text_lower):
            return "12_education"
        elif re.search(r'\b(bergbau|steinbruch|mühle.*strinz|handwerk|beruf|bäcker|schmied|wagner|zimmermann|kramer|leineweber|schäfer|hirte)\b', text_lower):
            return "13_economy_trades"
        elif re.search(r'\b(brunnen|wasser|straße|gebäude|haus.*name|bau|infrastruktur|laufbrunnen)\b', text_lower):
            return "14_infrastructure"
        elif re.search(r'\b(fest|brauch|tradition|kerb|hochzeit|fastnacht|feier|bei.*1.*fängt|hohoho)\b', text_lower):
            return "15_customs_traditions"
        elif re.search(r'\b(sage|märchen|erzählung|schinderhannes|hexenhaus|spuk|feuerbuche)\b', text_lower):
            return "16_stories_legends"
        elif re.search(r'\b(person|familie|hausname|bewohner|catharina|anna.*maria|johann|philipp)\b', text_lower):
            return "17_people_families"
        elif re.search(r'\b(begriffe|glossar|erklärung|bedeutung|geld|währung|albus|batzen|gulden|flosin|terminei|centgericht|lehen|vogt)\b', text_lower):
            return "18_glossary_terms"
        
        # War and conflict specific
        elif re.search(r'\b(krieg|soldat|gefallen|einzug|mobilmachung|front|schlacht|weißenburg|franzos|deutsch.*trupp)\b', text_lower):
            return "05_world_wars"
        
        # Specific events and chronicles
        elif re.search(r'\b(chronik|ereignis|februar.*1945|märz.*1945|april.*1945|mai.*1945|juni.*1945|juli.*1945|august.*1945|september.*1945|oktober.*1945|november.*1945)\b', text_lower):
            return "20_chronicles_events"
        
        # Transportation and infrastructure
        elif re.search(r'\b(bahn|längsbahn|eisenbahn|verkehr|transport)\b', text_lower):
            return "21_transportation"
        
        # Agriculture and rural life
        elif re.search(r'\b(landwirtschaft|bauer|ernte|getreide|vieh|stall|acker|zehnt|schluckerter|frühstück|mittagstisch|abendessen)\b', text_lower):
            return "22_agriculture"
        
        # Conclusion and thanks
        elif re.search(r'\b(dank|ende|schluss|nachwort|thorsten.*stötzer)\b', text_lower):
            return "23_conclusion"
        
        # Default to miscellaneous for remaining content
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
                'title': 'Einleitung',
                'content': [],
                'images': []
            }
            
            # Process each paragraph
            for para in root.findall('.//w:p', self.namespaces):
                text = self.extract_text_from_element(para).strip()
                images = self.extract_images_from_paragraph(para)
                
                if not text and not images:
                    continue
                
                # Check if this might be a section heading
                is_potential_heading = (
                    len(text) < 200 and 
                    (text.isupper() or 
                     any(char.isupper() for char in text[:20]) or
                     re.match(r'^\d{3,4}', text) or
                     text.endswith(':') or
                     re.match(r'^[A-ZÄÖÜ]', text))
                )
                
                if text and is_potential_heading and current_section['content']:
                    # Save current section if it has content
                    category = self.categorize_content(current_section['title'] + ' ' + ' '.join(current_section['content'][:3]))
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
                category = self.categorize_content(current_section['title'] + ' ' + ' '.join(current_section['content'][:3]))
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
    
    def generate_markdown_files(self, categorized_content, output_dir="final_markdown"):
        """Generate final structured Markdown files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create images directory
        self.create_images_directory(output_dir)
        
        # Category names mapping
        category_names = {
            "00_introduction": "Einleitung und Ortsname",
            "01_prehistory_ancient": "Vorgeschichte und Antike",
            "02_medieval": "Mittelalter (bis 1500)",
            "03_early_modern": "Frühe Neuzeit (1500-1800)",
            "04_modern": "Neuzeit (1800-1914)",
            "05_world_wars": "Weltkriege und Zwischenkriegszeit (1914-1945)",
            "06_contemporary": "Nachkriegszeit bis heute (1945-)",
            "10_administration": "Verwaltung und Politik",
            "11_religion": "Kirche und Religion",
            "12_education": "Bildung und Schule",
            "13_economy_trades": "Wirtschaft und Handwerk",
            "14_infrastructure": "Infrastruktur und Gebäude",
            "15_customs_traditions": "Bräuche und Traditionen",
            "16_stories_legends": "Sagen und Erzählungen",
            "17_people_families": "Personen und Familien",
            "18_glossary_terms": "Begriffe und Glossar",
            "20_chronicles_events": "Chronik der Ereignisse 1945",
            "21_transportation": "Verkehr und Eisenbahn",
            "22_agriculture": "Landwirtschaft und ländliches Leben",
            "23_conclusion": "Schluss und Danksagung",
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
                
                for i, section in enumerate(sections):
                    # Write section heading
                    f.write(f"## {section['title']}\n\n")
                    
                    # Write content
                    for content in section['content']:
                        if content.strip():
                            f.write(f"{content}\n\n")
                    
                    # Write images
                    for image in section['images']:
                        f.write(f"![Image](images/{image})\n\n")
                    
                    # Add separator between sections (except for last section)
                    if i < len(sections) - 1:
                        f.write("---\n\n")
        
        # Generate main index file
        self.write_index_file(file_list, categorized_content, output_path)
        
        return file_list
    
    def write_index_file(self, file_list, categorized_content, output_path):
        """Write comprehensive index file"""
        index_path = output_path / "README.md"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Chronik von Strinz-Margarethä\n\n")
            f.write("Diese umfassende Chronik dokumentiert die Geschichte von Strinz-Margarethä ")
            f.write("von den prähistorischen Anfängen bis zur Gegenwart. Der Inhalt wurde aus dem ")
            f.write("ursprünglichen Word-Dokument vollständig extrahiert und thematisch sowie ")
            f.write("chronologisch strukturiert.\n\n")
            
            f.write("## Über diese Chronik\n\n")
            f.write("Die Chronik wurde ursprünglich als Word-Dokument erstellt und enthält eine ")
            f.write("Fülle von historischen Informationen, Bildern, Dokumenten und Erzählungen ")
            f.write("über Strinz-Margarethä. Für eine bessere Nutzbarkeit wurde der Inhalt in ")
            f.write("thematische Abschnitte gegliedert.\n\n")
            
            f.write("## Inhaltsverzeichnis\n\n")
            
            for file_info in file_list:
                f.write(f"- **[{file_info['title']}]({file_info['filename']})**")
                f.write(f" - {file_info['sections_count']} Abschnitte\n")
            
            f.write(f"\n## Statistiken\n\n")
            f.write(f"- **Anzahl Hauptkategorien:** {len(file_list)}\n")
            
            total_sections = sum(len(sections) for sections in categorized_content.values())
            f.write(f"- **Gesamtanzahl Abschnitte:** {total_sections}\n")
            
            # Count images
            total_images = sum(
                len(section['images']) 
                for sections in categorized_content.values() 
                for section in sections
            )
            f.write(f"- **Gesamtanzahl Bilder:** {total_images}\n")
            
            f.write(f"\n## Hinweise zur Nutzung\n\n")
            f.write("- **Bilder:** Alle Bilder sind im `images/` Ordner gespeichert und in den Texten verlinkt\n")
            f.write("- **Struktur:** Die Chronik ist sowohl thematisch als auch chronologisch geordnet\n")
            f.write("- **Navigation:** Jede Kategorie-Datei enthält verwandte Abschnitte\n")
            f.write("- **Trennung:** Abschnitte sind durch Trennlinien (`---`) voneinander getrennt\n")
            f.write("- **Vollständigkeit:** Alle Inhalte des ursprünglichen Dokuments sind enthalten\n\n")
            
            f.write("## Quellenhinweis\n\n")
            f.write("Diese Chronik basiert auf dem umfangreichen Word-Dokument ")
            f.write("'Strinzer Chronik überarbeitet.docx' und wurde automatisch ")
            f.write("extrahiert und strukturiert, um eine bessere Lesbarkeit und ")
            f.write("Navigation zu ermöglichen.\n")

def main():
    parser = FinalDocxParser("docx_extracted")
    print("Parsing Word document with final optimized structure...")
    
    categorized_content = parser.parse_document()
    print(f"Found {len(categorized_content)} categories")
    for category, sections in sorted(categorized_content.items()):
        print(f"  {category}: {len(sections)} sections")
    
    print("Generating final structured Markdown files...")
    file_list = parser.generate_markdown_files(categorized_content)
    print(f"Generated {len(file_list)} structured Markdown files")
    
    print("Final extraction complete!")
    print("Files created in 'final_markdown' directory")

if __name__ == "__main__":
    main()
