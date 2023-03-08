import os
import sys
import datetime

date = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
print(date.hour,date.minute)

# if len(sys.argv)>1:
#     print(sys.argv)
# else:
#     os.execv(sys.executable, ['python'] + sys.argv + ['111'])
