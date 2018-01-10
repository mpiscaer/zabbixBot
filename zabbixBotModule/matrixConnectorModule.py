from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema
import sys
import logging

class matrixConnector:
    """
    Connector to the Matrix network

    Example:
    matrixObj = MatrixConnector(url, username, password, updatePersistentData, token)
        url = the url to the matrix server
        username = the username of the matrix Server
        password = the password of the matrix user
        updatePersistentData = Callback to the function to save the learned token
        token = the token of this client, we will resived this at the first connection.
    """

    # declare the variable
    __rooms = {}


    def __init__(self, url, username, password, updatePersistentData, token=None ):
        # save my own name
        matrixConnector.username = username
        if token is None:
            # Try to login with username and password
            self.__client = MatrixClient(url)
            try:
                self.__token = self.__client.login_with_password(username, password)
                # save the token
                value = self.__token
                updatePersistentData('matrix_token', value)

            except MatrixRequestError as e:
                print(e)
                if e.code == 403:
                    print("Bad username or password.")
                    sys.exit(4)
                else:
                    print("Check your sever details are correct.")
                    sys.exit(2)
            except MissingSchema as e:
                print("Bad URL format.")
                print(e)
                sys.exit(3)
        else:
            # Try to login with token
            try:
                self.__client = MatrixClient(url, token, username)
                print("UserId:", self.__client.user_id)
            except MatrixRequestError as e:
                print(e)
                if e.code == 403:
                    print("Bad username or password.")
                    sys.exit(4)
                else:
                    print("Check your sever details are correct.")
                    sys.exit(2)
            except MissingSchema as e:
                print("Bad URL format.")
                print(e)
                sys.exit(3)

    def joinRoom(self, room_id_alias):
        """ Join a Room
        room = obj.joinRoom(room_id_alias)
        """

        roomID = room_id_alias

        if room_id_alias.startswith("#"):
            roomID = self.__client.api.get_room_id(room_id_alias)


        if roomID not in self.discoverJoinedRooms().keys():
            return False

        try:
            room = self.__client.join_room(roomID)
        except MatrixRequestError as e:
            print(e)
            if e.code == 400:
                print("Room ID/Alias in the wrong format")
                sys.exit(11)
            else:
                print("Couldn't find room.")
                sys.exit(12)

        self.__rooms[roomID] = room

    def discoverJoinedRooms(self):
        # Discover what rooms the user has joined
        return self.__client.get_rooms()

    def start_listener_thread(self, onMessage):
        # Login to the rooms, to get the message out of the room
        matrixConnector.onMessage = onMessage
        self.__client.add_listener(self.__onEvent)
        self.__client.start_listener_thread()

    def __onEvent(room, event):
        # get the events out of the room
        message = event["content"]["body"]
        roomId = event["room_id"]
        matrixConnector.onMessage(message, roomId)
        print(matrixConnector.username)
        print(event)

    def sendMessage(self, message, roomId):
        # Let the bot say something
        self.__rooms[roomId].send_html(message)
        #print("roomId:", roomId)
