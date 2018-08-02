import sys
import time
import datetime
import threading
import irc.bot
import requests
import secrets

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.channel_name = channel

        self.last_reminded = 0

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, token)], username, username)
        self.start_event_loop();
        

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)
 
        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        return

    def run_event_loop(self):
        c = self.connection

        # https://api.twitch.tv/kraken/streams/majorkilo
        url = 'https://api.twitch.tv/kraken/streams/' + self.channel_id
        headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()

        live_time = self.convert_time(r['stream']['created_at'])
        uptime = self.compare_time_to_now(live_time)

        if uptime > self.last_reminded + 15:
            self.last_reminded = uptime
            c.privmsg(self.channel, 'HEY, {}!!! Take a drink.'.format(r['stream']['channel']['display_name']))

        # r['created_at']

        self.start_event_loop()

    def start_event_loop(self):
        while True:
            try:
                threading.Timer(15, self.run_event_loop).start()
                break
            except:
                print("Error in tmr!")
    
    def convert_time(self, theTime):
        return datetime.datetime(*time.strptime(theTime, "%Y-%m-%dT%H:%M:%SZ")[:6])
    
    def compare_time_to_now(self, theTime):
        return (datetime.datetime.utcnow() - theTime).seconds

    def do_command(self, e, cmd):
        c = self.connection

        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])

        # Provide basic information to viewers for specific commands
        elif cmd == "raffle":
            message = "This is an example bot, replace this text with your raffle text."
            c.privmsg(self.channel, message)
        elif cmd == "schedule":
            message = "This is an example bot, replace this text with your schedule text."            
            c.privmsg(self.channel, message)

        # The command was not recognized
        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)

def main():
    username  = secrets.username
    client_id = secrets.twitch_client_id
    token     = secrets.oauth_token
    channel   = secrets.channel_name

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()