"""
AI Analyzer - Uses Azure OpenAI to analyze incidents and generate solutions
"""
import json
from typing import Dict, Optional
from openai import AzureOpenAI
from utils.config import AZURE_OPENAI_CONFIG


class AIAnalyzer:
    """Analyze incidents using Azure OpenAI"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_CONFIG['api_key'],
            api_version=AZURE_OPENAI_CONFIG['api_version'],
            azure_endpoint=AZURE_OPENAI_CONFIG['endpoint'],
            timeout=60.0
        )
        self.deployment = AZURE_OPENAI_CONFIG['deployment']
        print("✅ AI Analyzer initialized")
    
    def analyze_incident(
        self,
        parsed_incident: Dict,
        context: Dict
    ) -> Dict:
        """
        Analyze incident using AI with gathered context
        
        Args:
            parsed_incident: Parsed incident from IncidentParser
            context: Gathered context from ContextGatherer
            
        Returns:
            Dictionary with AI analysis results
        """
        print("\n🤖 Analyzing incident with AI...")
        
        # Build prompt
        prompt = self._build_analysis_prompt(parsed_incident, context)
        
        # Get AI analysis
        analysis = self._call_ai(prompt, max_tokens=1500)
        
        # Parse response
        parsed_analysis = self._parse_analysis_response(analysis)
        
        print("✅ AI analysis complete")
        
        return parsed_analysis
    
    def generate_remediation_plan(
        self,
        parsed_incident: Dict,
        context: Dict,
        analysis: Dict
    ) -> Dict:
        """
        Generate detailed remediation plan
        
        Args:
            parsed_incident: Parsed incident
            context: Gathered context
            analysis: AI analysis results
            
        Returns:
            Dictionary with remediation plan
        """
        print("🔧 Generating remediation plan...")
        
        prompt = self._build_remediation_prompt(parsed_incident, context, analysis)
        
        remediation = self._call_ai(prompt, max_tokens=2000)
        
        parsed_remediation = self._parse_remediation_response(remediation)
        
        print("✅ Remediation plan generated")
        
        return parsed_remediation
    
    def generate_escalation_summary(
        self,
        parsed_incident: Dict,
        analysis: Dict,
        remediation: Dict,
        recipient_type: str = 'L3'
    ) -> str:
        """
        Generate escalation summary
        
        Args:
            parsed_incident: Parsed incident
            analysis: AI analysis
            remediation: Remediation plan
            recipient_type: 'L3' for technical or 'management' for business
            
        Returns:
            Formatted escalation summary
        """
        print(f"📤 Generating {recipient_type} escalation summary...")
        
        prompt = self._build_escalation_prompt(
            parsed_incident,
            analysis,
            remediation,
            recipient_type
        )
        
        summary = self._call_ai(prompt, max_tokens=1000)
        
        print("✅ Escalation summary generated")
        
        return summary
    
    def _build_analysis_prompt(self, parsed_incident: Dict, context: Dict) -> str:
        """Build prompt for incident analysis"""
        
        # Format context for inclusion
        context_text = self._format_context_for_prompt(context)
        
        prompt = f"""You are an expert incident analyst for PORTNET, Singapore's maritime port community system.

# Incident Details
Type: {parsed_incident.get('incident_type', 'Unknown')}
Module: {parsed_incident.get('module', 'Unknown')}
Severity: {parsed_incident.get('severity', 'MEDIUM')}

Incident Description:
{parsed_incident.get('raw_text', '')}

{context_text}

# Your Task
Analyze this incident and provide:

1. **Root Cause Analysis** (2-3 sentences)
   - What is the underlying cause?
   - Why did it happen?

2. **Impact Assessment** (2-3 sentences)
   - What systems/processes are affected?
   - What is the business impact?

3. **Evidence** (bullet points)
   - Key log entries or data that support your analysis
   - Reference specific error messages or patterns

4. **Confidence Level**
   - HIGH: Clear root cause with strong evidence
   - MEDIUM: Likely cause with supporting evidence
   - LOW: Hypothesis that needs verification

Provide your analysis in a clear, structured format. Be specific and reference the context provided.
"""
        
        return prompt
    
    def _build_remediation_prompt(
        self,
        parsed_incident: Dict,
        context: Dict,
        analysis: Dict
    ) -> str:
        """Build prompt for remediation plan"""
        
        prompt = f"""You are creating a remediation plan for a PORTNET incident.

# Incident
{parsed_incident.get('raw_text', '')}

# Root Cause
{analysis.get('root_cause', 'See analysis')}

# Your Task
Create a detailed, actionable remediation plan:

1. **Pre-checks** (What to verify before starting)
   - Specific queries or checks to run
   - What to look for

2. **Remediation Steps** (Numbered, specific actions)
   - Include exact SQL queries if database changes needed
   - Include specific commands or procedures
   - Each step should be clear and actionable

3. **Expected Outcome** (For each step)
   - What should happen after each step
   - How to verify it worked

4. **Verification Steps** (How to confirm the fix worked)
   - Specific checks to perform
   - Success criteria

5. **Rollback Plan** (If something goes wrong)
   - How to revert changes
   - What to do if fix doesn't work

6. **Monitoring** (What to watch after fix)
   - Logs to monitor
   - Metrics to track
   - How long to monitor

