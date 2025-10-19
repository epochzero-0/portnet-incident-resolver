"""
Parser for Knowledge Base document
Extracts known issues, procedures, and solutions
"""
from docx import Document
from typing import List, Dict, Optional


class KnowledgeBaseParser:
    """Parse and search knowledge base document"""
    
    def __init__(self, file_path: str):
        """
        Initialize parser with document path
        
        Args:
            file_path: Path to Knowledge Base.docx
        """
        self.file_path = file_path
        self.content = None
        self.sections = []
        self._load_document()
    
    def _load_document(self):
        """Load and parse Word document"""
        try:
            doc = Document(self.file_path)
            
            # Extract all paragraphs
            paragraphs = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append({
                        'text': text,
                        'style': para.style.name
                    })
            
            # Combine into full content
            self.content = '\n'.join([p['text'] for p in paragraphs])
            
            # Try to identify sections based on headings
            self._extract_sections(paragraphs)
            
            print(f"✓ Loaded knowledge base: {len(paragraphs)} paragraphs, {len(self.sections)} sections")
            
        except Exception as e:
            raise Exception(f"Failed to load knowledge base: {str(e)}")
    
    def _extract_sections(self, paragraphs: List[Dict]):
        """
        Extract sections based on headings
        
        Args:
            paragraphs: List of paragraph dictionaries
        """
        current_section = None
        current_content = []
        
        for para in paragraphs:
            # Check if this is a heading
            if 'Heading' in para['style']:
                # Save previous section
                if current_section:
                    self.sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content)
                    })
                
                # Start new section
                current_section = para['text']
                current_content = []
            else:
                # Add to current section
                if current_section:
                    current_content.append(para['text'])
        
        # Add last section
        if current_section:
            self.sections.append({
                'title': current_section,
                'content': '\n'.join(current_content)
            })
    
    def get_full_content(self) -> str:
        """
        Get full document content
        
        Returns:
            Complete document text
        """
        return self.content
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """
        Search knowledge base by keywords
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of matching sections with relevance scores
        """
        if not keywords:
            return []
        
        matches = []
        
        # Search in sections if available
        if self.sections:
            for section in self.sections:
                title = section['title'].lower()
                content = section['content'].lower()
                combined = f"{title} {content}"
                
                # Count matches
                keyword_matches = sum(1 for kw in keywords if kw.lower() in combined)
                
                if keyword_matches > 0:
                    relevance = keyword_matches / len(keywords)
                    matches.append({
                        'section_title': section['title'],
                        'content': section['content'],
                        'relevance': relevance,
                        'matched_keywords': [k for k in keywords if k.lower() in combined]
                    })
        else:
            # Fallback: search in full content
            content_lower = self.content.lower()
            keyword_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
            
            if keyword_matches > 0:
                matches.append({
                    'section_title': 'Full Document',
                    'content': self.content,
                    'relevance': keyword_matches / len(keywords),
                    'matched_keywords': [k for k in keywords if k.lower() in content_lower]
                })
        
        # Sort by relevance
        matches.sort(key=lambda x: x['relevance'], reverse=True)
        
        return matches
    
    def search_procedures(self, keywords: List[str]) -> List[str]:
        """
        Search for specific procedures or SOPs
        
        Args:
            keywords: Keywords related to the procedure
            
        Returns:
            List of relevant procedure texts
        """
        matches = self.search_by_keywords(keywords)
        
        # Extract procedure-related content
        procedures = []
        for match in matches:
            content = match['content']
            # Look for numbered steps or procedure indicators
            if any(indicator in content.lower() for indicator in ['step', 'procedure', 'sop', '1.', '2.']):
                procedures.append(content)
        
        return procedures
    
    def get_section_by_title(self, title: str) -> Optional[Dict]:
        """
        Get specific section by title
        
        Args:
            title: Section title to search for
            
        Returns:
            Section dictionary or None
        """
        for section in self.sections:
            if title.lower() in section['title'].lower():
                return section
        return None
    
    def get_all_sections(self) -> List[Dict]:
        """
        Get all sections
        
        Returns:
            List of all sections
        """
        return self.sections