"""
Parser for Application Log files
Searches and analyzes log entries for incidents
"""
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ApplicationLogParser:
    """Parse and search application logs"""
    
    def __init__(self, log_files: Dict[str, Path]):
        """
        Initialize parser with log file paths
        
        Args:
            log_files: Dictionary mapping service names to file paths
        """
        self.log_files = log_files
        self.logs_cache = {}
        self._load_all_logs()
    
    def _load_all_logs(self):
        """Load all log files into memory"""
        for service_name, file_path in self.log_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.logs_cache[service_name] = f.readlines()
                print(f"✓ Loaded {service_name}: {len(self.logs_cache[service_name])} lines")
            except Exception as e:
                print(f"✗ Failed to load {service_name}: {str(e)}")
                self.logs_cache[service_name] = []
    
    def search_logs(self, search_terms: List[str]) -> Dict[str, List[Dict]]:
        """
        Search all logs for specific terms
        
        Args:
            search_terms: List of terms to search for (container numbers, vessel names, etc.)
            
        Returns:
            Dictionary mapping service names to matching log entries
        """
        results = {}
        
        for service_name, log_lines in self.logs_cache.items():
            matches = []
            
            for line_num, line in enumerate(log_lines, 1):
                # Check if any search term is in this line
                if any(term in line for term in search_terms):
                    parsed_entry = self._parse_log_line(line, line_num)
                    if parsed_entry:
                        matches.append(parsed_entry)
            
            if matches:
                results[service_name] = matches
        
        return results
    
    def _parse_log_line(self, line: str, line_num: int) -> Optional[Dict]:
        """
        Parse a single log line into structured format
        
        Args:
            line: Log line text
            line_num: Line number in file
            
        Returns:
            Parsed log entry or None
        """
        # Log format: 2025-10-09T08:25:33.050Z INFO api-event-service Boot version=1.0.0
        
        # Extract timestamp
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)', line)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        
        # Extract log level
        level_match = re.search(r'\s(DEBUG|INFO|WARN|ERROR)\s', line)
        level = level_match.group(1) if level_match else 'UNKNOWN'
        
        # Extract service name (component)
        service_match = re.search(r'(INFO|ERROR|WARN|DEBUG)\s+(\S+)\s', line)
        component = service_match.group(2) if service_match else 'unknown'
        
        # Extract message (everything after the component)
        if service_match:
            message_start = service_match.end()
            message = line[message_start:].strip()
        else:
            message = line.strip()
        
        return {
            'line_num': line_num,
            'timestamp': timestamp,
            'level': level,
            'component': component,
            'message': message,
            'raw': line.strip()
        }
    
    def get_errors_only(self, search_terms: List[str]) -> Dict[str, List[Dict]]:
        """
        Get only ERROR level logs matching search terms
        
        Args:
            search_terms: Terms to search for
            
        Returns:
            Dictionary of error logs by service
        """
        all_results = self.search_logs(search_terms)
        
        # Filter only errors
        errors = {}
        for service, entries in all_results.items():
            error_entries = [e for e in entries if e['level'] == 'ERROR']
            if error_entries:
                errors[service] = error_entries
        
        return errors
    
    def get_warnings_only(self, search_terms: List[str]) -> Dict[str, List[Dict]]:
        """
        Get only WARN level logs matching search terms
        
        Args:
            search_terms: Terms to search for
            
        Returns:
            Dictionary of warning logs by service
        """
        all_results = self.search_logs(search_terms)
        
        # Filter only warnings
        warnings = {}
        for service, entries in all_results.items():
            warn_entries = [e for e in entries if e['level'] == 'WARN']
            if warn_entries:
                warnings[service] = warn_entries
        
        return warnings
    
    def build_timeline(self, search_terms: List[str]) -> List[Dict]:
        """
        Build chronological timeline of events
        
        Args:
            search_terms: Terms to search for
            
        Returns:
            Sorted list of log entries by timestamp
        """
        all_results = self.search_logs(search_terms)
        
        # Flatten all entries
        timeline = []
        for service, entries in all_results.items():
            for entry in entries:
                entry['service'] = service
                timeline.append(entry)
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '')
        
        return timeline
    
    def get_affected_services(self, search_terms: List[str]) -> List[str]:
        """
        Get list of services that have logs matching search terms
        
        Args:
            search_terms: Terms to search for
            
        Returns:
            List of affected service names
        """
        results = self.search_logs(search_terms)
        return list(results.keys())
    
    def analyze_patterns(self, search_terms: List[str]) -> Dict:
        """
        Analyze patterns in matching logs
        
        Args:
            search_terms: Terms to search for
            
        Returns:
            Dictionary with analysis results
        """
        results = self.search_logs(search_terms)
        
        total_entries = sum(len(entries) for entries in results.values())
        
        # Count by level
        level_counts = {}
        for entries in results.values():
            for entry in entries:
                level = entry['level']
                level_counts[level] = level_counts.get(level, 0) + 1
        
        # Count by service
        service_counts = {service: len(entries) for service, entries in results.items()}
        
        # Get error messages
        error_messages = []
        for entries in results.values():
            for entry in entries:
                if entry['level'] == 'ERROR':
                    error_messages.append(entry['message'])
        
        return {
            'total_entries': total_entries,
            'affected_services': list(results.keys()),
            'level_counts': level_counts,
            'service_counts': service_counts,
            'unique_errors': list(set(error_messages)),
            'error_count': level_counts.get('ERROR', 0),
            'warning_count': level_counts.get('WARN', 0)
        }
    
    def extract_entities(self, search_terms: List[str]) -> Dict[str, List[str]]:
        """
        Extract entities (container numbers, vessel names, etc.) from logs
        
        Args:
            search_terms: Initial search terms
            
        Returns:
            Dictionary of entity types to values found
        """
        results = self.search_logs(search_terms)
        
        entities = {
            'containers': set(),
            'vessels': set(),
            'error_codes': set(),
            'reference_ids': set()
        }
        
        for entries in results.values():
            for entry in entries:
                message = entry['message']
                
                # Extract container numbers (format: XXXX1234567)
                container_matches = re.findall(r'\b[A-Z]{4}\d{7}\b', message)
                entities['containers'].update(container_matches)
                
                # Extract vessel names (format: MV VESSEL NAME)
                vessel_matches = re.findall(r'MV\s+[A-Z\s]+(?:/\d+[A-Z]?)?', message)
                entities['vessels'].update(vessel_matches)
                
                # Extract error codes
                error_matches = re.findall(r'[A-Z]+_ERR_\d+', message)
                entities['error_codes'].update(error_matches)
                
                # Extract reference IDs
                ref_matches = re.findall(r'REF-[A-Z]+-[^\s]+', message)
                entities['reference_ids'].update(ref_matches)
        
        # Convert sets to lists
        return {k: list(v) for k, v in entities.items()}
    
    def get_context_around_error(self, search_terms: List[str], context_lines: int = 5) -> Dict[str, List[Dict]]:
        """
        Get context around error lines (lines before and after)
        
        Args:
            search_terms: Terms to search for
            context_lines: Number of lines before/after to include
            
        Returns:
            Dictionary with errors and their context
        """
        results_with_context = {}
        
        for service_name, log_lines in self.logs_cache.items():
            errors_with_context = []
            
            for line_num, line in enumerate(log_lines, 1):
                # Check if this is an error line matching search terms
                if 'ERROR' in line and any(term in line for term in search_terms):
                    # Get context
                    start = max(0, line_num - context_lines - 1)
                    end = min(len(log_lines), line_num + context_lines)
                    
                    context = {
                        'error_line': self._parse_log_line(line, line_num),
                        'before': [self._parse_log_line(log_lines[i], i+1) for i in range(start, line_num-1)],
                        'after': [self._parse_log_line(log_lines[i], i+1) for i in range(line_num, end)]
                    }
                    
                    errors_with_context.append(context)
            
            if errors_with_context:
                results_with_context[service_name] = errors_with_context
        
        return results_with_context
    
    def format_log_entry(self, entry: Dict) -> str:
        """
        Format a log entry for display
        
        Args:
            entry: Parsed log entry
            
        Returns:
            Formatted string
        """
        return f"[{entry['timestamp']}] {entry['level']} {entry['component']}: {entry['message']}"
    
    def get_summary(self, search_terms: List[str]) -> str:
        """
        Get formatted summary of search results
        
        Args:
            search_terms: Terms to search for
            
        Returns:
            Formatted summary string
        """
        analysis = self.analyze_patterns(search_terms)
        
        summary = f"""
Log Search Summary
==================
Search Terms: {', '.join(search_terms)}
Total Entries Found: {analysis['total_entries']}

Affected Services: {', '.join(analysis['affected_services'])}

Log Levels:
- ERROR: {analysis['error_count']}
- WARN: {analysis['warning_count']}
- INFO: {analysis['level_counts'].get('INFO', 0)}
- DEBUG: {analysis['level_counts'].get('DEBUG', 0)}

Service Breakdown:
{chr(10).join(f"- {service}: {count} entries" for service, count in analysis['service_counts'].items())}
"""
        
        if analysis['unique_errors']:
            summary += f"\n\nUnique Error Messages:\n"
            for i, error in enumerate(analysis['unique_errors'][:5], 1):
                summary += f"{i}. {error}\n"
        
        return summary