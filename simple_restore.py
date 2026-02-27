import subprocess
import os

os.chdir(r'd:\workplace_shop\WeWin')
try:
    result = subprocess.run(
        ['git', 'checkout', 'HEAD', '--', 'Server/accounts/views.py'],
        capture_output=True,
        text=True
    )
    print('Return code:', result.returncode)
    print('STDOUT:', result.stdout)
    print('STDERR:', result.stderr)
except Exception as e:
    print('Error:', e)
