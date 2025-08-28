import os
import logging
import traceback
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("admission-chatbot-backend")

app = Flask(__name__)

# Put your real key in the environment for production. This default is for local dev only.
os.environ["SAMBANOVA_API_KEY"] = "1bda44c2-fac2-4082-8da5-b49b1a4e14b3"

_llm = None

def init_llm():
    """Lazily initialize the SambaNova LLM wrapper."""
    global _llm
    if _llm is not None:
        return _llm
    try:
        from llama_index.llms.sambanovasystems import SambaNovaCloud

        logger.info("Initializing SambaNovaCloud LLM...")
        _llm = SambaNovaCloud(
            model="Meta-Llama-3.3-70B-Instruct",
            context_window=100000,
            max_tokens=1024,
            temperature=0.7,
            top_k=1,
            top_p=0.01,
        )
        logger.info("SambaNovaCloud initialized")
    except Exception:
        logger.exception("Failed to initialize SambaNovaCloud")
        raise
    return _llm

def extract_text_from_llm_response(resp):
    """
    Best-effort extraction of primary text from common LLM wrapper return types.
    Returns a plain string.
    """
    try:
        # If it's already a string
        if isinstance(resp, str):
            return resp

        # Common single-field names
        for attr in ("response", "text", "output", "content", "answer"):
            val = getattr(resp, attr, None)
            if isinstance(val, str) and val.strip():
                return val

        # Common container fields: generations, choices, outputs
        for container in ("generations", "choices", "outputs", "candidates"):
            attr = getattr(resp, container, None)
            if attr:
                try:
                    # If it's a list of dicts or objects, inspect first item
                    first = attr[0]
                    if isinstance(first, str):
                        return first
                    if isinstance(first, dict):
                        for key in ("text", "content", "response"):
                            if key in first and isinstance(first[key], str):
                                return first[key]
                    # object with attributes
                    for key in ("text", "content", "response"):
                        nested = getattr(first, key, None)
                        if isinstance(nested, str):
                            return nested
                except Exception:
                    pass

        # If the object has a nice string repr, use it as a fallback
        try:
            s = str(resp)
            if s and s.strip():
                return s
        except Exception:
            pass

    except Exception:
        logger.exception("Error extracting text from LLM response")

    return ""  # empty string if nothing found

def call_llm(llm, prompt: str):
    """
    Try common call patterns against the LLM wrapper and return the raw response object.
    """
    errors = []
    # Prefer explicit chat API if available
    try:
        if hasattr(llm, "chat"):
            return llm.chat(prompt)
    except Exception as e:
        errors.append(("chat", str(e)))

    # generate
    try:
        if hasattr(llm, "generate"):
            return llm.generate(prompt)
    except Exception as e:
        errors.append(("generate", str(e)))

    # callable (llm(prompt))
    try:
        if callable(llm):
            return llm(prompt)
    except Exception as e:
        errors.append(("callable", str(e)))

    # predict / complete
    try:
        if hasattr(llm, "predict"):
            return llm.predict(prompt)
    except Exception as e:
        errors.append(("predict", str(e)))

    try:
        if hasattr(llm, "complete"):
            return llm.complete(prompt)
    except Exception as e:
        errors.append(("complete", str(e)))

    # If none worked, return a descriptive string for debugging
    return f"<LLM call failed; attempts: {errors}>"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_query = data.get("message", "")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        llm = init_llm()
    except Exception as e:
        tb = traceback.format_exc()
        logger.error("LLM init failed: %s", tb)
        return jsonify({"error": "LLM initialization failed", "details": str(e), "trace": tb}), 500

    try:
        logger.info("Calling LLM for user query")
        raw_resp = call_llm(llm, user_query)
        text = extract_text_from_llm_response(raw_resp) or ""
        # Return plain text only (no yes/no extraction)
        return jsonify({"response": text}), 200
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception("LLM call failed")
        return jsonify({"error": "LLM execution failed", "details": str(e), "trace": tb}), 500

if __name__ == "__main__":
    # For local development, bind to localhost
    app.run(host="127.0.0.1", port=5000, debug=True)