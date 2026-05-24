import subprocess
result = subprocess.run(['bash', '-c', "ip -6 addr show wlan0 scope global | grep -oP 'inet6 \\K[^/]*'"], capture_output=True, text=True)
temp = subprocess.run(["vcgencmd","measure_temp"], capture_output=True, text=True)

print(temp.stdout)
#print("Return Code:", result.returncode)
print("Standard Output:\n", result.stdout)
#print("Standard Error:\n", result.stderr)