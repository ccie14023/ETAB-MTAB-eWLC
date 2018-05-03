import pexpect

RESET = """no vlan 200-290
no int vlan 200
no int vlan 250
no int vlan 252
no int vlan 255
no int vlan 256
no int vlan 270
no int vlan 280
no int vlan 290"""

def reset_cfg(device_ip, username, password):

	p=pexpect.spawn('ssh {}@{}'.format(username,device_ip))

	p.expect('word:')
	p.sendline(password)

	p.expect('#')
	p.sendline('conf t')
	p.expect('#')

	commands = RESET.splitlines()

	for command in commands:
		p.sendline(command)
		p.expect('#')





