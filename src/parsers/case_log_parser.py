"""
Parser for Case Log Excel file
Extracts historical incidents and their solutions
"""
import pandas as pd
from typing import List, Dict, Optional


class CaseLogParser:
    """Parse and search historical case log"""
    
    def __init__(self, file_path: str):
        """
        Initialize parser with Excel file path
        
        Args:
            file_path: Path to Case Log.xlsx
        """
        self.file_path = file_path
        self.cases = None
        self._load_cases()
    
    def _load_cases(self):
        """Load cases from Excel file"""
        try:
            df = pd.read_excel(self.file_path)
            
            # Convert to list of dictionaries for easier processing
            self.cases = df.to_dict('records')
            
            print(f"✓ Loaded {len(self.cases)} historical cases")
            
        except Exception as e:
            raise Exception(f"Failed to load case log: {str(e)}")
    
    def get_all_cases(self) -> List[Dict]:
        """
        Get all cases
        
        Returns:
            List of all case dictionaries
        """
        return self.cases
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """
        Search cases by keywords in problem statement and solution
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of matching cases with similarity scores
        """
        if not keywords:
            return []
        
        matching_cases = []
        
        for case in self.cases:
            # Combine problem and solution text for searching
            problem_text = str(case.get('Problem Statements', '')).lower()
            solution_text = str(case.get('Solution', '')).lower()
            combined_text = f"{problem_text} {solution_text}"
            
            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword.lower() in combined_text)
            
            if matches > 0:
                similarity_score = matches / len(keywords)
                matching_cases.append({
                    'case': case,
                    'similarity': similarity_score,
                    'matched_keywords': [k for k in keywords if k.lower() in combined_text]
                })
        
        # Sort by similarity score
        matching_cases.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matching_cases
    
    def search_by_module(self, module: str) -> List[Dict]:
        """
        Search cases by module (EDI/API, Vessel, Container, etc.)
        
        Args:
            module: Module name to search for
            
        Returns:
            List of cases from that module
        """
        return [
            case for case in self.cases
            if str(case.get('Module', '')).lower() == module.lower()
        ]
    
    def search_similar(self, incident_keywords: List[str], top_n: int = 3) -> List[Dict]:
        """
        Find most similar historical cases
        
        Args:
            incident_keywords: Keywords from current incident
            top_n: Number of top matches to return
            
        Returns:
            Top N most similar cases
        """
        matches = self.search_by_keywords(incident_keywords)
        return matches[:top_n]
    
    def get_case_summary(self, case: Dict) -> str:
        """
        Get formatted summary of a case
        
        Args:
            case: Case dictionary
            
        Returns:
            Formatted string summary
        """
        return f"""
Module: {case.get('Module', 'N/A')}
Problem: {case.get('Problem Statements', 'N/A')}
Solution: {case.get('Solution', 'N/A')}
SOP: {case.get('SOP', 'N/A')}
"""
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the case log
        
        Returns:
            Dictionary with statistics
        """
        if not self.cases:
            return {}
        
        df = pd.DataFrame(self.cases)
        
        return {
            'total_cases': len(self.cases),
            'modules': df['Module'].value_counts().to_dict() if 'Module' in df.columns else {},
            'edi_cases': len(df[df['EDI?'] == 'Yes']) if 'EDI?' in df.columns else 0,
        }