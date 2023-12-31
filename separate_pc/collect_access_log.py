import paramiko
import re
import json
import os
from ipaddress import ip_address, ip_network

# Function to check if an IP address is public
def is_public_ip(ip):
    private_networks = [
        ip_network('10.0.0.0/8'),
        ip_network('172.16.0.0/12'),
        ip_network('192.168.0.0/16')
    ]
    ip_addr = ip_address(ip)
    return not any(ip_addr in network for network in private_networks)

# SSH Connection Information
hostname = 'raspberrypi'  # or the IP address of your Raspberry Pi
username = 'your_username'
password = 'your_password'
log_file_path = '/var/log/apache2/access.log'

# Regular Expression for IP Address
ip_regex = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

# Connect to Raspberry Pi via SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

# Execute Command to Read access.log
stdin, stdout, stderr = ssh.exec_command(f'cat {log_file_path}')
log_content = stdout.read().decode()

# Extract IP Addresses
ip_addresses = re.findall(ip_regex, log_content)

# Load existing data if available
ip_data = {}
if os.path.exists('extracted.json'):
    with open('extracted.json', 'r') as file:
        ip_data = json.load(file)

# Update counts for public IPs
for ip in ip_addresses:
    if is_public_ip(ip):
        if ip in ip_data:
            ip_data[ip] += 1
        else:
            ip_data[ip] = 1

# Save updated data to JSON file
with open('extracted.json', 'w') as file:
    json.dump(ip_data, file, indent=4)

# Close SSH Connection
ssh.close()

print("Public IP addresses extracted and saved to extracted.json")
