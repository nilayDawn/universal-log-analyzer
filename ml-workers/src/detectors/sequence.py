from collections import defaultdict

class SequenceDetector:
    def __init__(self):
        # Dictionary mapping Template_A -> Template_B -> count
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.state_totals = defaultdict(int)
        
        # Track the last seen template per Block ID for session continuity
        self.active_sessions = {}
        self.min_observations = 10 # Minimum baseline before trusting the model

    def calculate_score(self, block_id: str, current_template: str) -> float:
        if block_id == "unknown":
            return 0.0

        previous_template = self.active_sessions.get(block_id)
        self.active_sessions[block_id] = current_template

        if not previous_template:
            return 0.0 # First log for this block session

        # Record and analyze the transition from Previous -> Current
        total_transitions = self.state_totals[previous_template]
        self.transitions[previous_template][current_template] += 1
        self.state_totals[previous_template] += 1

        if total_transitions < self.min_observations:
            return 0.0 # Still learning the baseline

        # Calculate transition probability
        transition_count = self.transitions[previous_template][current_template]
        probability = transition_count / (total_transitions + 1)

        # Flag an anomaly if this workflow path occurs < 5% of the time
        if probability < 0.05:
            return min(1.0 - probability, 1.0)
            
        return 0.0