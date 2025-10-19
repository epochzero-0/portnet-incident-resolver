"""
Parser for Product Team Escalation Contacts PDF
Extracts contact information for different modules and roles
"""
import re
from PyPDF2 import PdfReader
from typing import List, Dict, Optional


class EscalationContactsParser:
    """Parse and route escalation contacts"""
    
    def __init__(self, file_path: str):
        """
        Initialize parser with PDF path
        
        Args:
            file_path: Path to Product Team Escalation Contacts.pdf
        """
        self.file_path = file_path
        self.contacts = []
        self.contacts_by_module = {}
        self._load_contacts()
    
    def _load_contacts(self):
        """Load and parse PDF"""
        try:
            reader = PdfReader(self.file_path)
            
            # Extract text from all pages
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
            
            # Parse contacts from text
            self._parse_contacts(full_text)
            
            print(f"✓ Loaded {len(self.contacts)} escalation contacts")
            
        except Exception as e:
            raise Exception(f"Failed to load escalation contacts: {str(e)}")
    
    def _parse_contacts(self, text: str):
        """
        Parse contact information from text
        
        Args:
            text: Raw text from PDF
        """
        # This is a flexible parser that adapts to the PDF structure
        # We'll extract patterns like:
        # - Names
        # - Email addresses
        # - Phone numbers
        # - Roles/Titles
        # - Modules/Teams
        
        lines = text.split('\n')
        current_module = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a module header
            if self._is_module_header(line):
                current_module = self._extract_module_name(line)
                if current_module not in self.contacts_by_module:
                    self.contacts_by_module[current_module] = []
                continue
            
            # Try to extract contact information
            contact = self._extract_contact_from_line(line)
            if contact and current_module:
                contact['module'] = current_module
                self.contacts.append(contact)
                self.contacts_by_module[current_module].append(contact)
    
    def _is_module_header(self, line: str) -> bool:
        """Check if line is a module header"""
        # Common patterns for module headers
        patterns = [
            r'Module:',
            r'Team:',
            r'EDI',
            r'Vessel',
            r'Container',
            r'Database',
            r'Infrastructure',
            r'Management'
        ]
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns)
    
    def _extract_module_name(self, line: str) -> str:
        """Extract module name from header line"""
        # Remove common prefixes
        line = re.sub(r'^(Module|Team):\s*', '', line, flags=re.IGNORECASE)
        return line.strip()
    
    def _extract_contact_from_line(self, line: str) -> Optional[Dict]:
        """
        Extract contact information from a line
        
        Args:
            line: Text line to parse
            
        Returns:
            Contact dictionary or None
        """
        contact = {}
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
        if email_match:
            contact['email'] = email_match.group()
        
        # Extract phone number (Singapore format)
        phone_match = re.search(r'\+65\s*\d{4}\s*\d{4}', line)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        # If we found email, try to extract name and role
        if 'email' in contact:
            # Name is usually before email
            name_part = line.split(contact['email'])[0].strip()
            
            # Role indicators
            role_indicators = ['Lead', 'Engineer', 'Specialist', 'Manager', 'Owner', 'DBA', 'L3']
            
            # Try to split name and role
            for indicator in role_indicators:
                if indicator in name_part:
                    parts = name_part.split(indicator)
                    if len(parts) == 2:
                        contact['name'] = parts[0].strip(' -:')
                        contact['role'] = (parts[1] + ' ' + indicator).strip()
                        break
            
            # If role not found, check common patterns
            if 'role' not in contact:
                # Check for patterns like "Name (Role)" or "Name - Role"
                role_match = re.search(r'[\(\-]\s*([^)]+)[\)]?', name_part)
                if role_match:
                    contact['role'] = role_match.group(1).strip()
                    contact['name'] = name_part.split(role_match.group(0))[0].strip()
                else:
                    contact['name'] = name_part
                    contact['role'] = 'Unknown'
        
        return contact if 'email' in contact else None
    
    def get_contacts_by_module(self, module: str) -> List[Dict]:
        """
        Get contacts for a specific module
        
        Args:
            module: Module name (EDI, Vessel, Container, etc.)
            
        Returns:
            List of contacts for that module
        """
        # Flexible matching
        for key in self.contacts_by_module.keys():
            if module.lower() in key.lower():
                return self.contacts_by_module[key]
        return []
    
    def get_contacts_by_role(self, role: str) -> List[Dict]:
        """
        Get contacts by role (L3 Engineer, Team Lead, etc.)
        
        Args:
            role: Role to search for
            
        Returns:
            List of matching contacts
        """
        return [
            contact for contact in self.contacts
            if role.lower() in contact.get('role', '').lower()
        ]
    
    def route_incident(self, module: str, severity: str = 'MEDIUM') -> List[Dict]:
        """
        Route incident to appropriate contacts
        
        Args:
            module: Affected module
            severity: Incident severity (LOW, MEDIUM, HIGH, CRITICAL)
            
        Returns:
            Prioritized list of contacts
        """
        contacts = []
        
        # Get module contacts
        module_contacts = self.get_contacts_by_module(module)
        contacts.extend(module_contacts)
        
        # Add management for high severity
        if severity in ['HIGH', 'CRITICAL']:
            mgmt_contacts = self.get_contacts_by_module('Management')
            contacts.extend(mgmt_contacts)
        
        # Prioritize by role
        priority_order = ['L3 Engineer', 'Engineer', 'Lead', 'Specialist', 'Owner', 'Manager']
        
        def get_priority(contact):
            role = contact.get('role', '').lower()
            for i, priority_role in enumerate(priority_order):
                if priority_role.lower() in role:
                    return i
            return 999
        
        contacts.sort(key=get_priority)
        
        return contacts
    
    def get_all_contacts(self) -> List[Dict]:
        """Get all contacts"""
        return self.contacts
    
    def get_all_modules(self) -> List[str]:
        """Get list of all modules"""
        return list(self.contacts_by_module.keys())