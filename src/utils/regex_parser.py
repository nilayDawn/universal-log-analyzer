import re
#regex pattern to extract data

PATTERNS = {
    "WEB": r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[WEB\] IP=(?P<ip>\S+) PATH=(?P<path>\S+) STATUS=(?P<status>\d+)",
    "AUTH": r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[AUTH\] USER=(?P<user>\S+) LOGIN=(?P<status>\w+)",
    "DATABASE": r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[DATABASE\] LEVEL=(?P<level>\w+) MSG=\"(?P<msg>[^\"]*)\"",
    # Fallback bucket for logs that we cannot classify.
    "UNMATCHED": r"(?P<ts>.*)"
}

