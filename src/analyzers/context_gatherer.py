"""
Context Gatherer - Searches all data sources for relevant information
"""
from typing import Dict, List
from parsers import (
    CaseLogParser,
    KnowledgeBaseParser,
    EscalationContactsParser,
    ApplicationLogParser
)
from utils.config import (
    CASE_LOG_FILE,
    KNOWLEDGE_BASE_FILE,
    ESCALATION_CONTACTS_FILE,
    LOG_FILES
)


class ContextGatherer:
    """Gather relevant context from all data sources"""
    
    def __init__(self):
        """Initialize all parsers"""
        print("🔄 Initializing Context Gatherer...")
        
        self.case_log_parser = CaseLogParser(CASE_LOG_FILE)
        self.kb_parser = KnowledgeBaseParser(KNOWLEDGE_BASE_FILE)
        self.contacts_parser = EscalationContactsParser(ESCALATION_CONTACTS_FILE)
        self.log_parser = ApplicationLogParser(LOG_FILES)
        
        print("✅ Context Gatherer ready")
    
    def gather(self, parsed_incident: Dict) -> Dict:
        """
        Gather all relevant context for an incident
        
        Args:
            parsed_incident: Parsed incident from IncidentParser
            
        Returns:
            Dictionary with all gathered context
        """
        print("\n🔍 Gathering context from all sources...")
        
        # Extract search terms
        search_terms = self._get_search_terms(parsed_incident)
        keywords = parsed_incident.get('keywords', [])
        module = parsed_incident.get('module', 'General')
        severity = parsed_incident.get('severity', 'MEDIUM')
        
        context = {
            'search_terms': search_terms,
            'logs': self._search_logs(search_terms),
            'historical_cases': self._search_cases(keywords, module),
            'knowledge_base': self._search_kb(keywords),
            'escalation_contacts': self._get_escalation_contacts(module, severity),
            'log_analysis': None,  # Will be filled by log analysis
        }
        
        # Analyze log patterns
        if context['logs']['results']:
            context['log_analysis'] = self._analyze_logs(context['logs'])
        
        print(f"✅ Context gathered: {self._get_context_summary(context)}")
        
        return context
    
    def _get_search_terms(self, parsed_incident: Dict) -> List[str]:
        """Extract search terms from parsed incident"""
        search_terms = []
        
        # Get all entity values
        entities = parsed_incident.get('entities', {})
        for entity_list in entities.values():
            search_terms.extend(entity_list)
        
        # Remove duplicates
        return list(set(search_terms))
    
    def _search_logs(self, search_terms: List[str]) -> Dict:
        """
        Search application logs
        
        Args:
            search_terms: Terms to search for
            
        Returns:
            Dictionary with log search results
        """
        if not search_terms:
            return {'results': {}, 'summary': 'No search terms'}
        
        print(f"   📄 Searching logs for: {', '.join(search_terms[:3])}...")
        
        # Search all logs
        results = self.log_parser.search_logs(search_terms)
        
        # Get errors only
        errors = self.log_parser.get_errors_only(search_terms)
        
        # Get warnings
        warnings = self.log_parser.get_warnings_only(search_terms)
        
        # Build timeline
        timeline = self.log_parser.build_timeline(search_terms)
        
        # Get affected services
        affected_services = self.log_parser.get_affected_services(search_terms)
        
        # Analyze patterns
        analysis = self.log_parser.analyze_patterns(search_terms)
        
        total_entries = sum(len(entries) for entries in results.values())
        print(f"   ✓ Found {total_entries} log entries across {len(results)} services")
        
        return {
            'results': results,
            'errors': errors,
            'warnings': warnings,
            'timeline': timeline[:20],  # Top 20 chronological events
            'affected_services': affected_services,
            'analysis': analysis,
            'summary': f"{total_entries} entries in {len(results)} services"
        }
    
    def _search_cases(self, keywords: List[str], module: str) -> Dict:
        """
        Search historical cases
        
        Args:
            keywords: Keywords to search for
            module: Module name
            
        Returns:
            Dictionary with case search results
        """
        print(f"   📚 Searching historical cases...")
        
        # Search by keywords
        similar_cases = self.case_log_parser.search_similar(keywords, top_n=5)
        
        # Search by module
        module_cases = self.case_log_parser.search_by_module(module)
        
        print(f"   ✓ Found {len(similar_cases)} similar cases")
        
        return {
            'similar_cases': similar_cases,
            'module_cases': module_cases[:5],  # Top 5
            'total_similar': len(similar_cases),
            'summary': f"{len(similar_cases)} similar cases found"
        }
    
    def _search_kb(self, keywords: List[str]) -> Dict:
        """
        Search knowledge base
        
        Args:
            keywords: Keywords to search for
            
        Returns:
            Dictionary with KB search results
        """
        print(f"   📖 Searching knowledge base...")
        
        # Search by keywords
        articles = self.kb_parser.search_by_keywords(keywords)
        
        # Search for procedures
        procedures = self.kb_parser.search_procedures(keywords)
        
        print(f"   ✓ Found {len(articles)} relevant articles")
        
        return {
            'articles': articles[:5],  # Top 5
            'procedures': procedures[:3],  # Top 3
            'total_articles': len(articles),
            'summary': f"{len(articles)} articles found"
        }
    
    def _get_escalation_contacts(self, module: str, severity: str) -> Dict:
        """
        Get relevant escalation contacts
        
        Args:
            module: Module name
            severity: Severity level
            
        Returns:
            Dictionary with escalation contacts
        """
        print(f"   👥 Finding escalation contacts for {module}/{severity}...")
        
        # Route incident to appropriate contacts
        contacts = self.contacts_parser.route_incident(module, severity)
        
        print(f"   ✓ Found {len(contacts)} contacts")
        
        return {
            'contacts': contacts,
            'total': len(contacts),
            'summary': f"{len(contacts)} contacts for {module}"
        }
    
    def _analyze_logs(self, log_context: Dict) -> Dict:
        """
        Analyze log patterns and extract insights
        
        Args:
            log_context: Log search results
            
        Returns:
            Dictionary with log analysis
        """
        analysis = log_context.get('analysis', {})
        errors = log_context.get('errors', {})
        timeline = log_context.get('timeline', [])
        
        # Extract key error messages
        error_messages = []
        for service, error_entries in errors.items():
            for entry in error_entries[:3]:  # Top 3 per service
                error_messages.append({
                    'service': service,
                    'timestamp': entry.get('timestamp'),
                    'message': entry.get('message', '')[:200]  # Truncate
                })
        
        # Identify patterns
        patterns = []
        if analysis.get('error_count', 0) > 5:
            patterns.append('Multiple errors detected')
        
        if len(log_context.get('affected_services', [])) > 2:
            patterns.append('Multiple services affected')
        
        if timeline:
            # Check if errors clustered in time
            if len(timeline) > 3:
                patterns.append('Errors occurred in sequence')
        
        return {
            'error_messages': error_messages,
            'patterns': patterns,
            'error_count': analysis.get('error_count', 0),
            'warning_count': analysis.get('warning_count', 0),
            'affected_services': log_context.get('affected_services', [])
        }
    
    def _get_context_summary(self, context: Dict) -> str:
        """Generate summary of gathered context"""
        summaries = []
        
        if context['logs']['results']:
            summaries.append(context['logs']['summary'])
        
        if context['historical_cases']['similar_cases']:
            summaries.append(context['historical_cases']['summary'])
        
        if context['knowledge_base']['articles']:
            summaries.append(context['knowledge_base']['summary'])
        
        if context['escalation_contacts']['contacts']:
            summaries.append(context['escalation_contacts']['summary'])
        
        return ', '.join(summaries) if summaries else 'No context found'
    
    def format_context_for_ai(self, context: Dict) -> str:
        """
        Format gathered context for AI prompt
        
        Args:
            context: Gathered context dictionary
            
        Returns:
            Formatted string for AI prompt
        """
        formatted = "# Context Information\n\n"
        
        # Log Analysis
        if context['logs']['results']:
            formatted += "## Application Logs\n"
            log_analysis = context.get('log_analysis', {})
            
            formatted += f"- Total entries: {context['logs']['analysis'].get('total_entries', 0)}\n"
            formatted += f"- Errors: {log_analysis.get('error_count', 0)}\n"
            formatted += f"- Affected services: {', '.join(log_analysis.get('affected_services', []))}\n"
            
            # Include top error messages
            error_messages = log_analysis.get('error_messages', [])
            if error_messages:
                formatted += "\n### Key Error Messages:\n"
                for i, error in enumerate(error_messages[:3], 1):
                    formatted += f"{i}. [{error['service']}] {error['message']}\n"
            
            formatted += "\n"
        
        # Historical Cases
        if context['historical_cases']['similar_cases']:
            formatted += "## Similar Historical Cases\n"
            for i, case_match in enumerate(context['historical_cases']['similar_cases'][:3], 1):
                case = case_match['case']
                formatted += f"\n### Case {i} (Similarity: {case_match['similarity']:.0%})\n"
                formatted += f"Module: {case.get('Module', 'N/A')}\n"
                formatted += f"Problem: {case.get('Problem Statements', 'N/A')[:200]}...\n"
                formatted += f"Solution: {case.get('Solution', 'N/A')[:200]}...\n"
            
            formatted += "\n"
        
        # Knowledge Base
        if context['knowledge_base']['articles']:
            formatted += "## Knowledge Base Articles\n"
            for i, article in enumerate(context['knowledge_base']['articles'][:2], 1):
                formatted += f"\n### Article {i}: {article['section_title']}\n"
                formatted += f"{article['content'][:300]}...\n"
            
            formatted += "\n"
        
        return formatted