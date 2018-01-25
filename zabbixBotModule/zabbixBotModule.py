from time import sleep
from zabbixBotModule.chatConnector import chatConnector
from zabbixBotModule.config import config
from pyzabbix import ZabbixAPI
import yaml, logging, time, json, sys

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
                severities = None
                # get the parameters of the command and lowercase them.
                # and the if the option is posible
                if message[7:].lower().startswith(("high")):
                    severities = 4
                if message[7:].lower().startswith(("average")):
                    severities = 3
                if message[7:].lower().startswith(("warning")):
                    severities = 2
                if message[7:].lower().startswith(("information")):
                    severities = 1

                zabbixBotClass.__commandoTop10(room, severities)

            elif message.startswith("!help"):
                zabbixBotClass.__commandoHelp(room)
            else:
                zabbixBotClass.__commandoUnkown(room)

    def __commandoUnkown(room):
        # There was an unknown command
        zabbixBotClass.chatter.sendMessage("I do not know this commando", room)

    def __commandoTop10(room, severitie=None):
        # There was asked for the top10 zabbix triggers

        logging.error("    severitie: " + str(severitie))

        if severitie is None:
            # get the zabbix triggers
            triggers = zabbixBotClass.zabbix.trigger.get(   only_true=1,
                                                            skipDependent=1,
                                                            monitored=1,
                                                            active=1,
                                                            output='extend',
                                                            expandDescription=1,
                                                            selectHosts=['host'],
                                                            sortfield='lastchange',
                                                            sortorder='DESC',
                                                            limit=10,
                                                            maintenance=False )

        else:
            # get the zabbix triggers
            triggers = zabbixBotClass.zabbix.trigger.get(   only_true=1,
                                                            min_severity=severitie,
                                                            skipDependent=1,
                                                            monitored=1,
                                                            active=1,
                                                            output='extend',
                                                            expandDescription=1,
                                                            selectHosts=['host'],
                                                            sortfield='lastchange',
                                                            sortorder='DESC',
                                                            limit=10,
                                                            maintenance=False )

        this_message = ""
        for trigger in triggers:
            """ Example 1
            this_message =  this_message +\
                "<u><strong>Timestamp:</u></strong> " + str(time.strftime('%d-%m-%y %H:%m', time.gmtime(int(trigger['lastchange'])))) + '<br>' +\
                " <u><strong>host:</u></strong> " + trigger['hosts'][0]['host'] + '<br>' +\
                " <u><strong>Tigger:</u></strong> '" + trigger['description'] + "'" + '<br>' +\
                " <font color=" + zabbixBotClass.__zabbixConvertIntToSeveritie(trigger['priority'])['color'] + "><u><strong>Severitie:</u></strong> "  + zabbixBotClass.__zabbixConvertIntToSeveritie(trigger['priority'])['name'] + "</font>" + '<br>' +\
                '<br>'
            """

            """ Example 2 """
            this_message = this_message + \
                str(time.strftime('%d-%m-%y %H:%m:%S', time.gmtime(int(trigger['lastchange'])))) + \
                " | <font color=" + zabbixBotClass.__zabbixConvertIntToTriggerStatus(trigger['value'])['color'] + ">" + zabbixBotClass.__zabbixConvertIntToTriggerStatus(trigger['value'])['name'] + "</font>"+ \
                " | <font color=#92ff24>" + trigger['hosts'][0]['host'] + "</font>" + \
                " | <font color=" + zabbixBotClass.__zabbixConvertIntToSeveritie(trigger['priority'])['color'] + ">" + trigger['description'] + "</font>" + \
                " | <font color=" + zabbixBotClass.__zabbixConvertIntToSeveritie(trigger['priority'])['color'] + ">" + zabbixBotClass.__zabbixConvertIntToSeveritie(trigger['priority'])['name'] + "</font>" + \
                '<br>'

        # no triggers found
        if len(this_message) == 0:
            this_message = "No triggers found"
        zabbixBotClass.chatter.sendMessage(this_message, room)

    def __commandoHelp(room):
        zabbixBotClass.chatter.sendMessage("At this moment we do know the following commands:", room)
        zabbixBotClass.chatter.sendMessage("<li>!top10 severity</li>", room)
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

    def alert(self, message, room):
        try:
            message = json.loads(message)
        except ValueError:
            raise ZabbixAPIException(
                "Unable to parse json: %s" % response.text
            )

        # check if the variables exists
        if 'priority' not in message:
            logging.error("Can not find priority in the json message")
            sys.exit()

        if 'triggerStatus' not in message:
            logging.error("Can not find triggerStatus in the json message")
            sys.exit()

        if 'host' not in message:
            logging.error("Can not find host in the json message")
            sys.exit()

        if 'description' not in message:
            logging.error("Can not find description in the json message")
            sys.exit()

        # composing the message
        this_message = ""
        this_message = this_message + \
            "<font color=" + zabbixBotClass.__zabbixConvertIntToTriggerStatus(message['triggerStatus'])['color'] + ">" + zabbixBotClass.__zabbixConvertIntToTriggerStatus(message['triggerStatus'])['name'] + "</font>"+ \
            " | <font color=#92ff24>" + message['host'] + "</font>" + \
            " | <font color=" + zabbixBotClass.__zabbixConvertIntToSeveritie(message['priority'])['color'] + ">" + message['description'] + "</font>" + \
            " | <font color=" + zabbixBotClass.__zabbixConvertIntToSeveritie(message['priority'])['color'] + \
            ">" + \
            zabbixBotClass.__zabbixConvertIntToSeveritie(message['priority'])['name'] + \
            '</font><br>'

        # sending the message
        zabbixBotClass.chatter.sendMessage(this_message, room)

    def __updatePersistentData(self, item, value):
        #print('Token: %s') % (value)
        print(value)
        return True

    def __zabbixConvertIntToSeveritie(severitieNumber):
        severitieNumberInt = int(severitieNumber)
        if severitieNumberInt == 5:
            return {
                'name': 'Disaster',
                'color': '#E45959',
                'number': 5 }
        if severitieNumberInt == 4:
            return {
                'name': 'High',
                'color': '#E97659',
                'number': 4 }
        if severitieNumberInt == 3:
            return {
                'name': 'Average',
                'color': '#FFA059',
                'number': 3 }
        if severitieNumberInt == 2:
            return {
                'name': 'Warning',
                'color': '#FFC859',
                'number': 2 }
        if severitieNumberInt == 1:
            return {
                'name': 'Information',
                'color': '#7499FF',
                'number': 1 }
        if severitieNumberInt == 0:
            return {
                'name': 'Not classified',
                'color': '#97AAB3',
                'number': 0 }
        return False

    def __zabbixConvertIntToTriggerStatus(problemNumber):
        problemNumberInt = int(problemNumber)
        if problemNumberInt == 0:
            return {
                'name': 'Resolved',
                'number': 0,
                'color': 'green'
                }
        if problemNumberInt == 1:
            return {
                'name': 'Problem',
                'number': 1,
                'color': 'red'
                }
