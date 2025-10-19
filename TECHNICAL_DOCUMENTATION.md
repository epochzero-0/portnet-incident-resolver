# 🔬 Technical Documentation

Deep technical dive into PORTNET Incident Resolver architecture, design decisions, and implementation details.

---

## 📑 Table of Contents

1. [System Architecture](#system-architecture)
2. [Design Philosophy](#design-philosophy)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [AI Integration](#ai-integration)
6. [Performance Optimization](#performance-optimization)
7. [Testing Strategy](#testing-strategy)
8. [Future Improvements](#future-improvements)

---

## 🏗️ System Architecture

### **High-Level Overview**

```
┌──────────────────────────────────────────────────────────────┐
│                      Presentation Layer                       │
│                    (Streamlit Web UI)                        │
│  • User input forms                                          │
│  • Results visualization                                     │
│  • Download/export functionality                            │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                      │
│                    (Core Analyzers)                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Incident   │→ │   Context    │→ │   AI Analyzer    │ │
│  │    Parser    │  │   Gatherer   │  │                  │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
│        │                  │                    │           │
│        │                  │                    │           │
│  Extract entities    Search data         Generate plans    │
│  Classify type      Correlate info       Create summaries  │
│                                                              │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                      Data Access Layer                        │
│                        (Parsers)                             │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │   Case   │  │   Log    │  │    KB    │  │  Contacts  │ │
│  │  Parser  │  │  Parser  │  │  Parser  │  │   Parser   │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                      Data Sources                             │
├──────────────────────────────────────────────────────────────┤
│  • Case Log.xlsx (323 cases)                                │
│  • Application Logs/ (6 services, 63 lines)                 │
│  • Knowledge Base.docx (102K chars)                         │
│  • Escalation Contacts.pdf (3 contacts)                     │
│  • Database/db.sql (schema reference)                       │
└──────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                   External Services                           │
├──────────────────────────────────────────────────────────────┤
│  • Azure OpenAI API (GPT-4.1-nano)                          │
│  • Analysis & generation                                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Design Philosophy

### **1. Separation of Concerns**

**Why?**
> Each component should have one responsibility and do it well

**How?**
```python
src/
├── parsers/      # ONLY parse files → return structured data
├── analyzers/    # ONLY analyze data → return insights  
├── generators/   # ONLY generate outputs → return formatted text
└── utils/        # ONLY provide utilities → return config/helpers
```

**Benefits:**
- ✅ Easy to test each component independently
- ✅ Easy to modify one part without breaking others
- ✅ Clear responsibility boundaries

---

### **2. Data-First Approach**

**Why?**
> AI is only as good as the context it receives

**How?**
```python
# Wrong: Ask AI blindly
result = ai.analyze("Container duplicate issue")  # ❌ No context

# Right: Gather all context first
context = {
    'logs': search_logs("CMAU0000020"),           # ✅ Specific evidence
    'cases': find_similar_cases("duplicate"),     # ✅ Historical solutions
    'kb