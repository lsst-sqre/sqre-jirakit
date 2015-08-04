#!/usr/bin/env python

import oauth2 as oauth
import sys
import lsst.sqre.jirakit as jirakit  # helper code
import os
from tlslite.utils import keyfactory
import base64

class SignatureMethod_RSA_SHA1(oauth.SignatureMethod):
    name = 'RSA-SHA1'

    def signing_base(self, request, consumer, token):
        if not hasattr(request, 'normalized_url') or request.normalized_url is None:
            raise ValueError("Base URL for request is not set.")

        sig = (
            oauth.escape(request.method),
            oauth.escape(request.normalized_url),
            oauth.escape(request.get_normalized_parameters()),
        )

        key = '%s&' % oauth.escape(consumer.secret)
        if token:
            key += oauth.escape(token.secret)
        raw = '&'.join(sig)
        return key, raw

    def sign(self, request, consumer, token):
        """Builds the base signature string."""
        key, raw = self.signing_base(request, consumer, token)
        
        with open(os.path.expanduser('~/.ssh/jirakey.pem'), 'r') as f:
            data = f.read()
        privateKeyString = data.strip()

        privatekey = keyfactory.parsePrivateKey(privateKeyString)
        signature = privatekey.hashAndSign(raw)

        return base64.b64encode(signature)

consumer_key = 'oauth-sqre-consumer'
consumer_secret = 'dont_care'

request_token_url = 'https://jira.lsstcorp.org/plugins/servlet/oauth/request-token'
access_token_url = 'https://jira.lsstcorp.org/plugins/servlet/oauth/access-token'
authorize_url = 'https://jira.lsstcorp.org/plugins/servlet/oauth/authorize'

data_url = 'https://jira.lsstcorp.org/rest/api/latest/issue/DLP-516'

consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

(mytoken,mysecret) = jirakit.token(debug=True)

print mytoken
print mysecret

# Now lets try to access the same issue again with the access token. We should get a 200!
accessToken = oauth.Token(mytoken, mysecret)
client = oauth.Client(consumer, accessToken)
client.set_signature_method(SignatureMethod_RSA_SHA1())

resp, content = client.request(data_url, "GET")
print data_url
print resp['status']
print content
#if resp['status'] != '200':
#    raise Exception("Should have access!")
