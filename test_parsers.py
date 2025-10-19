"""
Test script to verify all parsers work correctly with actual files
Run this before proceeding to Phase 2
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.config import (
    CASE_LOG_FILE,
    KNOWLEDGE_BASE_FILE,
    ESCALATION_CONTACTS_FILE,
    LOG_FILES,
    validate_files
)
from parsers import (
    CaseLogParser,
    KnowledgeBaseParser,
    EscalationContactsParser,
    ApplicationLogParser
)


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_file_existence():
    """Test that all required files exist"""
    print_header("TEST 1: File Existence Check")
    
    try:
        validate_files()
        print("✅ All required files found!")
        return True
    except FileNotFoundError as e:
        print(f"❌ Missing files:\n{e}")
        return False


def test_case_log_parser():
    """Test Case Log Excel parser"""
    print_header("TEST 2: Case Log Parser")
    
    try:
        parser = CaseLogParser(CASE_LOG_FILE)
        
        # Get all cases
        all_cases = parser.get_all_cases()
        print(f"✅ Loaded {len(all_cases)} cases")
        
        # Show first case
        if all_cases:
            print("\n📄 Sample Case:")
            first_case = all_cases[0]
            print(f"   Module: {first_case.get('Module', 'N/A')}")
            print(f"   Problem: {first_case.get('Problem Statements', 'N/A')[:100]}...")
            print(f"   Solution: {first_case.get('Solution', 'N/A')[:100]}...")
        
        # Test search
        print("\n🔍 Testing search functionality...")
        results = parser.search_by_keywords(['duplicate', 'container'])
        print(f"   Found {len(results)} cases matching 'duplicate, container'")
        
        # Show statistics
        stats = parser.get_statistics()
        print("\n📊 Statistics:")
        print(f"   Total Cases: {stats.get('total_cases', 0)}")
        print(f"   EDI Cases: {stats.get('edi_cases', 0)}")
        if stats.get('modules'):
            print(f"   Modules: {', '.join(stats['modules'].keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_base_parser():
    """Test Knowledge Base document parser"""
    print_header("TEST 3: Knowledge Base Parser")
    
    try:
        parser = KnowledgeBaseParser(KNOWLEDGE_BASE_FILE)
        
        # Get content info
        content = parser.get_full_content()
        print(f"✅ Loaded document: {len(content)} characters")
        
        # Show sections
        sections = parser.get_all_sections()
        print(f"\n📑 Found {len(sections)} sections")
        
        if sections:
            print("\n   Section Titles:")
            for i, section in enumerate(sections[:5], 1):
                print(f"   {i}. {section['title']}")
            if len(sections) > 5:
                print(f"   ... and {len(sections) - 5} more")
        
        # Test search
        print("\n🔍 Testing search functionality...")
        results = parser.search_by_keywords(['vessel', 'error'])
        print(f"   Found {len(results)} sections matching 'vessel, error'")
        
        if results:
            print(f"\n   Top match: {results[0]['section_title']}")
            print(f"   Relevance: {results[0]['relevance']:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_escalation_contacts_parser():
    """Test Escalation Contacts PDF parser"""
    print_header("TEST 4: Escalation Contacts Parser")
    
    try:
        parser = EscalationContactsParser(ESCALATION_CONTACTS_FILE)
        
        # Get all contacts
        all_contacts = parser.get_all_contacts()
        print(f"✅ Loaded {len(all_contacts)} contacts")
        
        # Show sample contacts
        if all_contacts:
            print("\n👥 Sample Contacts:")
            for contact in all_contacts[:3]:
                print(f"   • {contact.get('name', 'N/A')} - {contact.get('role', 'N/A')}")
                print(f"     Email: {contact.get('email', 'N/A')}")
                if contact.get('phone'):
                    print(f"     Phone: {contact['phone']}")
                print()
        
        # Show modules
        modules = parser.get_all_modules()
        print(f"📋 Modules found: {len(modules)}")
        if modules:
            for module in modules:
                print(f"   • {module}")
        
        # Test routing
        print("\n🔀 Testing routing functionality...")
        routed = parser.route_incident(module='EDI', severity='HIGH')
        print(f"   Routed to {len(routed)} contacts for EDI/HIGH severity")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_application_log_parser():
    """Test Application Logs parser"""
    print_header("TEST 5: Application Log Parser")
    
    try:
        parser = ApplicationLogParser(LOG_FILES)
        
        print(f"✅ Loaded {len(parser.logs_cache)} log files")
        
        # Show log file info
        print("\n📁 Log Files:")
        for service, lines in parser.logs_cache.items():
            print(f"   • {service}: {len(lines)} lines")
        
        # Test search with a common term
        print("\n🔍 Testing search functionality...")
        print("   Searching for: 'ERROR'")
        
        results = parser.search_logs(['ERROR'])
        total_matches = sum(len(entries) for entries in results.values())
        print(f"   Found {total_matches} error entries across {len(results)} services")
        
        if results:
            print("\n   Services with errors:")
            for service, entries in results.items():
                print(f"   • {service}: {len(entries)} errors")
        
        # Test pattern analysis
        print("\n📊 Testing pattern analysis...")
        analysis = parser.analyze_patterns(['ERROR'])
        print(f"   Total entries: {analysis['total_entries']}")
        print(f"   Error count: {analysis['error_count']}")
        print(f"   Warning count: {analysis['warning_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_scenario():
    """Test a realistic search scenario"""
    print_header("TEST 6: Realistic Search Scenario")
    
    try:
        # Scenario: Search for container-related issues
        print("🎯 Scenario: Searching for container 'CMAU0000020'")
        
        # Search logs
        log_parser = ApplicationLogParser(LOG_FILES)
        log_results = log_parser.search_logs(['CMAU0000020'])
        
        if log_results:
            print(f"\n✅ Found in logs:")
            for service, entries in log_results.items():
                print(f"   • {service}: {len(entries)} entries")
                if entries:
                    # Show first entry
                    first = entries[0]
                    print(f"     Example: [{first['level']}] {first['message'][:60]}...")
        else:
            print("\n   No log entries found (expected for test)")
        
        # Search historical cases
        case_parser = CaseLogParser(CASE_LOG_FILE)
        case_results = case_parser.search_by_keywords(['container', 'duplicate'])
        
        print(f"\n✅ Found {len(case_results)} similar historical cases")
        if case_results:
            top_case = case_results[0]
            print(f"   Top match (similarity: {top_case['similarity']:.2%}):")
            print(f"   Problem: {top_case['case'].get('Problem Statements', 'N/A')[:80]}...")
        
        # Search knowledge base
        kb_parser = KnowledgeBaseParser(KNOWLEDGE_BASE_FILE)
        kb_results = kb_parser.search_by_keywords(['container'])
        
        print(f"\n✅ Found {len(kb_results)} KB articles")
        if kb_results:
            print(f"   Top match: {kb_results[0]['section_title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("  PORTNET INCIDENT RESOLVER - PARSER TESTS")
    print("🚀" * 30)
    
    tests = [
        ("File Existence", test_file_existence),
        ("Case Log Parser", test_case_log_parser),
        ("Knowledge Base Parser", test_knowledge_base_parser),
        ("Escalation Contacts Parser", test_escalation_contacts_parser),
        ("Application Log Parser", test_application_log_parser),
        ("Realistic Search Scenario", test_search_scenario),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready for Phase 2!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix issues before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)