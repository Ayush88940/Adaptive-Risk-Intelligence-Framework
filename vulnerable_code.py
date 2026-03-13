# This file contains deliberate security vulnerabilities for testing purposes.
# DO NOT include this in a real production environment.

import os
import yaml
import subprocess
import pickle

def unsafe_operations():
    # 1. Hardcoded sensitive information (Bandit B105)
    SECRET_KEY = "super-secret-password-123"
    
    # 2. Use of eval() which is dangerous (Bandit B307)
    user_input = "print('system compromised!')"
    eval(user_input)
    
    # 3. Unsafe YAML loading (Bandit B506)
    # This allows for arbitrary code execution during deserialization
    untrusted_yaml = "!!python/object/apply:os.system ['ls']"
    data = yaml.load(untrusted_yaml)
    
    # 4. Insecure Shell Command Execution (Bandit B602)
    filename = "test.txt; rm -rf /"
    os.system(f"ls {filename}")
    
    # 5. Dangerous Deserialization with Pickle (Bandit B301)
    pickled_data = b'\x80\x03cposix\nsystem\nq\x00X\x06\x00\x00\x00whoamiq\x01\x85q\x02Rq\x03.'
    pickle.loads(pickled_data)

if __name__ == "__main__":
    unsafe_operations()
