import subprocess
import os

os.chdir(r'd:\workplace_shop\WeWin')

try:
    result = subprocess.run(
        ['git', 'show', '479920f:Server/accounts/views.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        with open('Server/accounts/views.py', 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        print('File restored successfully!')
    else:
        print('Error:', result.stderr)
except Exception as e:
    print('Error:', e)
