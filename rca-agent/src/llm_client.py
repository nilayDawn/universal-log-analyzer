import os
import sys
from google import genai
from google.genai import types
from schemas import RootCauseAnalysis

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

def generate_rca(block_id: str, context_logs: str) -> str:
    """Sends the logs to Gemini and returns a JSON string matching the RootCauseAnalysis schema."""
    if not context_logs.strip():
        return '{"error": "No logs provided for analysis."}'

    # The modern client automatically picks up GEMINI_API_KEY from the environment
    client = genai.Client()
    
    prompt = f"""
    You are an expert AIOps diagnosing agent. A critical anomaly has been detected for the HDFS entity: {block_id}.
    Analyze the following chronological logs to determine the root cause of the failure.
    
    Logs:
    {context_logs}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',   # model 2.5 is no longer available, using 3.8-flash instead
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RootCauseAnalysis,
            ),
        )
        return response.text
    except Exception as e:
        return f'{{"error": "LLM generation failed: {str(e)}"}}'