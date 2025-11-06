import os
import stat
import math

def handle_rm_error(func, path, _):
    """
    Error handler for shutil.rmtree that handles read-only files.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise
    
def calculate_shannon_entropy(data):
    if not data:
        return 0
    
    entropy = 0
    for char in set(data):
        freq = float(data.count(char)) / len(data)
        entropy -= freq * math.log(freq, 2)
    return entropy