Be very specific. If you recommend a SQL query, write the actual query. If you recommend checking logs, specify which service and what to look for.
"""
        
        return prompt
    
    def _build_escalation_prompt(
        self,
        parsed_incident: Dict,
        analysis: Dict,
        remediation: Dict,
        recipient_type: str
    ) -> str:
        """Build prompt for escalation summary"""
        
        if recipient_type.lower() == 'l3':
            prompt = f"""Create a technical escalation summary for L3 Engineering team.

# Incident
{parsed_incident.get('raw_text', '')}

# Root Cause
{analysis.get('root_cause', '')}

# Remediation Plan
{remediation.get('summary', '')}

Create a concise email suitable for L3 engineers:

Subject: [Clear, specific subject line]

Body:
- Brief incident description (2-3 sentences)
- Root cause (technical details)
- Immediate actions taken/needed
- Technical details (error codes, affected services, log references)
- Recommended fix with technical specifics
- Verification steps
- Any risks or dependencies

Keep it technical, specific, and actionable. Engineers should know exactly what to do after reading this.
"""
        else:  # Management
            prompt = f"""Create a business-focused escalation summary for Management.

# Incident
{parsed_incident.get('raw_text', '')}

# Impact
{analysis.get('impact', '')}

# Status
Root cause identified, resolution in progress.

Create a concise email suitable for management:

Subject: [Clear subject with business impact]

Body:
- What happened (business terms, 2-3 sentences)
- Customer/business impact
- Root cause (non-technical explanation)
- Resolution timeline
- Current status
- Risk mitigation
- Next steps

Focus on business impact and timeline. Avoid technical jargon. Management should understand the business implications and timeline.
"""
        
        return prompt
    
    def _format_context_for_prompt(self, context: Dict) -> str:
        """Format gathered context for AI prompt"""
        
        formatted = "# Context Information\n\n"
        
        # Log Analysis
        if context.get('logs', {}).get('results'):
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
        if context.get('historical_cases', {}).get('similar_cases'):
            formatted += "## Similar Historical Cases\n"
            for i, case_match in enumerate(context['historical_cases']['similar_cases'][:3], 1):
                case = case_match['case']
                formatted += f"\n### Case {i} (Similarity: {case_match['similarity']:.0%})\n"
                formatted += f"Module: {case.get('Module', 'N/A')}\n"
                formatted += f"Problem: {case.get('Problem Statements', 'N/A')[:200]}...\n"
                formatted += f"Solution: {case.get('Solution', 'N/A')[:200]}...\n"
            
            formatted += "\n"
        
        # Knowledge Base
        if context.get('knowledge_base', {}).get('articles'):
            formatted += "## Knowledge Base Articles\n"
            for i, article in enumerate(context['knowledge_base']['articles'][:2], 1):
                formatted += f"\n### Article {i}: {article['section_title']}\n"
                formatted += f"{article['content'][:300]}...\n"
            
            formatted += "\n"
        
        return formatted
    
    def _call_ai(self, prompt: str, max_tokens: int = 1500) -> str:
        """
        Call Azure OpenAI API
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            
        Returns:
            AI response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical analyst for PORTNET maritime operations. Provide clear, actionable analysis and recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ AI call failed: {e}")
            return f"Error: Unable to get AI response. {str(e)}"
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """
        Parse AI analysis response into structured format
        
        Args:
            response: Raw AI response
            
        Returns:
            Structured analysis dictionary
        """
        sections = {
            'root_cause': self._extract_section(response, ['root cause', '1.']),
            'impact': self._extract_section(response, ['impact', '2.']),
            'evidence': self._extract_section(response, ['evidence', '3.']),
            'confidence': self._extract_section(response, ['confidence', '4.']),
            'full_response': response
        }
        
        return sections
    
    def _parse_remediation_response(self, response: str) -> Dict:
        """
        Parse remediation response into structured format
        
        Args:
            response: Raw AI response
            
        Returns:
            Structured remediation dictionary
        """
        sections = {
            'pre_checks': self._extract_section(response, ['pre-check', '1.']),
            'steps': self._extract_section(response, ['remediation step', 'step', '2.']),
            'verification': self._extract_section(response, ['verification', 'verify', '4.']),
            'rollback': self._extract_section(response, ['rollback', '5.']),
            'monitoring': self._extract_section(response, ['monitoring', 'monitor', '6.']),
            'full_response': response,
            'summary': response[:500] + '...' if len(response) > 500 else response
        }
        
        return sections
    
    def _extract_section(self, text: str, markers: list) -> str:
        """
        Extract a section from text based on markers
        
        Args:
            text: Full text
            markers: List of possible section markers
            
        Returns:
            Extracted section or empty string
        """
        text_lower = text.lower()
        
        for marker in markers:
            marker_lower = marker.lower()
            if marker_lower in text_lower:
                start = text_lower.find(marker_lower)
                
                # Find the next section
                next_markers = ['\n#', '\n##', '\n1.', '\n2.', '\n3.', '\n4.', '\n5.', '\n6.']
                end = len(text)
                
                for next_marker in next_markers:
                    pos = text.find(next_marker, start + len(marker))
                    if pos != -1 and pos < end:
                        end = pos
                
                section = text[start:end].strip()
                
                # Remove the marker itself from the beginning
                for m in markers:
                    if section.lower().startswith(m.lower()):
                        section = section[len(m):].strip()
                        break
                
                return section
        
        return ""
    
    def test_connection(self) -> bool:
        """
        Test AI connection
        
        Returns:
            True if connection successful
        """
        try:
            response = self._call_ai("Respond with: Connection successful", max_tokens=50)
            return "successful" in response.lower()
        except:
            return False