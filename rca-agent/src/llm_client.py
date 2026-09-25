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
    
    # IMPROVED PROMPT: Clear instructions matching standard operational schema structures
    prompt = f"""
    You are an expert AIOps diagnosing agent. A critical anomaly has been detected for the HDFS entity: {block_id}.
    Analyze the following chronological logs to determine the exact root cause of the failure.
    
    Logs:
    {context_logs}
    
    Instructions for your structured output fields:
    - Assess whether this indicates a genuine hardware failure, network glitch, or normal routine execution.
    - Provide a concise summary of the timeline of events leading up to the final log status.
    - Quantify your confidence score regarding this assessment.
    - Detail actionable remediation steps for system administrators.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',   # model 2.5 is no longer available, using 3.8-flash instead
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RootCauseAnalysis,
                temperature=0.1
            ),
        )
        return response.text
    except Exception as e:
        return f'{{"error": "LLM generation failed: {str(e)}"}}'