# Reddit API Scripts

Various reddit API scripts

## Set up

To use them you will need a reddit app with OAuth access right to make the missing secret_keys.py file for the script (see secret_keys_empty.py for a template)

To set it up look at https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example and https://github.com/reddit-archive/reddit/wiki/OAuth2

The following excerpt can help you get the refresh token once the app is set up

```
# Generate token

# Fix and call this URL in your browser (fill the URL with what is needed, example of scope can be modflair%20flair, use %20 for multiple scopes)
# Request: https://www.reddit.com/api/v1/authorize?client_id=XXX_ID_XXX&response_type=code&state=XXX_randomString_XXX&redirect_uri=http://localhost:8080&duration=permanent&scope=XXX_DesiredScope_XXX
# You get a response with a Code to use in the script afterward
# Response: http://localhost:8080/?state=XXX_randomString_XXX&code=XXX_Code_XXX

# Small python script to get refresh token
# Fill the missing data with your APP data and the code you got
import requests
from requests.auth import HTTPBasicAuth
headers = requests.utils.default_headers()
headers.update({'User-Agent': 'XXX_MyUserAgent_XXX'})
auth=HTTPBasicAuth('XXX_ID_XXX', 'XXX_Secret_XXX')
url = 'https://www.reddit.com/api/v1/access_token'
data = {'grant_type': 'authorization_code', 'code': 'XXX_Code_XXX', 'redirect_uri': 'http://localhost:8080'}
x = requests.post(url, data = data, auth = auth, headers = headers)
print(x.text)

# You get a response with an access token (will expire anyways) and the refresh token to save
# Response: {"access_token": "XXX_AccessToken_XXX", "token_type": "bearer", "expires_in": 3600, "refresh_token": "XXX_RefreshToken_XXX", "scope": "XXX_Scope_XXX"}
```

See each script for the relevant scope required

## Flair Data

Get the flair usage data from a subreddit

## Active user test

Sort a list of users into active, old, dead and active but empty with regards to a cutoff timestamp.

## Usernotes Manipulation

Decode usernotes into readbale format and allow to purge users from it.