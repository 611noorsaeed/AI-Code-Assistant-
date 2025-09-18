import subprocess, tempfile, os
import pygments.lexers

def run_code_snippet(code: str):
    """Run a Python snippet safely in a subprocess and return stdout/stderr."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
        f.write(code)
        temp_path = f.name
    try:
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)
    finally:
        os.unlink(temp_path)

def detect_language(code: str) -> str:
    """Detect programming language of code using Pygments."""
    try:
        lexer = pygments.lexers.guess_lexer(code)
        return lexer.name.lower()
    except Exception:
        return "unknown"
