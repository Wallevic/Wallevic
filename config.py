"""
AAUA AI Assistant Configuration
This file contains all configurable settings for the chatbot.
"""

import os
from typing import Dict, List

# =============================================================================
# API Configuration
# =============================================================================

# SambaNova API Configuration
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY", "1bda44c2-fac2-4082-8da5-b49b1a4e14b3")
SAMBANOVA_MODEL = "Meta-Llama-3.1-70B-Instruct"
SAMBANOVA_CONFIG = {
    "context_window": 100000,
    "max_tokens": 1024,
    "temperature": 0.7,
    "top_k": 1,
    "top_p": 0.01,
}

# =============================================================================
# Server Configuration
# =============================================================================

# Flask Backend Configuration
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Streamlit Frontend Configuration
STREAMLIT_PORT = 8501

# =============================================================================
# Web Search Configuration
# =============================================================================

# DuckDuckGo Search Configuration
DDG_MAX_RESULTS = 6
DDG_SAFESEARCH = "off"
DDG_TIMEOUT = 15

# Web Scraping Configuration
SCRAPING_TIMEOUT = 15
MAX_CONTENT_LENGTH = 4000
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Search Queries for AAUA
AAUA_SEARCH_QUERIES = [
    "{query} AAUA Adekunle Ajasin University Nigeria",
    "{query} site:aaua.edu.ng",
    "{query} Akungba-Akoko university",
    "{query} Ondo State university admission"
]

# =============================================================================
# AAUA Knowledge Base
# =============================================================================

AAUA_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    "admissions": {
        "requirements": "AAUA admission requirements include: 5 O'Level credits including English and Mathematics, UTME score of 180+, and meeting specific course requirements. Visit aaua.edu.ng for detailed information.",
        "application": "Apply through JAMB portal, then complete AAUA post-UTME screening. Application period typically runs from March to July.",
        "deadlines": "UTME registration: February, Post-UTME: July-August, Admission list: September-October",
        "post_utme": "AAUA conducts post-UTME screening for all candidates. Check the official website for current screening dates and requirements.",
        "transfer": "Transfer students must have completed at least one academic session at their previous institution and meet AAUA's transfer requirements."
    },
    "programs": {
        "faculties": "AAUA has 9 faculties: Arts, Education, Law, Science, Social Sciences, Agriculture, Engineering, Environmental Design, and Pharmacy",
        "popular_courses": "Computer Science, Law, Economics, Accounting, Microbiology, Biochemistry, Political Science, English Language, Mathematics, Physics, Chemistry",
        "undergraduate": "AAUA offers various undergraduate programs across 9 faculties. Each program typically lasts 4-5 years depending on the course.",
        "postgraduate": "AAUA offers postgraduate programs including Masters and PhD degrees in various disciplines. Check the postgraduate school for specific requirements.",
        "part_time": "Some programs are available on part-time basis. Contact the relevant faculty for information on part-time options."
    },
    "fees": {
        "tuition": "Tuition fees range from ₦50,000 to ₦150,000 per session depending on faculty and program. New students may have additional charges.",
        "accommodation": "Hostel fees: ₦15,000 - ₦25,000 per session. Off-campus accommodation available in Akungba-Akoko with varying costs.",
        "acceptance": "Acceptance fee is typically ₦20,000 for new students. This is separate from tuition fees.",
        "other_fees": "Other fees include: Development levy, Library fee, ICT fee, Sports fee, and Student Union fee. Total additional fees approximately ₦10,000-₦15,000.",
        "payment": "Fees can be paid through the university portal or designated banks. Payment plans may be available for some students."
    },
    "campus": {
        "location": "Adekunle Ajasin University is located in Akungba-Akoko, Ondo State, Nigeria. The campus is easily accessible by road.",
        "facilities": "Modern library, ICT center, sports complex, health center, student union building, cafeteria, banking facilities, and security services.",
        "transportation": "Regular transportation services connect the campus to major cities. Private vehicles and commercial transport are available.",
        "security": "24/7 security services are provided on campus. Students are advised to follow security guidelines and report any incidents.",
        "health": "The university health center provides basic medical services to students. Emergency services are available 24/7."
    },
    "student_life": {
        "clubs": "Various student clubs and organizations are available including academic, cultural, religious, and social groups.",
        "sports": "Sports facilities include football field, basketball court, tennis court, and indoor sports facilities. Inter-faculty competitions are held regularly.",
        "events": "Annual events include orientation week, cultural day, sports week, and graduation ceremonies.",
        "support": "Student support services include counseling, career guidance, disability support, and international student services.",
        "accommodation": "On-campus and off-campus accommodation options are available. Students can choose based on preference and budget."
    },
    "academic": {
        "calendar": "Academic calendar typically runs from September to July with breaks for holidays and examinations.",
        "examinations": "Examinations are held at the end of each semester. Students must meet attendance requirements to be eligible.",
        "grading": "Grading system uses letter grades (A-F) with corresponding grade points. Minimum CGPA of 1.0 required to graduate.",
        "library": "The university library provides access to books, journals, electronic resources, and study spaces.",
        "research": "Students can participate in research activities through their departments and faculty research groups."
    }
}

# =============================================================================
# Prompt Templates
# =============================================================================

SYSTEM_PROMPT = """You are an AI assistant specialized in Adekunle Ajasin University (AAUA), Akungba-Akoko, Nigeria. 
Your role is to provide helpful, accurate information on admissions, courses, fees, student services, and related issues at AAUA.

IMPORTANT: Always personalize responses to AAUA context. If the question seems unrelated to AAUA, politely redirect to AAUA topics or note your specialization.

Use the provided context to inform your answer, but prioritize official AAUA information.
If information is unavailable, suggest checking the official AAUA website (aaua.edu.ng) or contacting the university."""

