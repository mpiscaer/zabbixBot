from zabbixBotModule.matrixConnectorModule import matrixConnector
from configparser import SafeConfigParser
import logging

class chatConnector:
    """
    Connector to the diffrent chat networks
    chatter = chatConnector(chatProtocol, config_of_the_network, callback_to_save_data)

        chatProtocol = What pro protocol will be used
        config_of_the_network = Config of the networks
        callback_to_save_data = Callback to Save the data
    """
    def __init__(self, typeProtocol, config, updatePersistentData):
        if typeProtocol.lower() == "matrix":
            try:
                url = config['url']
                username = config['username']
                password = config['password']
                self.protocol = 'matrix'
            except:
                logging.error('One sessing is missing')

            try:
                token = config['token']
            except:
                token = None

            self.chatClient = matrixConnector(url, username, password, updatePersistentData, token)
        else:
            exit()

    def joinRoom(self, room):
        """ Join a Room
        room = obj.joinRoom(room_id_alias)
        """
        if self.protocol == 'matrix':
            self.chatClient.joinRoom(room)

    def start_listener_thread(self, onMessage):
        # Login to the rooms, to get the message out of the room
        self.chatClient.start_listener_thread(onMessage)

    def sendMessage(self, message, room):
        # Let the bot say something
        self.chatClient.sendMessage(message, room)
