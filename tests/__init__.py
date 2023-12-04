import os
import sys

# Get the current directory (where conftest.py resides)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (root directory of the project)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the parent directory to PYTHONPATH
sys.path.insert(0, parent_dir)