ANALYSIS_PROMPT = """You are an AI assistant for AAUA (Adekunle Ajasin University). Analyze this query and determine the best approach:

Query: {query}

Available actions:
1. Use internal AAUA knowledge base
2. Search the web for current AAUA information
3. Both internal knowledge and web search
4. General response with AAUA context

Respond with only the action number (1, 2, 3, or 4)."""

# =============================================================================
# Response Personalization
# =============================================================================

# Keywords for detecting query types
QUERY_KEYWORDS = {
    "admissions": ["admission", "apply", "requirement", "entry", "enrollment", "register"],
    "programs": ["course", "program", "faculty", "study", "degree", "major", "subject"],
    "fees": ["fee", "cost", "tuition", "payment", "money", "price", "charge"],
    "campus": ["campus", "location", "facility", "hostel", "accommodation", "building"],
    "student_life": ["student", "life", "club", "sport", "event", "activity", "social"],
    "academic": ["academic", "exam", "grade", "study", "library", "research", "calendar"]
}

# Fallback responses for different scenarios
FALLBACK_RESPONSES = {
    "no_response": "I apologize, but I couldn't generate a response. Please try rephrasing your question about AAUA or visit our official website at aaua.edu.ng for more information.",
    "error": "I encountered an error while processing your query about AAUA. Please try again or visit our official website at aaua.edu.ng for information.",
    "unrelated": "I'm specialized in AAUA (Adekunle Ajasin University) information. While I can't answer that specific question, I'd be happy to help with AAUA-related queries like admissions, programs, fees, or campus information. You can also visit our official website at aaua.edu.ng for more details.",
    "general": "Here's some general information, but for specific details about AAUA (Adekunle Ajasin University), I recommend checking our official website at aaua.edu.ng or asking me about AAUA-specific topics like admissions, programs, or campus facilities."
}

# =============================================================================
# Logging Configuration
# =============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "aaua_chatbot.log"

# =============================================================================
# UI Configuration
# =============================================================================

# Streamlit UI Configuration
STREAMLIT_CONFIG = {
    "page_title": "AAUA AI Assistant",
    "page_icon": "🎓",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Color scheme (AAUA colors)
COLORS = {
    "primary": "#400075",
    "secondary": "#6a0dad",
    "background": "#f8f9ff",
    "border": "#e0e6ff",
    "text": "#333333",
    "success": "#28a745",
    "error": "#dc3545",
    "warning": "#ffc107"
}

# Quick question cards
QUICK_QUESTIONS = [
    {"icon": "📝", "text": "What are the admission requirements for Computer Science?"},
    {"icon": "🏠", "text": "Tell me about hostel accommodation options"},
    {"icon": "📅", "text": "What is the current academic calendar?"},
    {"icon": "💸", "text": "How much are the tuition fees for Law program?"},
    {"icon": "🎓", "text": "What programs are available in Faculty of Science?"},
    {"icon": "📚", "text": "How do I apply for admission to AAUA?"},
    {"icon": "🏥", "text": "What health services are available on campus?"},
    {"icon": "🚌", "text": "How do I get to AAUA campus?"},
    {"icon": "📖", "text": "Tell me about the library facilities"},
    {"icon": "🎯", "text": "What are the popular courses at AAUA?"}
]

# =============================================================================
# Testing Configuration
# =============================================================================

# Test queries for validation
TEST_QUERIES = [
    "What are the admission requirements for Computer Science?",
    "How much are the tuition fees?",
    "Tell me about hostel accommodation",
    "What programs are available in Faculty of Science?",
    "How do I apply for admission to AAUA?",
    "What is the current academic calendar?",
    "Tell me about the campus facilities",
    "What are the popular courses at AAUA?",
    "How do I contact the university?",
    "What is the weather like today?"  # Non-AAUA query to test personalization
]

# =============================================================================
# Development Configuration
# =============================================================================

# Development mode settings
DEBUG_MODE = True
ENABLE_LOGGING = True
ENABLE_CORS = True
ENABLE_HEALTH_CHECK = True

# Rate limiting (requests per minute)
RATE_LIMIT = 60

# Cache settings
ENABLE_CACHE = True
CACHE_DURATION = 300  # 5 minutes

# =============================================================================
# Export Configuration
# =============================================================================

def get_all_config() -> Dict:
    """Get all configuration as a dictionary."""
    return {
        "api": {
            "sambanova_key": SAMBANOVA_API_KEY,
            "sambanova_model": SAMBANOVA_MODEL,
            "sambanova_config": SAMBANOVA_CONFIG
        },
        "server": {
            "flask_host": FLASK_HOST,
            "flask_port": FLASK_PORT,
            "streamlit_port": STREAMLIT_PORT
        },
        "search": {
            "ddg_max_results": DDG_MAX_RESULTS,
            "scraping_timeout": SCRAPING_TIMEOUT,
            "max_content_length": MAX_CONTENT_LENGTH
        },
        "knowledge_base": AAUA_KNOWLEDGE_BASE,
        "ui": {
            "colors": COLORS,
            "quick_questions": QUICK_QUESTIONS
        },
        "development": {
            "debug_mode": DEBUG_MODE,
            "enable_logging": ENABLE_LOGGING,
            "rate_limit": RATE_LIMIT
        }
    }
