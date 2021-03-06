[![Build Status](https://travis-ci.org/deadc0de6/weegram.svg?branch=master)](https://travis-ci.org/deadc0de6/weegram)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

# WEEGRAM

This script allows to receive [telegram](https://telegram.org/) notifications from
[weechat](https://weechat.org/) when you are away and priv/highlight messages are received.

# Installation

Install by copying the script `weegram.py` in `~/.weechat/python/`

Load with
```
/script load weegram.py
```

To autoload, symlink it to `autoload`:
```bash
ln -s ~/.weechat/python/weegram.py ~/.weechat/python/autoload
```

# Usage

Quick start:
```
/script load weegram.py
/weegram help
```

The available options:
```
| weegram (status|enable|disable|chatid|token|withcontent|help)
|   status: get service status
|   enable [<time>]: enable service
|     - time: inactivity duration to activate (in min)
|   disable: disable service
|   chatid <id>: set chat-id
|   token <token>: set token
|   withcontent: toggle content in notification
|   help: get help
```

Set options by simply calling `weegram`, for example
```
/weegram chatid my-very-secret-chat-id
```

Get current settings with
```
/weegram status
```

# Get a telegram bot

To get a bot on [telegram](https://telegram.org/):

* talk to [botfather](https://telegram.me/BotFather)
* [create a new bot](https://core.telegram.org/bots#creating-a-new-bot) and retrieve the token (`/newbot`)
* start a chat with the newly created bot and say *hello*
* query `https://api.telegram.org/bot<TOKEN>/getUpdates` to get the *chat-id*

For more see: <https://core.telegram.org/bots#6-botfather>

# Contribution

If you are having trouble installing or using this script, open an issue.

If you want to contribute, feel free to do a PR (please follow PEP8).

# License

This project is licensed under the terms of the GPLv3 license.
