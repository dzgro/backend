# Import all fixtures from the parent shared_fixtures.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared_fixtures import *