import os
import sys

root, ext = os.path.splitext(sys.argv[1])

if ext == '.py':
    filename = os.path.basename(sys.argv[1])
    with open(root + '.bat', 'w') as f:
        f.write('title {0:}\npython {0:}\npause\n'.format(filename))

elif ext == '.rb':
    filename = os.path.basename(sys.argv[1])
    with open(root + '.bat', 'w') as f:
        f.write('title {0:}\nruby {0:}\npause\n'.format(filename))
