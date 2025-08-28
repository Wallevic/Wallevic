import os
import logging
import traceback
import requests
import json
import re
import time
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG for more details
logger = logging.getLogger("oaustech-chatbot-backend")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Set SambaNova API key securely (remove placeholder before deployment)
os.environ["SAMBANOVA_API_KEY"] = "1bda44c2-fac2-4082-8da5-b49b1a4e14b3"

# OAUSTECH-specific knowledge base
OAUSTECH_KNOWLEDGE_BASE = {
    "admissions": {
        "requirements": "OAUSTECH admission requirements include: 5 O'Level credits including English and Mathematics, UTME score of 180+, and meeting specific course requirements. Visit oaustech.edu.ng for detailed information.",
        "application": "Apply through JAMB portal, then complete OAUSTECH post-UTME screening. Application period typically runs from March to July.",
        "deadlines": "UTME registration: February, Post-UTME: July-August, Admission list: September-October"
    },
    "programs": {
        "faculties": "OAUSTECH has 6 faculties: Engineering, Science, Technology, Environmental Sciences, Agriculture, and Management Sciences",
        "popular_courses": "Computer Engineering, Electrical Engineering, Mechanical Engineering, Computer Science, Biochemistry, Microbiology, Architecture, Quantity Surveying, Business Administration"
    },
    "fees": {
        "tuition": "Tuition fees range from ₦60,000 to ₦180,000 per session depending on faculty and program",
        "accommodation": "Hostel fees: ₦20,000 - ₦35,000 per session. Off-campus accommodation available in Okitipupa"
    },
    "campus": {
        "location": "Olusegun Agagu University of Science and Technology is located in Okitipupa, Ondo State, Nigeria",
        "facilities": "Modern library, ICT center, engineering workshops, science laboratories, sports complex, health center, student union building"
    }
}

_llm = None

def init_llm():
    """Lazily initialize the SambaNova LLM wrapper."""
    global _llm
    if _llm is not None:
        return _llm
    try:
        from llama_index.llms.sambanovasystems import SambaNovaCloud

        logger.debug("Initializing SambaNovaCloud LLM...")
        _llm = SambaNovaCloud(
            model="Meta-Llama-3.3-70B-Instruct",  # Verify this model name with SambaNova
            context_window=100000,
            max_tokens=1024,
            temperature=0.7,
            top_k=1,
            top_p=0.01,
        )
        logger.info("SambaNovaCloud initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SambaNovaCloud: {str(e)}")
        raise
    return _llm

def extract_text_from_llm_response(resp):
    """Extract the primary text from the LLM response object."""
    try:
        if isinstance(resp, str):
            return resp

        for attr in ("response", "text", "output", "content", "answer", "message"):
            val = getattr(resp, attr, None)
            if isinstance(val, str) and val.strip():
                return val

        for container in ("generations", "choices", "outputs", "candidates"):
            attr = getattr(resp, container, None)
            if attr and len(attr) > 0:
                first = attr[0]
                if isinstance(first, str):
                    return first
                if isinstance(first, dict):
                    for key in ("text", "content", "response", "message"):
                        if key in first and isinstance(first[key], str):
                            return first[key]
                for key in ("text", "content", "response", "message"):
                    nested = getattr(first, key, None)
                    if isinstance(nested, str):
                        return nested

        s = str(resp).strip()
        if s:
            return s

    except Exception:
        logger.exception("Error extracting text from LLM response")
        return ""

    return ""

def call_llm(llm, prompt: str):
    """Attempt to call the LLM using common methods."""
    errors = []
    methods = ["chat", "complete", "generate", "predict"]

    for method in methods:
        if hasattr(llm, method):
            try:
                logger.debug(f"Calling LLM with method: {method}")
                return getattr(llm, method)(prompt)
            except Exception as e:
                errors.append((method, str(e)))

    if callable(llm):
        try:
            logger.debug("Calling LLM as callable")
            return llm(prompt)
        except Exception as e:
            errors.append(("__call__", str(e)))

    logger.error(f"LLM call failed; attempts: {errors}")
    return f"<LLM call failed; attempts: {errors}>"

