from time import sleep
from zabbixBotModule.chatConnector import chatConnector
from zabbixBotModule.config import config
from pyzabbix import ZabbixAPI
import yaml
import logging
import time

class zabbixBotClass:
    chatter = ""
    zabbix = ""

    def __init__(self):
        # load configure items
        self.global_config = config('global')

        # load the path
        self.dataFile = self.global_config.getConfigEntry('data_file')

        # configure logging
        logging.basicConfig(level=logging.INFO )

        self.__loadZabbix()

        self.__loadChatProtocol()
        self.__joinRooms()


    def __loadChatProtocol (self):
        # load the chatProtocol
        self.chatProtocolName = self.global_config.getConfigEntry('chatProtocol')
        self.chatProtocolConfig = config(self.chatProtocolName)

        zabbixBotClass.chatter = chatConnector(self.chatProtocolName, self.chatProtocolConfig.dump(), self.__updatePersistentData)

    def __loadZabbix (self):
        self.zabbixConfig = config('zabbix')

        url = self.zabbixConfig.getConfigEntry('url')
        username = self.zabbixConfig.getConfigEntry('username')
        password = self.zabbixConfig.getConfigEntry('password')

        zabbixBotClass.zabbix = ZabbixAPI(url)
        zabbixBotClass.zabbix.login(username, password)

    def __joinRooms(self):

        roomNames = self.chatProtocolConfig.getConfigEntry('channels')

        if type(roomNames) is str:
            bufferRoomNames = []
            bufferRoomNames.append(roomNames)
            roomNames = bufferRoomNames

        self.rooms = {}
        #try:
        for roomName in roomNames:
            zabbixBotClass.chatter.joinRoom(roomName)

        #except:
        #    logging.error("A problem with joining a room")

    def __listenToTheRooms(self):
        # Login to the rooms, to get the message out of the room
        zabbixBotClass.chatter.start_listener_thread(zabbixBotClass.__onMessage)

    def __onMessage(message, room):
        # Get the messages out of the room
        zabbixBotClass.__checkIfitsCommando(message, room)

    def __checkIfitsCommando(message, room):
        # check if if the was commando
        if message.startswith("!"):
            if message.startswith("!top10"):
                zabbixBotClass.__commandoTop10(room)
            elif message.startswith("!help"):
                zabbixBotClass.__commandoHelp(room)
            else:
                zabbixBotClass.__commandoUnkown(room)

    def __commandoUnkown(room):
        # There was an unknown command
        zabbixBotClass.chatter.sendMessage("I do not know this commando", room)

    def __commandoTop10(room):
        # There was asked for the top10 zabbix triggers

        # get the zabbix triggers
        triggers = zabbixBotClass.zabbix.trigger.get(   only_true=1,
                                                        skipDependent=1,
                                                        monitored=1,
                                                        active=1,
                                                        output='extend',
                                                        expandDescription=1,
                                                        selectHosts=['host'],
                                                        )

        print(triggers)
        zabbixBotClass.chatter.sendMessage("top10", room)

    def __commandoHelp(room):
        zabbixBotClass.chatter.sendMessage("At this moment we do know the following commands:", room)
        zabbixBotClass.chatter.sendMessage("<li>!top10</li>", room)
        zabbixBotClass.chatter.sendMessage("<li>!help</li>", room)

    def standalone(self):
        # run the program as standalone
        logging.info('Starting in standalone mode')

        self.__listenToTheRooms()

        while True:
            sleep(1);
        return True

    def daemon(self):
        # run the program as daemon
        logging.error('This mode is currently not supported')
        return False

    def say(self, message, room):
        # Let the bot say something
        # say(message, room)
        zabbixBotClass.chatter.sendMessage(message, room)
        return True

    def __updatePersistentData(self, item, value):
        #print('Token: %s') % (value)
        print(value)
        return True
