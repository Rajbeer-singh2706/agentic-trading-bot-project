
import os 
import sys 


print(os.path.dirname(__file__))
# D:\AI_PROJECTS\agentic-trading-bot-project

path = os.path.join(os.path.dirname(__file__), 'src')
print(f"path : {path}")
sys.path.insert(0, path)

from main_1 import app 


## python main.py
