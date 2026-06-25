# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'keyauthx.py'
# Bytecode version: 3.9.0beta5 (3425)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import os
import json as jsond
import time
from uuid import uuid4
import platform
import subprocess
import hmac
import hashlib
import requests
import win32security
class api:
    name = ownerid = secret = version = hash_to_check = ''
    def __init__(self, name, ownerid, secret, version, hash_to_check):
        if len(ownerid)!= 10 and len(secret)!= 64:
                print('Go to Manage Applications on dashboard, copy python code, and replace code in main.py with that')
                time.sleep(3)
                os._exit(1)
        self.name = name
        self.ownerid = ownerid
        self.secret = secret
        self.version = version
        self.hash_to_check = hash_to_check
        self.init()
    sessionid = enckey = ''
    initialized = False
    def init(self):
        if self.sessionid!= '':
            print('You\'ve already initialized!')
            time.sleep(3)
            os._exit(1)
        sent_key = str(uuid4())[:16]
        self.enckey = sent_key + '-' + self.secret
        post_data = {'type': 'init', 'ver': self.version, 'hash': self.hash_to_check, 'enckey': sent_key, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        if response == 'KeyAuth_Invalid':
            print('The application doesn\'t exist')
            time.sleep(3)
            os._exit(1)
        json = jsond.loads(response)
        if json['message'] == 'invalidver':
            if json['download']!= '':
                print('New Version Available')
                download_link = json['download']
                os.system(f'start {download_link}')
                time.sleep(3)
                os._exit(1)
            else:
                print('Invalid Version, Contact owner to add download link to latest app version')
                time.sleep(3)
                os._exit(1)
        if not json['success']:
            print(json['message'])
            time.sleep(3)
            os._exit(1)
        self.sessionid = json['sessionid']
        self.initialized = True
        if json['newSession']:
            time.sleep(0.1)
    def license(self, key, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = others.get_hwid()
        post_data = {'type': 'license', 'key': key, 'hwid': hwid, 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            self.__load_user_data(json['info'])
            print(json['message'])
        else:
            print(json['message'])
            time.sleep(3)
            os._exit(1)
    def checkinit(self):
        if not self.initialized:
            print('Initialize first, in order to use the functions')
            time.sleep(3)
            os._exit(1)
    def __do_request(self, post_data):
        try:
            response = requests.post('https://keyauth.win/api/1.2/', data=post_data, timeout=(15, 30))
            if 'signature' not in response.headers:
                print('cheking other url')
                response = requests.post('https://prod.keyauth.com/api/1.2/', data=post_data, timeout=(15, 30))
            key = self.secret if post_data['type'] == 'init' else self.enckey
            if post_data['type'] == 'log':
                return response.text
            else:
                client_computed = hmac.new(key.encode('utf-8'), response.text.encode('utf-8'), hashlib.sha256).hexdigest()
                signature = response.headers['signature']
                if not hmac.compare_digest(client_computed, signature):
                    print('Signature checksum failed. Request was tampered with or session ended most likely.')
                    print('Response: ' + response.text)
                    time.sleep(3)
                    os._exit(1)
                return response.text
        except requests.exceptions.Timeout:
            print('Request timed out. Server is probably down/slow at the moment')
    class application_data_class:
        numUsers = numKeys = app_ver = customer_panel = onlineUsers = ''
    class user_data_class:
        username = ip = hwid = expires = createdate = lastlogin = subscription = subscriptions = ''
    user_data = user_data_class()
    app_data = application_data_class()
    def __load_app_data(self, data):
        self.app_data.numUsers = data['numUsers']
        self.app_data.numKeys = data['numKeys']
        self.app_data.app_ver = data['version']
        self.app_data.customer_panel = data['customerPanelLink']
        self.app_data.onlineUsers = data['numOnlineUsers']
    def __load_user_data(self, data):
        self.user_data.username = data['username']
        self.user_data.ip = data['ip']
        self.user_data.hwid = data['hwid'] or 'N/A'
        self.user_data.expires = data['subscriptions'][0]['expiry']
        self.user_data.createdate = data['createdate']
        self.user_data.lastlogin = data['lastlogin']
        self.user_data.subscription = data['subscriptions'][0]['subscription']
        self.user_data.subscriptions = data['subscriptions']
class others:
    @staticmethod
    def get_hwid():
        if platform.system() == 'Linux':
            with open('/etc/machine-id') as f:
                hwid = f.read()
                return hwid
        else:
            if platform.system() == 'Windows':
                winuser = os.getlogin()
                sid = win32security.LookupAccountName(None, winuser)[0]
                hwid = win32security.ConvertSidToStringSid(sid)
                return hwid
            else:
                if platform.system() == 'Darwin':
                    output = subprocess.Popen('ioreg -l | grep IOPlatformSerialNumber', stdout=subprocess.PIPE, shell=True).communicate()[0]
                    serial = output.decode().split('=', 1)[1].replace(' ', '')
                    hwid = serial[1:(-2)]
                    return hwid
import sys
import hashlib
def getchecksum():
    md5_hash = hashlib.md5()
    target = sys.argv[0] if sys.argv and sys.argv[0] not in ('', '-') else __file__
    with open(target, 'rb') as file:
        md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest
use_key_auth = True
if use_key_auth:
    keyauthapp = api(name='hamza ben', ownerid='Y7sXHYnVt2', secret='06c9acae0e44feda99cd33b450505df5e710fab282553afc21938f67b7fad537', version='1.0', hash_to_check=getchecksum())
def ysd(key):
    if use_key_auth:
        keyauthapp.license(key)
        subs = keyauthapp.user_data.subscriptions
        for i in range(len(subs)):
            sub = subs[i]['subscription']
            timeleft = subs[i]['timeleft']
            if timeleft > 86400:
                time_left = int(timeleft / 60 / 60 / 24)
                txt = ' day(s)'
            else:
                if timeleft > 3600:
                    time_left = int(timeleft / 60 / 60)
                    txt = ' hour(s)'
                else:
                    if timeleft > 60:
                        time_left = int(timeleft / 60)
                        txt = ' min'
                    else:
                        time_left = int(timeleft)
                        txt = 's'
            print(f'[{i + 1} / {len(subs)}] | Subscription: {sub} - Timeleft: {timeleft}' + 's' + '/' + str(time_left) + txt)
            return (timeleft, time_left, txt)
    else:
        return (999999, 99999, ' day(s)')
