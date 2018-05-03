import openpyxl
from ncclient import manager
import jinja2
import sys
import time
from misc import reset_cfg

HOST = "172.20.228.41"
USERNAME = "admin"
PASSWORD = "TM3adm!n"
XLS = "dataset.xlsx"

USAGE = """
The script will always read from a spreadsheet called "dataset.xls"
The host device, username and password are hardcoded into the script and need to be changed there.

vlan_config.py -s 
Set the specified config

vlan_config.py -d
Delete the specified config

"""

CONFIG_XML = """
<vlan>
	<vlan-list xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-vlan">
    	<id>{{ data["vlan"] }}</id>
  </vlan-list>
</vlan>

<interface>
	<Vlan>
		<name>{{ data["vlan"] }}</name>
		<ip>
			<address>
			  <primary>
			    <address>{{ data["ip"] }}</address>
			    <mask>255.255.255.0</mask>
			  </primary>
			</address>
			<helper-address>
              <address>{{ data["helper"] }}</address>
            </helper-address>
			{% if data["relay"] == "YES" %}
			<dhcp>
              <relay xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-dhcp">
                <information>
                  <option-insert/>
                </information>
              </relay>
            </dhcp>
			{% endif %}
		</ip>
	</Vlan>
</interface>
"""

DEL_XML = """

<vlan>
  <vlan-list xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-vlan">
    <id>{{ data["vlan"] }}</id>
  </vlan-list>
</vlan>

<interface>
	<Vlan xc:operation="delete">
		<name>{{ data["vlan"] }}</name>
</interface>

"""

def read_xls(workbook):

	wb = openpyxl.load_workbook(workbook)
	sheet = wb.get_active_sheet()

	data = []

	for row in range(2,sheet.max_row+1):
		data.append(
		{'vlan':str(sheet['A' + str(row)].value),
		'ip':sheet['B' + str(row)].value,
		'helper':sheet['C' + str(row)].value,
		'relay':sheet['D' + str(row)].value.upper()})

	return data

def render_xml(template,data):

	t = jinja2.Template(template)

	xml_data = t.render(data=data,trim_blocks=True, 
	lstrip_blocks=True)

	return xml_data

def set_config(snippet):

    with manager.connect(host=HOST, port=830,
    	username=USERNAME,password=PASSWORD, hostkey_verify=False) as m:
    	assert(":validate" in m.server_capabilities)
    	m.edit_config(target='running', config=snippet,
                  test_option='test-then-set',error_option=None)

if __name__ == '__main__':

	try:
		arg = sys.argv[1]
	except:
		print USAGE
		sys.exit()

	if arg == "-s":

		print "Reading data from spreadsheet..."
		data_set = read_xls(XLS)

		xml_data = """
		<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
		<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">"""

		print "Rendering XML data..."
		for vlan in data_set:
			xml_data += render_xml(CONFIG_XML, vlan)

		xml_data += "</native></config>"

		print "Pushing config to eWLC {}...".format(HOST)
		set_config(xml_data)
	elif arg == "-d":
		reset_cfg(HOST, USERNAME, PASSWORD)
	else:
		print USAGE


