#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required

from oauth2client.appengine import CredentialsProperty
from oauth2client.appengine import StorageByKeyName
from oauth2client.appengine import OAuth2WebServerFlow

from model import *

import os

from libgreader import GoogleReader
from libgreader.auth import GAPDecoratorAuthMethod

GOOGLE_URL = 'https://accounts.google.com'
AUTHORIZATION_URL = GOOGLE_URL + '/o/oauth2/auth'
ACCESS_TOKEN_URL = GOOGLE_URL + '/o/oauth2/token'

FLOW = OAuth2WebServerFlow(
    client_id='229095357872.apps.googleusercontent.com',
    client_secret='',
    scope=[
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.google.com/reader/api/',
    ],
    redirect_uri='http://vanewswatch.appspot.com/oauth2callback',
    user_agent='vanewswatch-1.0',
    auth_uri=AUTHORIZATION_URL,
    token_uri=ACCESS_TOKEN_URL)

class Credentials(db.Model):
  credentials = CredentialsProperty()

class MainHandler(webapp2.RequestHandler):
	@login_required
	def get(self):
		user = users.get_current_user()
		credentials = StorageByKeyName(Credentials, user.user_id(), 'credentials').get()
		
		if credentials is None or credentials.invalid == True:
			authorize_url = FLOW.step1_get_authorize_url('http://vanewswatch.appspot.com/oauth2callback')
			template_values = {
				'authurl': authorize_url
			}
			path = os.path.join(os.path.dirname(__file__), 'templates/template_authorize.html')
			self.response.out.write(template.render(path, template_values))
		else:
			# make it ajaxy - separate request for list of filters as json and dynamic listing
			filters = db.GqlQuery("SELECT * FROM NewsWatchFilter WHERE owner = :1", user)
			template_values = {
				'filters': filters
			}
			path = os.path.join(os.path.dirname(__file__), 'templates/template_filters.html')
			self.response.out.write(template.render(path, template_values))

class SubscriptionListHandler(webapp2.RequestHandler):
	@login_required
	def get(self):
		user = users.get_current_user()
		
		if user:
			storage = StorageByKeyName(Credentials, user.user_id(), 'credentials')
			credentials = storage.get()
			
			auth = GAPDecoratorAuthMethod(credentials)
			reader = GoogleReader(auth)
			reader.buildSubscriptionList()
			
			feeds = reader.getFeeds()
			template_values = {
				'feeds': feeds
			}
			path = os.path.join(os.path.dirname(__file__), 'templates/template_slist.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class OAuthHandler(webapp2.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    credentials = FLOW.step2_exchange(self.request.params)
    StorageByKeyName(
        Credentials, user.user_id(), 'credentials').put(credentials)
    self.redirect("/")

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/subscriptions', SubscriptionListHandler),
 	('/oauth2callback', OAuthHandler)],
                              debug=True)
