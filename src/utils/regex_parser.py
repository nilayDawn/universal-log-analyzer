import re
#regex pattern to extract data

PATTERNS = {
    "WEB": r"(?P<ts>.*?) \[WEB\] IP=(?P<ip>.*?) PATH=(?P<path>.*?) STATUS=(?P<status>\d+)",
    "AUTH": r"(?P<ts>.*?) \[AUTH\] USER=(?P<user>.*?) LOGIN=(?P<status>\w+)",
    "DATABASE": r"(?P<ts>.*?) \[DATABASE\] LEVEL=(?P<level>\w+) MSG=\"(?P<msg>.*)\""
}
