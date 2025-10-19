"""
Test with Real Test Case 2 - Complete End-to-End Flow
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analyzers import IncidentParser, ContextGatherer, AIAnalyzer
import json


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_complete_flow():
    """Test complete incident resolution flow"""
    
    # Test Case 2
    incident_text = """
Test Case 3 (SMS Received on Duty Phone) 
Alert: SMS INC-154599  
Issue: EDI message REF-IFT-0007 stuck in ERROR status (Sender: LINE-PSA, 
Recipient: PSA-TOS, State: No acknowledgment sent, ack_at is NULL).
"""
    
    print_section("TEST CASE 2: Vessel Advice Creation Error")
    print("\nIncident Text:")
    print(incident_text)
    
    # Step 1: Parse Incident
    print_section("STEP 1: Parse Incident")
    parser = IncidentParser()
    parsed_incident = parser.parse(incident_text)
    
    print("\n📋 Parsed Incident:")
    print(f"   Type: {parsed_incident['incident_type']}")
    print(f"   Module: {parsed_incident['module']}")
    print(f"   Severity: {parsed_incident['severity']}")
    print(f"\n   Entities Found:")
    for entity_type, values in parsed_incident['entities'].items():
        print(f"   - {entity_type}: {', '.join(values)}")
    print(f"\n   Keywords: {', '.join(parsed_incident['keywords'][:10])}")
    
    # Step 2: Gather Context
    print_section("STEP 2: Gather Context")
    gatherer = ContextGatherer()
    context = gatherer.gather(parsed_incident)
    
    print("\n📊 Context Summary:")
    print(f"   Logs: {context['logs']['summary']}")
    print(f"   Historical Cases: {context['historical_cases']['summary']}")
    print(f"   Knowledge Base: {context['knowledge_base']['summary']}")
    print(f"   Escalation Contacts: {context['escalation_contacts']['summary']}")
    
    # Show log details if found
    if context['logs']['results']:
        print("\n   📄 Log Entries Found:")
        for service, entries in context['logs']['results'].items():
            print(f"      {service}: {len(entries)} entries")
            if entries:
                # Show first error or first entry
                sample = entries[0]
                print(f"         Sample: [{sample['level']}] {sample['message'][:80]}...")
    
    # Show similar cases
    if context['historical_cases']['similar_cases']:
        print("\n   📚 Similar Historical Cases:")
        for i, case_match in enumerate(context['historical_cases']['similar_cases'][:3], 1):
            case = case_match['case']
            print(f"\n      Case {i} (Similarity: {case_match['similarity']:.0%}):")
            print(f"      Module: {case.get('Module', 'N/A')}")
            problem = case.get('Problem Statements', 'N/A')
            print(f"      Problem: {problem[:100]}...")
            solution = case.get('Solution', 'N/A')
            print(f"      Solution: {solution[:100]}...")
    
    # Show escalation contacts
    if context['escalation_contacts']['contacts']:
        print("\n   👥 Escalation Contacts:")
        for contact in context['escalation_contacts']['contacts'][:3]:
            print(f"      - {contact.get('name', 'Unknown')} ({contact.get('role', 'Unknown')})")
            print(f"        Email: {contact.get('email', 'N/A')}")
    
    # Step 3: AI Analysis
    print_section("STEP 3: AI Analysis")
    print("\n🤖 Sending to AI for analysis...")
    
    analyzer = AIAnalyzer()
    analysis = analyzer.analyze_incident(parsed_incident, context)
    
    print("\n✅ AI Analysis Results:")
    print("\n📍 Root Cause:")
    print(analysis.get('root_cause', 'N/A'))
    
    print("\n💥 Impact:")
    print(analysis.get('impact', 'N/A'))
    
    print("\n🔍 Evidence:")
    print(analysis.get('evidence', 'N/A'))
    
    print(f"\n🎯 Confidence: {analysis.get('confidence', 'N/A')}")
    
    # Step 4: Generate Remediation Plan
    print_section("STEP 4: Generate Remediation Plan")
    print("\n🔧 Generating remediation plan...")
    
    remediation = analyzer.generate_remediation_plan(parsed_incident, context, analysis)
    
    print("\n✅ Remediation Plan:")
    print("\n1️⃣ Pre-checks:")
    print(remediation.get('pre_checks', 'N/A')[:500])
    
    print("\n2️⃣ Remediation Steps:")
    print(remediation.get('steps', 'N/A')[:800])
    
    print("\n3️⃣ Verification:")
    print(remediation.get('verification', 'N/A')[:400])
    
    # Step 5: Generate Escalation Summaries
    print_section("STEP 5: Generate Escalation Summaries")
    
    # L3 Technical Summary
    print("\n📤 L3 Engineering Escalation:")
    print("-" * 70)
    l3_summary = analyzer.generate_escalation_summary(
        parsed_incident, analysis, remediation, 'L3'
    )
    print(l3_summary)
    
    # Management Summary
    print("\n📤 Management Escalation:")
    print("-" * 70)
    mgmt_summary = analyzer.generate_escalation_summary(
        parsed_incident, analysis, remediation, 'management'
    )
    print(mgmt_summary)
    
    # Final Summary
    print_section("COMPLETE - TEST CASE 2 RESULTS")
    print("\n✅ All steps completed successfully!")
    print("\nSummary:")
    print(f"   ✓ Incident parsed: {parsed_incident['incident_type']}")
    print(f"   ✓ Context gathered: {len(context['logs']['results'])} services, {len(context['historical_cases']['similar_cases'])} cases")
    print(f"   ✓ AI analysis: {analysis.get('confidence', 'N/A')} confidence")
    print(f"   ✓ Remediation plan: Generated")
    print(f"   ✓ Escalation summaries: L3 + Management")
    
    print("\n🎉 Test Case 2 completed successfully!")
    
    return True


if __name__ == "__main__":
    try:
        test_complete_flow()
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)