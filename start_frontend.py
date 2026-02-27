import os
import subprocess
import sys

os.environ['NODE_OPTIONS'] = '--openssl-legacy-provider'
os.chdir(r'd:\workplace_shop\WeWin\Page')

print("Starting frontend server...")
print("NODE_OPTIONS set to:", os.environ.get('NODE_OPTIONS'))

try:
    result = subprocess.run(['pnpm', 'serve'], shell=True)
    sys.exit(result.returncode)
except KeyboardInterrupt:
    print("\nServer stopped by user")
    sys.exit(0)
