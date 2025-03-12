# flake8: noqa
import ast
import os

from .base import *

try:
    from .local import *
except ImportError:
    print('Not found local.py')

for var in list(locals()):
    value = os.getenv(var)
    if value is None:
        continue
    try:
        locals()[var] = ast.literal_eval(value)
    except:
        locals()[var] = value
