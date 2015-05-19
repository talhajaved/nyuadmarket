from authomatic.providers import oauth2, oauth1
from authomatic.providers.oauth2 import OAuth2

class NYUADProvider(OAuth2):
    # URL where the user will be redirected and asked to grant permissions to your app.
    user_authorization_url = 'http://passport.sg.nyuad.org/visa/oauth/authorize'
    # URL where your app will exchange the request_token for access_token.
    access_token_url = 'http://passport.sg.nyuad.org/visa/oauth/token'
    # API endpoint where you can get the user's profile info.
    user_info_url = 'http://passport.sg.nyuad.org/visa/use/info/me'

    # Optional minimum scope needed to get the user's profile info.
    user_info_scope = ['netID', 'school', 'class']
    
    #The AuthorizationProvider.type_id is a unique numeric ID
    #assigned to each provider used by serialization and deserialization of credentials. It is automatically generated from the PROVIDER_ID_MAP
    #Just override the type_id getter with a static property in your subclass with any integer greater than 16
    type_id = 1901 #100017
    
    @staticmethod
    def _x_user_parser(user, data):
        """
        Use this to populate the User object with data from JSON
        returned by provider on User.update().
        """      

        user.NetID = data.get('netID')
        user.school = data.get('school')
        user.classyear = data.get('class')
        user.groups = data.get('groups')
        
        return user

oauthconfig = {
    
    'nyuad': { # Your internal provider name
           
        # Provider class
        'class_': NYUADProvider,
        
        # NYUAD is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': "sawgq4gwargdfsf24f2rgg29rw91r",
        'consumer_secret': "aq2gqg88rwa8ug2f0f0f0if329ifew903",
        'scope' : NYUADProvider.user_info_scope
    }

}

# {
#     "id": 1901,
#     "name": "nyuadmarket",
#     "clientID": "sawgq4gwargdfsf24f2rgg29rw91r",
#     "clientSecret": "aq2gqg88rwa8ug2f0f0f0if329ifew903",
#     "scopes": [
#         "user.me.netID",
#         "user.me.class",
#         "user.me.school",
#         "user.me.groups"
#     ],
#     "trusted": false
# }
