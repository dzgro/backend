"""
Unit test specific fixtures and configuration.
"""

import pytest
import sys
import os

# Add parent directory to path to import base conftest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import all base fixtures
from conftest import *

# Additional unit-specific fixtures can be added here