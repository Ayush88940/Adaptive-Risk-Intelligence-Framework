import os
import yaml
import subprocess
import pickle

def unsafe_operations():
    SECRET_KEY = "super-secret-password-123"
    
    user_input = "print('system compromised!')"
    eval(user_input)
    
    untrusted_yaml = "!!python/object/apply:os.system ['ls']"
    data = yaml.load(untrusted_yaml)
    
    filename = "test.txt; rm -rf /"
    os.system(f"ls {filename}")
    
    pickled_data = b'\x80\x03cposix\nsystem\nq\x00X\x06\x00\x00\x00whoamiq\x01\x85q\x02Rq\x03.'
    pickle.loads(pickled_data)

if __name__ == "__main__":
    unsafe_operations()
