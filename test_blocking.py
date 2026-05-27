import pexpect
import sys

# We will spawn the app, wait 1 second, send a command, and then IMMEDIATELY send another command
# or ctrl+c while it's processing to see if the interface crashed or queued correctly.
# AILOEngine's dummy command sleeps for 2 seconds.

child = pexpect.spawn('python3 ailo_engine.py', encoding='utf-8')
child.logfile = sys.stdout

# Wait for prompt
child.expect('AILO-Router', timeout=5)

# Send a long running command
child.sendline('long command')

# We expect it to print that it is processing in the background immediately
child.expect('Processing command', timeout=5)

# Now wait for the result
child.expect('Success:', timeout=5)

# Issue exit
child.sendline('/exit')
child.expect(pexpect.EOF)
