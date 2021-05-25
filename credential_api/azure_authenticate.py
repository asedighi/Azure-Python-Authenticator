import importlib
import inspect
import json
import logging
import os
import sys
import types

import jwt
from azure.common.credentials import (BasicTokenAuthentication,
                                      ServicePrincipalCredentials)
from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault import KeyVaultAuthentication, AccessToken

try:
    from azure.cli.core._profile import Profile
except Exception:
    Profile = None


class AzureAuthenticate:

    '''
    This is a singleton object.  We do not need more than one instance of this class.  
    '''
    _instance = None

    def __init__(self):
        '''
        Throw an exception if a ctor is explicitly called
        '''
        raise RuntimeError('Call instance() instead')


    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance of AzureAuthenticate')
            cls._instance = cls.__new__(cls)
            cls._instance.subscription_id = None
            cls._instance.credentials = None
            cls._instance.tenant_id = None
            cls._instance.resource = 'https://management.core.windows.net/' # 'https://vault.azure.net'
            cls._instance._is_token_auth = False
            cls._instance.access_token = None
            cls._instance._is_cli_auth = False

            '''
            this code will support three types of authentication:
            -   application and tenant authentication using service principals.  this is best used for remote access and developer env
            -   token-based authentication.  this is the jwt token we get when we authenticate.  
                    If you have the jwt token, a lot of the steps are skipped
            -   Managed identity-based, which is used when we run on Azure and MSI is used
            -   cli-based authentication which uses a developers credentials to authenticate the app/user
            '''
            tenant_auth_variables = [
                "TENANT_ID", "SUB_ID", "CLIENT_ID", "CLIENT_SECRET"
            ]

            token_auth_variables = [
                "ACCESS_TOKEN", "SUB_ID" 
            ]
            ### see: http://whatazurewebsiteenvironmentvariablesareavailable.azurewebsites.net/
            ### also, if MSI is enabled, the MSI_ENPOINT is set in the env.
            msi_auth_variables = [
                "MSI_ENDPOINT", "SUB_ID"
            ]

            
            if all(k in os.environ for k in msi_auth_variables):
                # MSI authentication
                if "CLIENT_ID" in os.environ:
                    cls._instance.credentials = MSIAuthentication(
                        client_id=os.environ["CLIENT_ID"],
                        resource=cls._instance.resource)
                else:
                    cls._instance.credentials = MSIAuthentication(
                        resource=cls._instance.resource)

                cls._instance.subscription_id = os.environ["SUB_ID"]
                print("Creating session with MSI Authentication")
            
            elif all(k in os.environ for k in tenant_auth_variables):
                # Tenant (service principal) authentication
                cls._instance.credentials = ServicePrincipalCredentials(
                    client_id=os.environ["CLIENT_ID"],
                    secret=os.environ["CLIENT_SECRET"],
                    tenant=os.environ["TENANT_ID"],
                    resource=cls._instance.resource)
                cls._instance.subscription_id = os.environ["SUB_ID"]
                cls._instance.tenant_id = os.environ["TENANT_ID"]
                print("Creating session with Service Principal Authentication")

            
            elif all(k in os.environ for k in token_auth_variables):
                # Token authentication
                cls._instance.credentials = BasicTokenAuthentication(
                    token={
                        'access_token': os.environ["ACCESS_TOKEN"]
                    })
                cls._instance.subscription_id = os.environ["SUB_ID"]
                print("Creating session with Token Authentication")
                cls._instance._is_token_auth = True

            
           
            else:
                # Azure CLI authentication
                cls._instance._is_cli_auth = True
                (cls._instance.credentials, cls._instance.subscription_id, cls._instance.tenant_id) = Profile().get_login_credentials(resource=cls._instance.resource)
                print("Creating session with Azure CLI Authentication")

            print("Session using Subscription ID: %s" % cls._instance.subscription_id)

            if cls._instance.credentials is None:
                print('Unable to locate credentials for Azure session.')


       

        return cls._instance


    def get_credentials(self):
        return self.credentials

    def get_subscription_id(self):
        return self.subscription_id


    def get_tenant_id(self):
        if self._is_token_auth:
            decoded = jwt.decode(self.credentials.token['access_token'], algorithms=["RS256"],  options={"verify_signature": False})
            return decoded['tid']
        return self.tenant_id

    def get_bearer_token(self):
        if self._is_cli_auth:
            return self.credentials._token_retriever()[1]
        return self.credentials.token['access_token']

    def get_access_token(self):
        if not self.access_token:
            t = self.get_bearer_token()
            self.access_token = AccessToken(token=t)
        return self.access_token


