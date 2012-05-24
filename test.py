import os
import sys

oauth_key = "www.valabs.spb.ru"
oauth_secret = ""

def fix_path():
	sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/libgreader'))
	sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/httplib2-0.7.4/python2'))
	sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/python-oauth2'))

def main():
	auth = OAuthMethod(oauth_key, oauth_secret)
	auth.setRequestToken()
	print auth.buildAuthUrl()
	raw_input()
	auth.setAccessToken()
	reader = GoogleReader(auth)
	print reader.getUserInfo()

if __name__ == "__main__":
    fix_path()
    from libgreader import GoogleReader,OAuthMethod,Feed
    import oauth2 as oauth
    main()