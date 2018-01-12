# zabbixBot
An Zabbix bot for chat channels, like Matrix.org

To send a alert, you use the command:
  - zabbixBot.py -a --room 'roomid'
The messages got send via STDIN in a JSON form.

This json has to have the following variables:
{"triggerStatus": "1", "host": "mgmt-test-01", "description": "test alert", "priority": "2"}

The zabbix action can have the following syntax:
Problem:
  {"triggerStatus": "1", "host": "{HOSTNAME} ({IPADDRESS})", "description": "{TRIGGER.NAME}", "priority": "{TRIGGER.NSEVERITY}"}

Recovery:
  {"triggerStatus": "0", "host": "{HOSTNAME} ({IPADDRESS})", "description": "{TRIGGER.NAME}", "priority": "{TRIGGER.NSEVERITY}"}
