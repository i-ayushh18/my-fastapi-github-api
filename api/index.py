import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'bytelyst-skillnest-web', 'python-api'))
from github_api import app  # Expose FastAPI app for Vercel 