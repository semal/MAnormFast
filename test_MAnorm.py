import os


command = 'python MAnorm_entrance.py ' \
          '--p1 1-peaks.xls ' \
          '--r1 1-reads.bed ' \
          '--p2 2-peaks.xls ' \
          '--r2 2-reads.bed ' \
          '-s ' \
          '-o test'
print command
# os.system(command)