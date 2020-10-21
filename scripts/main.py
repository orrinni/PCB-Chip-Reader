import subprocess
import shutil
import os
import sys

sys.path.append(os.getcwd())

from csv_generator import *

def get_parent_dir(n=1):
    """ returns the n-th parent dicrectory of the current
    working directory """
    current_path = os.path.dirname(os.path.abspath(__file__))
    for k in range(n):
        current_path = os.path.dirname(current_path)
    return current_path

def main():
    #Creates innerFolder
    inner = get_parent_dir(1) + "/images/innerFolder"
    os.mkdir(inner)
    
    #Call to outer model
    call_string = "python3 predict.py"
    subprocess.call(call_string, shell=True, cwd=os.getcwd())
    
    #Call to inner model
    call_string = "python3 predict2.py"
    subprocess.call(call_string, shell=True, cwd=os.getcwd())
    
    del_directory(inner)    

    
if __name__ == "__main__":
    main()
