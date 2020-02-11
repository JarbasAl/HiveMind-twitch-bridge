from twitch_bridge.twitch import Twitch


class EchoBot(Twitch):
    def on_message(self, username, message):
        self.send_message(message)

    def on_connect(self):
        self.send_message("I am EchoBot")


if __name__ == "__main__":
    # get oauth https://www.twitchapps.com/tmi/
    PASS = "oauth:GET_YOUR_OAUTH_TOKEN"
    CHANNELNAME = "jarbasai"

    twitch = EchoBot(CHANNELNAME, PASS)
    twitch.listen()
