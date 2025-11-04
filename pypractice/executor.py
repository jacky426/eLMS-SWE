# pypractice/executor.py
import subprocess
import tempfile
import os
import uuid
import time

def run_code(code: str, stdin: str = "", timeout: int = 5) -> dict:
    temp_dir = tempfile.mkdtemp()
    script_path = os.path.join(temp_dir, f"script_{uuid.uuid4().hex[:8]}.py")
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        start = time.time()
        result = subprocess.run(
            ['python', script_path],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout + 2
        )
        runtime = time.time() - start
        
        return {
            "output": result.stdout,
            "error": result.stderr,
            "runtime": round(runtime, 3),
            "timeout": False
        }
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Time limit exceeded", "runtime": timeout, "timeout": True}
    except Exception as e:
        return {"output": "", "error": str(e), "runtime": 0, "timeout": False}
    finally:
        try:
            os.remove(script_path)
            os.rmdir(temp_dir)
        except:
            pass