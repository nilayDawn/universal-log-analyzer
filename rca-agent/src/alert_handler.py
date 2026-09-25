import json
from retriever import EvidenceRetriever  
from llm_client import generate_rca      

class AlertOrchestrator:
    def __init__(self):
        self.retriever = EvidenceRetriever()

    def process_incident(self, block_id: str, trigger_time: float):
        """Orchestrates the entire RCA timeline workflow asynchronously or in a worker thread."""
        print(f"\n[⚡] Incident handler triggered for Block: {block_id}")
        
        # 1. Fetch the entire 20-minute operational block window from SQLite
        context_logs = self.retriever.get_context_window(block_id, trigger_time)
        
        if not context_logs.strip():
            print(f"[!] Critical context window empty for block {block_id}. Aborting LLM analysis.")
            return

        print(f"[*] Extracted historical context logs. Sending package to Gemini...")

        # 2. Transmit historical logs to Gemini for Root Cause Analysis
        json_rca_output = generate_rca(block_id, context_logs)
        
        # 3. Print or save the structured response
        try:
            parsed_json = json.loads(json_rca_output)
            print(f"[✓] Structured RCA Generation Complete for {block_id}:")
            print(json.dumps(parsed_json, indent=4))
            
            # Optional: Here you can insert 'parsed_json' into an 'incidents' table in SQLite
            
        except json.JSONDecodeError:
            print("[!] Gemini returned malformed JSON data:")
            print(json_rca_output)