def fetch_page_content(url: str) -> str:
    """Fetch and extract readable text from a webpage."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(url, timeout=15, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text from various elements
        text_elements = []
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th']):
            text = element.get_text(strip=True)
            if text and len(text) > 10:
                text_elements.append(text)
        
        text = ' '.join(text_elements)
        logger.debug(f"Fetched {len(text)} characters from {url}")
        return text[:4000]
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return ""

def search_web_for_oaustech(query: str) -> List[Dict]:
    """Enhanced web search specifically for OAUSTECH-related information."""
    try:
        search_queries = [
            f"{query} OAUSTECH Olusegun Agagu University Science Technology Nigeria",
            f"{query} site:oaustech.edu.ng",
            f"{query} Okitipupa university",
            f"{query} Ondo State university admission"
        ]
        
        all_results = []
        ddgs = DDGS()
        
        for search_query in search_queries:
            try:
                logger.debug(f"Searching DuckDuckGo with query: {search_query}")
                results = ddgs.text(search_query, max_results=2, safesearch="off")
                for result in results:
                    if result not in all_results:
                        all_results.append(result)
            except Exception as e:
                logger.warning(f"Search failed for '{search_query}': {e}")
                continue
        
        logger.debug(f"Found {len(all_results)} unique search results")
        return all_results[:6]
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return []

def get_relevant_oaustech_knowledge(query: str) -> str:
    """Extract relevant information from OAUSTECH knowledge base."""
    query_lower = query.lower()
    relevant_info = []
    
    if any(word in query_lower for word in ['admission', 'apply', 'requirement', 'entry']):
        relevant_info.append(OAUSTECH_KNOWLEDGE_BASE['admissions']['requirements'])
        relevant_info.append(OAUSTECH_KNOWLEDGE_BASE['admissions']['application'])
    
    if any(word in query_lower for word in ['course', 'program', 'faculty', 'study', 'degree']):
        relevant_info.append(OAUSTECH_KNOWLEDGE_BASE['programs']['faculties'])
        relevant_info.append(OAUSTECH_KNOWLEDGE_BASE['programs']['popular_courses'])
    
    if any(word in query_lower for word in ['fee', 'cost', 'tuition', 'payment', 'money']):
        relevant_info.append(OAUSTECH_KNOWLEDGE_BASE['fees']['tuition'])
        relevant_info.append(OAUSTECH_KNOWLEDGE_BASE['fees']['accommodation'])
    
    if any(word in query_lower for word in ['campus', 'location', 'facility', 'hostel', 'accommodation']):
        relevant_info.append(OAUSTECH_KNOWLEDGE_BASE['campus']['location'])
        relevant_info.append(OAUSTECH_KNOWLEDGE_BASE['campus']['facilities'])
    
    # Handle vague queries like "hey"
    if not relevant_info and len(query_lower.strip()) < 5:
        relevant_info.append("I'm here to help with information about Olusegun Agagu University of Science and Technology (OAUSTECH), conceptualized by Adekankun Mercy Ayomikun. Please ask about admissions, courses, fees, or campus life, or visit oaustech.edu.ng for more details.")
    
    return "\n".join(relevant_info) if relevant_info else ""

def personalize_response_for_oaustech(response: str, query: str) -> str:
    """Ensure response is personalized to OAUSTECH context."""
    query_lower = query.lower().strip()
    response_lower = response.lower()

    # Handle short/vague queries
    if len(query_lower) < 5 or query_lower in ['hey', 'hi', 'hello', 'yo']:
        return "Hello! I'm the OAUSTECH AI Assistant, conceptualized and developed by Adekankun Mercy Ayomikun, here to help with information about Olusegun Agagu University of Science and Technology, Okitipupa, Nigeria. Ask me about admissions, courses, fees, or campus life, or visit oaustech.edu.ng for more details."

    # If response doesn't mention OAUSTECH or is an error
    if 'oaustech' not in response_lower and 'olusegun agagu' not in response_lower or 'error' in response_lower or 'cannot' in response_lower:
        return f"I'm specialized in OAUSTECH (Olusegun Agagu University of Science and Technology) information, conceptualized by Adekankun Mercy Ayomikun. While I can't directly answer that query, I'd be happy to help with OAUSTECH-related topics like admissions, programs, fees, or campus facilities. You can also visit our official website at oaustech.edu.ng for more information."

    return response

def react_agent_process(query: str) -> Tuple[str, str]:
    """ReACT agent implementation for processing queries, returning response and debug info."""
    debug_info = []
    try:
        llm = init_llm()
        debug_info.append("LLM initialized successfully")
        
        # Step 1: Analyze query and determine action
        analysis_prompt = f"""
You are an AI assistant for OAUSTECH (Olusegun Agagu University of Science and Technology), conceptualized and developed by Adekankun Mercy Ayomikun. Analyze this query and determine the best approach:

Query: {query}

Available actions:
1. Use internal OAUSTECH knowledge base
2. Search the web for current OAUSTECH information
3. Both internal knowledge and web search
4. General response with OAUSTECH context

