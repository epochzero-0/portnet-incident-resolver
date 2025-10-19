"""
Incident Parser - Extracts entities and information from incident reports
"""
import re
from typing import Dict, List, Optional
from datetime import datetime


class IncidentParser:
    """Parse incident text and extract key entities"""
    
    def __init__(self):
        """Initialize parser with entity patterns"""
        self.patterns = {
            # Container number: XXXX1234567
            'container': r'\b[A-Z]{4}\d{7}\b',
            
            # Vessel name: MV VESSEL NAME or MV VESSEL NAME/07E
            'vessel': r'MV\s+[A-Z][A-Z\s]+(?:/\d+[A-Z]?)?',
            
            # Error codes: VESSEL_ERR_4, EDI_ERR_1
            'error_code': r'[A-Z_]+ERR[_-]\d+',
            
            # Reference IDs: REF-IFT-@@@7, TCK-123456, INC-123456
            'reference': r'(REF|TCK|INC|ALR|SMS)-[A-Z0-9@-]+',
            
            # Email addresses
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            
            # Booking references: BK-XXXXXXX
            'booking': r'BK-[A-Z0-9]+',
        }
    
    def parse(self, incident_text: str) -> Dict:
        """
        Parse incident text and extract all relevant information
        
        Args:
            incident_text: Raw incident report text
            
        Returns:
            Dictionary with parsed incident information
        """
        entities = self._extract_entities(incident_text)
        incident_type = self._classify_incident(incident_text, entities)
        module = self._identify_module(incident_text, entities)
        severity = self._estimate_severity(incident_text)
        keywords = self._extract_keywords(incident_text)
        
        return {
            'raw_text': incident_text,
            'entities': entities,
            'incident_type': incident_type,
            'module': module,
            'severity': severity,
            'keywords': keywords,
            'parsed_at': datetime.now().isoformat()
        }
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all entities from text using regex patterns
        
        Args:
            text: Incident text
            
        Returns:
            Dictionary of entity types to lists of found values
        """
        entities = {}
        
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Remove duplicates while preserving order
                unique_matches = list(dict.fromkeys(matches))
                entities[entity_type] = unique_matches
        
        return entities
    
    def _classify_incident(self, text: str, entities: Dict) -> str:
        """
        Classify the type of incident
        
        Args:
            text: Incident text
            entities: Extracted entities
            
        Returns:
            Incident type classification
        """
        text_lower = text.lower()
        
        # Check for specific keywords
        if any(word in text_lower for word in ['duplicate', 'duplicated', 'two identical']):
            return 'duplicate_entry'
        
        if any(word in text_lower for word in ['stuck', 'error status', 'not acknowledged']):
            return 'stuck_process'
        
        if any(word in text_lower for word in ['inconsistency', 'mismatch', 'conflicting']):
            return 'data_inconsistency'
        
        if any(word in text_lower for word in ['timeout', 'timed out', 'not responding']):
            return 'timeout'
        
        if any(word in text_lower for word in ['unable to create', 'cannot create', 'creation failed']):
            return 'creation_failure'
        
        if 'error_code' in entities:
            return 'error_code_incident'
        
        if any(word in text_lower for word in ['failed', 'failure', 'error']):
            return 'general_error'
        
        return 'unknown'
    
    def _identify_module(self, text: str, entities: Dict) -> str:
        """
        Identify which module/system is affected
        
        Args:
            text: Incident text
            entities: Extracted entities
            
        Returns:
            Module name
        """
        text_lower = text.lower()
        
        # Check for module keywords
        if any(word in text_lower for word in ['edi', 'edifact', 'codeco', 'baplie', 'coarri']):
            return 'EDI/API'
        
        if any(word in text_lower for word in ['vessel', 'ship', 'berth', 'arrival', 'departure']):
            return 'Vessel'
        
        if 'container' in entities or any(word in text_lower for word in ['container', 'cntr']):
            return 'Container'
        
        if any(word in text_lower for word in ['booking', 'bk-']):
            return 'Booking'
        
        if any(word in text_lower for word in ['database', 'db', 'query', 'sql']):
            return 'Database'
        
        return 'General'
    
    def _estimate_severity(self, text: str) -> str:
        """
        Estimate incident severity based on keywords
        
        Args:
            text: Incident text
            
        Returns:
            Severity level: LOW, MEDIUM, HIGH, CRITICAL
        """
        text_lower = text.lower()
        
        # Critical keywords
        if any(word in text_lower for word in ['urgent', 'critical', 'immediately', 'production down', 'outage']):
            return 'CRITICAL'
        
        # High severity keywords
        if any(word in text_lower for word in ['high priority', 'multiple', 'affecting customers', 'business impact']):
            return 'HIGH'
        
        # Low severity keywords
        if any(word in text_lower for word in ['minor', 'low priority', 'cosmetic', 'display only']):
            return 'LOW'
        
        # Default to MEDIUM
        return 'MEDIUM'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords for searching
        
        Args:
            text: Incident text
            
        Returns:
            List of keywords
        """
        # Common technical keywords to look for
        keyword_patterns = [
            'duplicate', 'error', 'failed', 'timeout', 'stuck',
            'inconsistency', 'mismatch', 'conflict', 'invalid',
            'missing', 'not found', 'unable', 'cannot',
            'vessel', 'container', 'edi', 'api', 'database',
            'booking', 'advice', 'message', 'acknowledgment'
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in keyword_patterns if kw in text_lower]
        
        # Add error codes as keywords
        error_codes = re.findall(r'[A-Z_]+ERR[_-]\d+', text)
        found_keywords.extend(error_codes)
        
        return list(set(found_keywords))  # Remove duplicates
    
    def get_search_terms(self, parsed_incident: Dict) -> List[str]:
        """
        Generate search terms from parsed incident for log/case searching
        
        Args:
            parsed_incident: Parsed incident dictionary
            
        Returns:
            List of search terms
        """
        search_terms = []
        
        # Add all entity values
        entities = parsed_incident.get('entities', {})
        for entity_type, values in entities.items():
            search_terms.extend(values)
        
        # Add keywords
        keywords = parsed_incident.get('keywords', [])
        search_terms.extend(keywords)
        
        return list(set(search_terms))  # Remove duplicates
    
    def format_summary(self, parsed_incident: Dict) -> str:
        """
        Generate human-readable summary of parsed incident
        
        Args:
            parsed_incident: Parsed incident dictionary
            
        Returns:
            Formatted summary string
        """
        entities = parsed_incident.get('entities', {})
        
        summary = f"""
Incident Summary
================
Type: {parsed_incident.get('incident_type', 'Unknown')}
Module: {parsed_incident.get('module', 'Unknown')}
Severity: {parsed_incident.get('severity', 'MEDIUM')}

Entities Found:
"""
        
        for entity_type, values in entities.items():
            summary += f"  {entity_type}: {', '.join(values)}\n"
        
        keywords = parsed_incident.get('keywords', [])
        if keywords:
            summary += f"\nKeywords: {', '.join(keywords[:10])}"
        
        return summary