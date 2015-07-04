import nose
import sys

if nose.run(argv=['', 'menpobench']):
    sys.exit(0)
else:
    sys.exit(1)
