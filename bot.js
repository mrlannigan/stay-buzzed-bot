const TwitchBot = require('twitch-bot');
const secrets = require('./secrets');
const topChannels = require('./streams.json');

exports.start = () => {
  let byteCount = 0;
  let lastCount = 0;

  const Bot = new TwitchBot({
    username: secrets.username,
    oauth: secrets.oauth_token,
    channels: [secrets.username]
  });

  const _origWrite = Bot.irc.write;
  Bot.irc.write = function (msg) {
    console.log(msg);
    return _origWrite.apply(this, arguments);
  }

  Bot.on('join', (channel) => {
    console.log(`Joined ${channel}`);
  });

  Bot.on('part', (channel) => {
    console.log(`Left ${channel}`);
  });

  Bot.on('message', chatter => {

    byteCount += chatter.message.length;

    if (chatter.channel === `#${secrets.username}`) {
      switch (chatter.message) {
        case '!join':
          Bot.join(chatter.username);
          break;
        case '!leave':
          Bot.part(chatter.username);
          break;
      }
    }

    if(chatter.message === '!test') {
      console.log('Got the command');
      Bot.say('Command executed! PogChamp', chatter.channel)
    }
  });

  Bot.on('error', err => {
    console.log(err)
  });

  setTimeout(() => {
    topChannels.data.forEach((channel) => {
      Bot.join(channel.user_name);
    })
  }, 1000)

  const counter = () => {
    lastCount += byteCount;
    console.log(`Delta: ${byteCount} ... Total: ${lastCount}`);

    byteCount = 0;
    setTimeout(counter, 5000);
  }

  setTimeout(counter, 5000);

}
