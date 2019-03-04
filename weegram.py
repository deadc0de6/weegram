'''
Receive telegram notification when you are away
and priv/highlight messages are received
Author: deadc0de6
Website: https://github.com/deadc0de6/weegram

Install by copying this file in ~/.weechat/python/

Load with
    /script load weegram.py
    or
    /python load weegram.py

To autoload, symlink it to autoload:
    ln -s ~/.weechat/python/weegram.py ~/.weechat/python/autoload

To get a bot on telegram:
    - talk to "botfather"
    - create a bot and retrieve the token (/newbot)
    - start a chat with the newly created bot and say hello
    - query "https://api.telegram.org/bot<TOKEN>/getUpdates" to get the chat-id
For more see: https://core.telegram.org/bots#6-botfather

Quick start:
    /script load weegram.py
    /weegram help
'''

import weechat as w
import requests
import urllib
import datetime

OK = w.WEECHAT_RC_OK
NOK = w.WEECHAT_RC_ERROR

C_B = w.color('bold')
C_NB = w.color('-bold')

NAME = 'weegram'
AUTHOR = 'deadc0de6'
VERSION = '0.1'
LICENSE = 'GPL-3.0'
DESC = 'Telegram notification on priv/highlight message'
CMD = NAME
CFGPATH = 'plugins.var.python.{}.*'.format(NAME)
SUBCMDS = [
    'status',
    'enable',
    'disable',
    'chatid',
    'token',
    'withcontent',
    'help']

SUBUSAGE = [
    '  {}status{}: get service status'.format(C_B, C_NB),
    '  {}enable [<time>]{}: enable service'.format(C_B, C_NB),
    '    - time: inactivity duration to activate (in min)'.format(C_B, C_NB),
    '  {}disable{}: disable service'.format(C_B, C_NB),
    '  {}chatid <id>{}: set chat-id'.format(C_B, C_NB),
    '  {}token <token>{}: set token'.format(C_B, C_NB),
    '  {}withcontent{}: content in notification'.format(C_B, C_NB),
    '  {}help{}: get help'.format(C_B, C_NB),
            ]
TG_URL = 'https://api.telegram.org'
TG_API = TG_URL + '/bot{}/sendMessage?chat_id={}&text={}'

DEFAULTS = {
    'enabled': 'off',
    'inactivity': '0',
    'token': '',
    'chatid': '',
    'withcontent': 'off',
           }

# variables
msghooks = []

############################################
# helpers
############################################


def error(string):
    w.prnt('', '{} ERROR: {}'.format(CMD, string))


def out(string):
    w.prnt('', '{}'.format(string))


def get_cfg(key):
    '''get config key'''
    if not w.config_is_set_plugin(key):
        w.config_set_plugin(key, DEFAULTS[key])
    return w.config_get_plugin(key)


def set_cfg(key, val):
    '''set config key'''
    w.config_set_plugin(key, str(val))


def init_cfg():
    '''init config defaults'''
    for opt, _ in DEFAULTS.items():
        get_cfg(opt)


def pstatus():
    '''print config status'''
    out('{} status:'.format(CMD))
    out('- enabled: {}'.format(get_cfg('enabled')))
    out('- inactivity: {}'.format(get_cfg('timer')))
    out('- token: {}'.format(get_cfg('token')))
    out('- chatid: {}'.format(get_cfg('chatid')))
    out('- withcontent: {}'.format(get_cfg('withcontent')))


def phelp():
    '''print usage'''
    out('{} ({})'.format(NAME, '|'.join(SUBCMDS)))
    out('\n'.join(SUBUSAGE))


def get_timer():
    '''return inactivity setting'''
    try:
        return int(w.config_get_plugin('inactivity'))
    except Exception:
        pass
    return 0

############################################
# telegram
############################################


def telegram(content):
    '''send notification to telegram bot'''
    token = get_cfg('token')
    chatid = get_cfg('chatid')
    if not token or not chatid:
        error('missing token or chatid')
        return False
    content = urllib.quote_plus(content)
    url = TG_API.format(token, chatid, content)
    r = requests.get(url)
    if r.status_code != 200:
        error('error {}: {}'.format(r.status_code, r.text))
        return False
    return True


