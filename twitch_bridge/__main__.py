from twitch_bridge import JarbasTwitchBridge, platform
from jarbas_hive_mind import HiveMindConnection


def connect_twitch_to_hivemind(channel, oauth, tags,
                               host="wss://127.0.0.1",
                               crypto_key=None,
                               port=5678, name="JarbasTwitchBridge",
                               key="dummy_key", useragent=platform):
    con = HiveMindConnection(host, port)

    terminal = JarbasTwitchBridge(channel=channel,
                                  oauth=oauth,
                                  tags=tags,
                                  crypto_key=crypto_key,
                                  headers=con.get_headers(name, key),
                                  useragent=useragent)

    con.connect(terminal)


if __name__ == '__main__':
    # TODO argparse
    # get oauth https://www.twitchapps.com/tmi/
    PASS = "oauth:GET_YOUR_OAUTH_TOKEN"
    CHANNELNAME = "jarbasai"
    tags = ["@bot", "@jarbas", "@jarbasai"]
    connect_twitch_to_hivemind(CHANNELNAME, PASS, tags)
