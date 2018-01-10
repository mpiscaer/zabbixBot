#!/usr/bin/python3.5
from zabbixBotModule.zabbixBotModule import zabbixBotClass
import sys, getopt
from sys import stdin
import fileinput
import os

def help():
    print('read_status.py [OPTION]')
    print('-h, --help                         display this help and exit')
    print('-d, --daemon                       listen for messages in deamon mode')
    print('-s, --standalone                   listen for messages in in standalone mode')
    print('    --say                          say something in a room --room is mandatory')
    print('    --room                         the room where the message needs tobe said')
    print('    --message                      the message is optional if not specified it will be via STDIN')

def main(argv):
    message = ""
    room = ""

    try:
        opts, args = getopt.getopt(argv,"shd", ["help", "daemon", "standalone", "say", "message=", "room="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    if len(opts) < 1:
        help()
        sys.exit(2)
    for opt, arg in opts:
        # modes that the bot can run.

        # 1st as an standalone
        # 2nd as an daemon
        # 3rd lets to bot say something

        if opt in ('-h', "--help"):
            help()
            sys.exit()
        elif opt in ("-d", "--daemon"):
            zabbixBot = zabbixBotClass()
            zabbixBot.daemon()
            sys.exit()
        elif opt in ("-s", "--standalone"):
            zabbixBot = zabbixBotClass()
            zabbixBot.standalone()
            sys.exit()
        elif opt in ("--say"):
            mode = "say"
        elif opt in ("--room"):
            room = arg
        elif opt in ("--message"):
            message = arg

    if mode == "say" and room != "" and message != "":
        saySomething(room, message)
    elif mode == "say" and room != "":
        saySomething(room, None)
    elif mode == "say":
        help()
        sys.exit()

def saySomething(room, message=None):
    zabbixBot = zabbixBotClass()
    if message == "" or message is None:
        for line in fileinput.input('-'):
            zabbixBot.say(line, room)
            pass
    else:
        zabbixBot.say(message, room)

if __name__ == '__main__':
    #check if the program as an argument
    main(sys.argv[1:])
