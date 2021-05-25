
from credential_api.azure_authenticate import AzureAuthenticate
import importlib
import inspect
import json
import logging
import os
import sys
import types



if __name__ == '__main__':
    
    with open('credentials.json') as json_data:
        cred = json.load(json_data)

        '''
        application or client id are the same
        '''
        os.environ["CLIENT_ID"] = cred['clientId'] 
        os.environ["CLIENT_SECRET"] = cred['clientSecret']
        os.environ["TENANT_ID"] = cred['tenantId']
        os.environ["SUB_ID"] = cred['subscriptionId']
        #os.environ["ACCESS_TOKEN"] = <get a token>



    cred = AzureAuthenticate.instance()
    ### you pass cred to functions that need credentials.

    t = cred.get_tenant_id()
    print ("tentant is: ", t)

    tken = cred.get_access_token()
    print ("Access token is: ", tken)
    ### tken can be used for REST HTTP calls.  the token is a jwt token


    print(cred.get_bearer_token())