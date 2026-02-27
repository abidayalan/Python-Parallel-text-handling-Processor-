from concurrent.futures import ThreadPoolExecutor
import os

def run_parallel(function, data):
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(function, data))
    return results