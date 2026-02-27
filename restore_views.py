import subprocess
import os

os.chdir(r'd:\workplace_shop\WeWin')
subprocess.run(['git', 'checkout', 'HEAD', '--', 'Server/accounts/views.py'], check=True)
print('File restored successfully!')
