import sys
import os

print("--- sys.path from tests/conftest.py ---")
for p in sys.path:
    print(p)
print("--- current working directory ---")
print(os.getcwd())
print("-------------------------------------") 