import subprocess
import sys
from agent.models import ResponseError

def execute_python(code: str):
    try:
        result = subprocess.run(
            [sys.executable],
            input=code,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return "Code executed successfully but produced no output. Make sure to use print() to output your result."
        else:
            return f"Code execution failed: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Code execution timed out after 60 seconds."