Respond with only the action number (1, 2, 3, or 4).
"""
        debug_info.append(f"Analysis prompt: {analysis_prompt[:200]}...")
        
        action_response = call_llm(llm, analysis_prompt)
        action = extract_text_from_llm_response(action_response).strip()
        debug_info.append(f"Action response: {action}")
        
        # Extract action number, default to 1 for vague queries
        action_match = re.search(r'\d', action)
        action_num = int(action_match.group()) if action_match else (1 if len(query.strip()) < 5 else 3)
        debug_info.append(f"Selected action: {action_num}")
        
        # Step 2: Gather information based on action
        context_parts = []
        
        if action_num in [1, 3]:
            internal_knowledge = get_relevant_oaustech_knowledge(query)
            if internal_knowledge:
                context_parts.append(f"Internal OAUSTECH Knowledge:\n{internal_knowledge}")
                debug_info.append(f"Internal knowledge retrieved: {internal_knowledge[:200]}...")
        
        if action_num in [2, 3]:
            web_results = search_web_for_oaustech(query)
            if web_results:
                web_context = "Web Search Results:\n"
                for i, result in enumerate(web_results[:3], 1):
                    url = result.get('href', '')
                    title = result.get('title', '')
                    snippet = result.get('body', '')
                    
                    if 'oaustech.edu.ng' in url:
                        full_content = fetch_page_content(url)
                        if full_content:
                            web_context += f"Source {i}: {url}\nTitle: {title}\nContent: {full_content[:1000]}\n\n"
                        else:
                            web_context += f"Source {i}: {url}\nTitle: {title}\nSnippet: {snippet}\n\n"
                    else:
                        web_context += f"Source {i}: {url}\nTitle: {title}\nSnippet: {snippet}\n\n"
                
                context_parts.append(web_context)
                debug_info.append(f"Web context retrieved: {web_context[:200]}...")
            else:
                debug_info.append("No web results found")
        
        # Step 3: Generate final response
        context = "\n\n".join(context_parts) if context_parts else "No specific context available."
        debug_info.append(f"Combined context length: {len(context)} characters")
        
        final_prompt = f"""
You are an AI assistant specialized in Olusegun Agagu University of Science and Technology (OAUSTECH), Okitipupa, Nigeria, conceptualized and developed by Adekankun Mercy Ayomikun as a final year undergraduate project. 
Your role is to provide helpful, accurate information on admissions, courses, fees, student services, and related issues at OAUSTECH.

IMPORTANT: Always personalize responses to OAUSTECH context. If the query is vague or unrelated to OAUSTECH, politely redirect to OAUSTECH topics or note your specialization.

Use the provided context to inform your answer, but prioritize official OAUSTECH information from oaustech.edu.ng.
If information is unavailable, suggest checking the official OAUSTECH website (oaustech.edu.ng) or contacting the university at info@oaustech.edu.ng or +234 709 880 9476.

Context:
{context}

User Query: {query}

Provide a comprehensive, helpful response that is specifically tailored to OAUSTECH:
"""
        debug_info.append(f"Final prompt length: {len(final_prompt)} characters")
        
        raw_response = call_llm(llm, final_prompt)
        response_text = extract_text_from_llm_response(raw_response).strip()
        debug_info.append(f"Raw LLM response: {response_text[:200]}...")
        
        if not response_text:
            response_text = "I apologize, but I couldn't generate a response. Please try rephrasing your question about OAUSTECH or visit our official website at oaustech.edu.ng for more information. This AI assistant was conceptualized by Adekankun Mercy Ayomikun."
        
        # Step 4: Personalize the response
        personalized_response = personalize_response_for_oaustech(response_text, query)
        debug_info.append("Response personalized for OAUSTECH")
        
        return personalized_response, "\n".join(debug_info)
        
    except Exception as e:
        debug_info.append(f"Error in ReACT agent: {str(e)}\n{traceback.format_exc()}")
        return (
            "I encountered an error while processing your query about OAUSTECH. Please try again or visit our official website at oaustech.edu.ng for information. This AI assistant was conceptualized by Adekankun Mercy Ayomikun.",
            "\n".join(debug_info)
        )

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "OAUSTECH Chatbot Backend"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_query = data.get("message", "").strip()
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        logger.info(f"Processing query: {user_query}")
        
        # Process query with ReACT agent
        response, debug_info = react_agent_process(user_query)
        
        return jsonify({
            "response": response,
            "query": user_query,
            "timestamp": str(time.time()),
            "debug": debug_info  # Include debug info for development
        }), 200
        
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Query processing failed: {tb}")
        return jsonify({
            "error": "Query processing failed",
            "details": str(e),
            "debug": tb,
            "fallback_response": "I'm having trouble processing your request about OAUSTECH. Please try again or visit our official website at oaustech.edu.ng for information. This AI assistant was conceptualized by Adekankun Mercy Ayomikun."
        }), 500

@app.route("/knowledge", methods=["GET"])
def get_knowledge_base():
    """Endpoint to get OAUSTECH knowledge base structure."""
    return jsonify({
        "knowledge_base": OAUSTECH_KNOWLEDGE_BASE,
        "description": "OAUSTECH-specific information for chatbot responses"
    }), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)