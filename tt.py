import os
import sys

if len(sys.argv)>1:
    print(sys.argv)
else:
    os.execv(sys.executable, ['python'] + sys.argv + ['111'])
