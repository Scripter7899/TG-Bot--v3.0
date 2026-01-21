
import compileall
import os

print("Starting Project-Wide Syntax Check...")
try:
    # Recursively compile all python files in the current directory
    # force=True forces recompilation even if timestamps are up to date
    # quiet=1 prints only errors
    result = compileall.compile_dir('.', force=True, quiet=1)
    
    if result:
        print("\n✅ Syntax Check Passed: All files compiled successfully.")
    else:
        print("\n❌ Syntax Check Failed: Errors detected.")
        exit(1)
        
except Exception as e:
    print(f"Error during syntax check: {e}")
    exit(1)
