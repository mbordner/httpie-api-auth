"""
ApiAuth auth plugin for HTTPie.

"""
from httpie.plugins import AuthPlugin
import hmac, base64, hashlib, datetime
import urllib.parse

__version__ = '0.3.1'
__author__ = 'Kyle Hargraves'
__licence__ = 'MIT'

class ApiAuth:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password.encode('ascii')

    def __call__(self, r):
        method = r.method.upper()

        content_type = r.headers.get('content-type')
        if not content_type:
            if r.body != None and len(r.body) > 0:
                content_type = 'application/json'.encode('ascii')
            else:
                content_type = ''.encode('ascii')

        content_md5  = r.headers.get('content-md5')
        if not content_md5:
            if content_type:
                m = hashlib.md5()
                m.update(r.body)
                content_md5 = base64.standard_b64encode(m.digest()).decode('utf-8')
                r.headers['Content-MD5'] = content_md5
            else:
                content_md5 = ''

        httpdate = r.headers.get('date')
        if not httpdate:
            now = datetime.datetime.utcnow()
            httpdate = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
            r.headers['Date'] = httpdate

        url  = urllib.parse.urlparse(r.url)
        path = url.path
        if url.query:
          path = path + '?' + url.query

        string_to_sign = '%s,%s,%s,%s,%s' % (method, content_type.decode('ascii'), content_md5, path, httpdate)

        digest = hmac.new(self.password, string_to_sign.encode('ascii'), hashlib.sha1).digest()
        signature = base64.standard_b64encode(digest).decode('utf-8')

        r.headers['Authorization'] = 'APIAuth %s:%s' % (self.username, signature)
        return r

class ApiAuthPlugin(AuthPlugin):

    name = 'ApiAuth auth'
    auth_type = 'api-auth'
    description = 'Sign requests using the ApiAuth authentication method'

    def get_auth(self, username, password):
        return ApiAuth(username, password)
