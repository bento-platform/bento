import os
# import subprocess
from os import path
from os.path import join, dirname


ABS_PATH = dirname(path.abspath(__file__))

print(ABS_PATH)