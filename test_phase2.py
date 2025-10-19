"""
Test Phase 2 - Core Analyzers
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analyzers import IncidentParser, ContextGatherer, AIAnalyzer


def test_incident_parser():
    """Test IncidentParser"""
    print("=" * 60)
    print("TEST 1: Incident Parser")
    print("=" * 60)
    
    sample_incident = """
    RE: Email ALR-861600 | CMAU0000020 - Duplicate Container information received
    
    Hi Team,
    Please assist in checking container CMAU0000020. Customer is seeing 2
    identical containers information.
    
    Thanks,
    Kenny
    """
    
    parser = IncidentParser()
    parsed = parser.parse(sample_incident)
    
    print("\n✅ Incident parsed successfully!")
    print(f"\nType: {parsed['incident_type']}")
    print(f"Module: {parsed['module']}")
    print(f"Severity: {parsed['severity']}")
    print(f"Entities found: {list(parsed['entities'].keys())}")
    print(f"Keywords: {parsed['keywords'][:5]}")
    
    return True


def test_context_gatherer():
    """Test ContextGatherer"""
    print("\n" + "=" * 60)
    print("TEST 2: Context Gatherer")
    print("=" * 60)
    
    # Parse incident first
    sample_incident = """
    Container CMAU0000020 showing duplicate entries.
    """
    
    parser = IncidentParser()
    parsed = parser.parse(sample_incident)
    
    # Gather context
    gatherer = ContextGatherer()
    context = gatherer.gather(parsed)
    
    print("\n✅ Context gathered successfully!")
    print(f"\nLogs: {context['logs']['summary']}")
    print(f"Cases: {context['historical_cases']['summary']}")
    print(f"KB: {context['knowledge_base']['summary']}")
    print(f"Contacts: {context['escalation_contacts']['summary']}")
    
    return True


def test_ai_analyzer():
    """Test AIAnalyzer"""
    print("\n" + "=" * 60)
    print("TEST 3: AI Analyzer")
    print("=" * 60)
    
    analyzer = AIAnalyzer()
    
    # Test connection
    print("\nTesting AI connection...")
    if analyzer.test_connection():
        print("✅ AI connection successful!")
        return True
    else:
        print("❌ AI connection failed")
        return False


def main():
    """Run all Phase 2 tests"""
    print("\n🚀 PHASE 2 ANALYZER TESTS\n")
    
    tests = [
        ("Incident Parser", test_incident_parser),
        ("Context Gatherer", test_context_gatherer),
        ("AI Analyzer", test_ai_analyzer),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, r in results if r)
    print(f"\nResults: {passed}/{len(results)} passed")
    
    if passed == len(results):
        print("\n🎉 Phase 2 complete! Ready for Phase 3!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")


if __name__ == "__main__":
    main()