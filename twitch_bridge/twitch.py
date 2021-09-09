import socket
from ovos_utils.log import LOG


class Twitch:
    def __init__(self, channel, oauth, nickname="bot", port=6667,
                 host="irc.twitch.tv"):
        self.nickname = nickname
        self.channel = channel
        self.oauth = oauth
        self.port = port
        self.host = host
        self._connected = False
        self._running = False
        self._socket = socket.socket()

    def connect(self):
        # Connecting to Twitch IRC by passing credentials and
        # joining a certain channel
        self._socket.connect((self.host, self.port))
        self._socket.send(
            b"PASS " + bytes(self.oauth, encoding="utf-8") + b"\r\n")
        self._socket.send(
            b"NICK " + bytes(self.nickname, encoding="utf-8") + b"\r\n")
        self._socket.send(
            b"JOIN #" + bytes(self.channel, encoding="utf-8") + b" \r\n")
        self._connected = True
        self.on_connect()

    def send_message(self, message):
        if not self._connected:
            self.connect()
        msg = bytes("PRIVMSG #" + self.channel + " :" + message + "\r\n",
                    encoding="utf-8")
        self._socket.send(msg)

    def listen(self):
        readbuffer = ""
        MODT = False
        if not self._connected:
            self.connect()
        self._running = True
        while self._running:
            try:
                readbuffer = readbuffer + \
                             self._socket.recv(1024).decode("utf-8")
                temp = readbuffer.split("\n")
                readbuffer = temp.pop()

                for line in temp:
                    # Splits the given string so we can work with it better
                    parts = line.split(":")
                    # Checks whether the message is PING because
                    # its a method of Twitch to check if you're afk
                    if parts[0].strip() == "PING":
                        msg = bytes("PONG %s\r\n" % parts[1], encoding="utf-8")
                        self._socket.send(msg)
                    else:
                        # Only works after twitch is done announcing stuff
                        # (MODT = Message of the day)
                        if not MODT:
                            for l in parts:
                                if "End of /NAMES list" in l:
                                    MODT = True
                            continue
                        if "QUIT" not in parts[1] and \
                                "JOIN" not in parts[1] and \
                                "PART" not in parts[1]:
                            try:
                                message = parts[2][:len(parts[2]) - 1]
                            except:
                                continue
                            # Sets the username variable to the actual username
                            username = parts[1].split("!")[0]
                            self.on_message(username, message)
            except socket.timeout:
                self.on_error("Socket timeout")
            except socket.error:
                self.on_error("Socket error")
            except Exception as e:
                self.on_error(str(e))

    def stop_listening(self):
        self._running = False
        self._connected = False
        self._socket.close()

    def on_connect(self):
        LOG.info("Connected to " + self.host)

    def on_message(self, username, message):
        LOG.info("Received Twitch message from: " + username)
        LOG.info("Message: " + message)

    def on_error(self, error):
        LOG.error(error)
        self.stop_listening()
        LOG.debug("Reconnecting...")
        self.listen()
