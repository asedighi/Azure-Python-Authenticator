## Developer Instructions ##

azure_authenticate class attempts to get credentials for access for an application.  
It is a singleton class, and can be accessed with little 'construction'.  The current sample reads from a config json file, but the code attempts to read the needed config variables from envrionment variables.  


### Authentication ###
The class supports three types of authentication:
    
    -   Application and tenant authentication using service principals.  this is best used for remote access and developer env
    -   token-based authentication.  this is the jwt token we get when we authenticate.  
        -   If you have the jwt token, a lot of the steps are skipped
    -   Managed identity-based, which is used when we run on Azure and MSI is used
    -   cli-based authentication which uses a developers credentials to authenticate the app/user

### Developer Credentials ###
if you are developing on your local machine - you can attempt to use the config file.  The format for the config file is:

``` 
{
	"clientId": "xxxxxxxxxxx4-8d8b-4419-821a-d3e11f582871",
	"clientSecret": "xxxxxxxxxxxxxxx.Zb27y0DD~40.1As2ZZCDih",
	"tenantId": "72f9xxxx-xxxx-xxxx-xxxx-2d7cd011db47",
	"subscriptionId": "a436xxxx-xxxx-xxxx-xxxx-xxxx920cd8b2"
}

```
This example was taken from ```credentials.json.backup```

### Sample usage ####

```
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
```

