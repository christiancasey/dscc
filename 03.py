#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 16:50:21 2019

@author: christiancasey

Test Box API
"""
import json
from boxsdk import JWTAuth
from boxsdk import Client

with open('345739_oqzyyy9w_config.json') as f:
	jsonCred = json.load(f)
	f.close()


print( jsonCred['boxAppSettings']['clientID'])
#%%

from boxsdk.network.default_network import DefaultNetwork
from pprint import pformat

class LoggingNetwork(DefaultNetwork):
    def request(self, method, url, access_token, **kwargs):
#        """ Base class override. Pretty-prints outgoing requests and incoming responses. """
#        print '\x1b[36m{} {} {}\x1b[0m'.format(method, url, pformat(kwargs))
#        response = super(LoggingNetwork, self).request(
#            method, url, access_token, **kwargs
#        )
#        if response.ok:
#            print '\x1b[32m{}\x1b[0m'.format(response.content)
#        else:
#            print '\x1b[31m{}\n{}\n{}\x1b[0m'.format(
#                response.status_code,
#                response.headers,
#                pformat(response.content),
#            )
        return response
							
from boxsdk import JWTAuth
from boxsdk import Client, OAuth2

def store_tokens(access_token, refresh_token):
 # store the tokens at secure storage (e.g. Keychain)
	print('store tokens()')


oauth2 = OAuth2(
													jsonCred['boxAppSettings']['clientID'], 
													jsonCred['boxAppSettings']['clientSecret'], 
													access_token = strAccessToken
													)
#
#
#client = Client(oauth2)#, LoggingNetwork())
#
#
#print(client.folder('0').get())



auth = JWTAuth(
    client_id=jsonCred['boxAppSettings']['clientID'],
    client_secret=jsonCred['boxAppSettings']['clientSecret'],
    enterprise_id=jsonCred['enterpriseID'],
    jwt_key_id=jsonCred['boxAppSettings']['appAuth']['publicKeyID'],
    rsa_private_key_file_sys_path=jsonCred['boxAppSettings']['appAuth']['privateKey'],
    rsa_private_key_passphrase=jsonCred['boxAppSettings']['appAuth']['passphrase'],
    store_tokens=store_tokens,
)

# Configure JWT auth object
#sdk = JWTAuth(jsonCred)

#client = Client(sdk)

#userid="*********"
#user=client.user(user_id = userid)

#%%

from boxsdk import DevelopmentClient
client = DevelopmentClient()


user = client.user().get()
print('The current user ID is {0}'.format(user.id))





