def notify(nick, content, priv=True):
    '''process notification'''
    if get_cfg('enabled') != 'on':
        return OK
    timer = get_timer()
    if timer > 0:
        # timer is enabled
        idle = int(w.info_get('inactivity', '')) / 60
        if idle < timer:
            # not idle enough
            return OK
    dt = datetime.datetime.now().strftime('%Y%m%d-%H:%M')
    pre = 'priv message' if priv else 'message'
    post = ': {}'.format(content) if get_cfg('withcontent') == 'on' else ''
    content = '[{}] {} from \"{}\" on weechat{}'.format(dt, pre, nick, post)
    if not telegram(content):
        return NOK
    return OK

############################################
# callbacks
############################################


def command_cb(data, buffer, arg):
    '''parse script commands'''
    args = arg.strip(' ').split(' ')
    if args[0] == 'status':
        pstatus()
    elif args[0] == 'enable':
        if len(args) > 1:
            try:
                int(args[1])  # check for bad value
                set_cfg('inactivity', args[1])
            except Exception:
                error('bad inactivity value')
                return NOK
        set_cfg('enabled', 'on')
        manage_hooks()
        pstatus()
    elif args[0] == 'disable':
        set_cfg('enabled', 'off')
        manage_hooks()
        pstatus()
    elif args[0] == 'token':
        if len(args) < 2 or not args[1]:
            error('bad token')
            return NOK
        set_cfg('token', args[1])
        pstatus()
    elif args[0] == 'chatid':
        if len(args) < 2 or not args[1]:
            error('bad chatid')
            return NOK
        set_cfg('chatid', args[1])
        pstatus()
    elif args[0] == 'withcontent':
        cur = get_cfg('withcontent')
        new = 'off' if cur == 'on' else 'on'
        set_cfg('withcontent', new)
        pstatus()
    elif args[0] == 'help':
        phelp()
    else:
        error('unknown command: \"{}\"'.format(' '.join(args)))
        return NOK
    return OK


def config_cb(data, option, value):
    '''apply config change'''
    manage_hooks()
    return OK


def priv_cb(data, signal, signal_data):
    '''private message callback'''
    msg = w.info_get_hashtable('irc_message_parse', {'message': signal_data})
    nick = msg['nick']
    content = msg['text']
    return notify(nick, content)


def highlight_cb(data, signal, signal_data):
    '''highlight message callback'''
    fields = signal_data[1:].strip(' ').split()
    nick = fields[0]
    content = ' '.join(fields[1:])
    return notify(nick, content, priv=False)

############################################
# msg hooks
############################################


def manage_hooks():
    '''enable/disable hooks when config changes'''
    if get_cfg('enabled') == 'on':
        if not msghooks:
            add_hooks()
    else:
        del_hooks()


def del_hooks():
    '''unhook all hooks'''
    global msghooks
    for hook in msghooks:
        w.unhook(hook)
    msghooks = []


def add_hooks():
    '''add all hooks'''
    global msghooks
    hook = w.hook_signal('irc_pv', 'priv_cb', '')
    msghooks.append(hook)
    hook = w.hook_signal('weechat_highlight', 'highlight_cb', '')
    msghooks.append(hook)

############################################
# entry point
############################################


def init():
    '''init script'''
    w.hook_command(CMD, DESC,
                   '|'.join(SUBCMDS),    # args
                   '\n'.join(SUBUSAGE),  # args_description
                   '|'.join(SUBCMDS),    # completion
                   'command_cb',         # callback
                   '')

    # init config defaults
    init_cfg()

    # hook any config change
    w.hook_config(CFGPATH, 'config_cb', '')
    manage_hooks()


if __name__ == '__main__':
    if w.register(NAME, AUTHOR, VERSION, LICENSE, DESC, '', ''):
        init()
