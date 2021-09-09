from ovos_utils import create_daemon
from jarbas_hive_mind.slave.terminal import HiveMindTerminalProtocol,\
    HiveMindTerminal
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message
from twitch_bridge.twitch import Twitch

platform = "JarbasTwitchBridgeV0.2"


class JarbasTwitchBridgeProtocol(HiveMindTerminalProtocol):

    def onOpen(self):
        super().onOpen()
        LOG.info("Twitch Channel: {0}".format(self.factory.channel))
        self.factory.start_twitch()

    def onClose(self, wasClean, code, reason):
        super().onClose(wasClean, code, reason)
        self.factory.twitch.stop_listening()


class JarbasTwitchBridge(HiveMindTerminal):
    protocol = JarbasTwitchBridgeProtocol

    def __init__(self, channel, oauth, tags=None, *args, **kwargs):
        super(JarbasTwitchBridge, self).__init__(*args, **kwargs)
        self.oauth = oauth
        self.channel = channel
        self.tags = tags or ["@bot"]
        self.twitch = Twitch(self.channel, self.oauth)
        self.twitch.on_message = self.on_twitch_message

    def start_twitch(self):
        create_daemon(self.twitch.listen)

    def on_twitch_message(self, username, message):
        utterance = message.lower().strip()
        should_answer = False
        for tag in self.tags:
            if tag.lower() in utterance:
                should_answer = True
                utterance = utterance.replace(tag.lower(), "")
        if self.client and should_answer:
            msg = {"data": {"utterances": [utterance], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {
                       "source": self.client.peer,
                       "destination": "hive_mind",
                       "platform": platform,
                       "user": {"twitch_username": username}}}
            self.send_to_hivemind_bus(msg)

    def speak(self, utterance, user_data):
        user = user_data["twitch_username"]
        utterance = "@{} , ".format(user) + utterance
        LOG.debug("Message: " + utterance)
        self.twitch.send_message(utterance)

    def handle_incoming_mycroft(self, message):
        assert isinstance(message, Message)
        user_data = message.context.get("user")

        if user_data:
            if message.msg_type == "speak":
                utterance = message.data["utterance"]
                self.speak(utterance, user_data)
            elif message.msg_type == "hive.complete_intent_failure":
                LOG.error("complete intent failure")
                utterance = 'I don\'t know how to answer that'
                self.speak(utterance, user_data)

