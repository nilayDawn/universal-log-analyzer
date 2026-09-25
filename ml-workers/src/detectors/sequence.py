# What it does: It checks if logs are happening in the correct, logical order. 
# Simple Example: A normal HDFS block write should follow a strict timeline:allocateBlock --> 2. Receiving block --> 3. addStoredBlock (Success).If a sequence detector suddenly sees step 3 without steps 1 and 2, it flags an anomaly. 
# Why it matters: It finds hidden process crashes or network drops where a task cuts out halfway through its job.
#Implements Markov Chain Transition Matrix


from collections import defaultdict

class SequenceDetector:
    def __init__(self, min_observations=10):
        # Markov Chain Transition matrix
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.state_totals = defaultdict(int)
        
        # Track active block sessions
        self.active_sessions = {}
        self.min_observations = min_observations

    def calculate_score(self, block_id: str, current_template: str) -> float:
        if block_id == "unknown":
            return 0.0

        previous_template = self.active_sessions.get(block_id)
        
        # Session Lifecycle Management
        if "terminating" in current_template.lower() or "verification succeeded" in current_template.lower():
            # If the block sequence is finished, drop it from memory to prevent leaks
            self.active_sessions.pop(block_id, None)
        else:
            self.active_sessions[block_id] = current_template

        if not previous_template:
            return 0.0  # Session start

        # Update baseline statistics
        self.transitions[previous_template][current_template] += 1
        self.state_totals[previous_template] += 1
        
        # Get the freshly updated total for proper relative probability math
        updated_total = self.state_totals[previous_template]

        if updated_total < self.min_observations:
            return 0.0  # Training phase bypass

        # Fixed Probability Formula
        transition_count = self.transitions[previous_template][current_template]
        probability = transition_count / updated_total

        # Anomaly trigger (Less than 5% probability)
        if probability < 0.05:
            # Returns a value close to 1.0 for high anomalies
            return 1.0 - probability
            
        return 0.0
