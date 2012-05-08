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

import os
import random
import cgi
import urllib
import datetime
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

##### Key creator #####
def campaign_key(campaign_name=None):
	return db.Key.from_path('Add_Player', campaign_name or 'default')

##### Database Models #####
class Player(db.Model):
	name = db.StringProperty(multiline=False)
	level = db.IntegerProperty()
	xp = db.IntegerProperty()
	initiative = db.IntegerProperty()
	hp = db.IntegerProperty()
	campaign = db.StringProperty(multiline=False)

class Enemy(db.Model):
	name = db.StringProperty(multiline=False)
	cr = db.StringProperty(multiline=False)
	initiativemod = db.IntegerProperty()
	initiative = db.IntegerProperty()
	numDie = db.IntegerProperty()
	dieType = db.IntegerProperty()
	hpMod = db.IntegerProperty()
	hp = db.IntegerProperty()
	campaign = db.StringProperty(multiline=False)

##### Helper functions #####

### Player Functions ###

# Adds 'x' xp to the players total xp, then 
# calls the check level method.
def addxp( player, x): 
	player.xp = player.xp + int(x)
	checklevel(player)
	
# Removes 'x' xp to the players total xp.
def removexp(player, x): 
	player.xp = player.xp - int(x)	
	
# Sets the players level based on his current xp. 
def checklevel(player): 
	if player.xp < 2000:
		player.level = 1
	elif player.xp < 5000:
		player.level = 2
	elif player.xp < 9000:
		player.level = 3
	elif player.xp < 15000:
		player.level = 4
	elif player.xp < 23000:
		player.level = 5
	elif player.xp < 35000:
		player.level = 6
	elif player.xp < 51000:
		player.level = 7
	elif player.xp < 75000:
		player.level = 8
	elif player.xp < 105000:
		player.level = 9
	elif player.xp < 155000:
		player.level = 10
	elif player.xp < 220000:
		player.level = 11
	elif player.xp < 315000:
		player.level = 12
	elif player.xp <445000:
		player.level = 13
	elif player.xp < 635000:
		player.level = 14
	elif player.xp < 890000:
		player.level = 15
	elif player.xp < 1300000:
		player.level = 16
	elif player.xp < 1800000:
		player.level = 17
	elif player.xp < 2550000:
		player.level = 18
	elif player.xp < 3600000:
		player.level = 19
	else:
		player.level = 20
			
##### Functial Views #####
			
### Player ###
class AddPlayer(webapp.RequestHandler): 
	# Called by EncounterSetup
	def post(self):
		#Create a new player with a key derived from the campaign name.
		campaign_name = self.request.get('campaign_name')
		player = Player(parent=campaign_key(campaign_name)) 
		
		player.campaign = campaign_name
		player.name = self.request.get('name')	 	# Set name.
		player.xp = 0								# Set default xp to 0.
		addxp(player, int(self.request.get('xp')))	# Set xp to inputed. 	
		player.hp = int(self.request.get('hp'))		# Set hp.
													
		player.put()									# Store player in db.
		
		self.redirect('/encounterSetup?' + urllib.urlencode(
			{'campaign_name': campaign_name}))			# Redirect to visual view.
		
class RemovePlayer(webapp.RequestHandler):
	# Called by EncounterSetup
	def post(self):
		db.delete(self.request.get('key')) 				# Delete selected player 
	
		campaign_name = self.request.get('campaign_name')
		self.redirect('/encounterSetup?' + urllib.urlencode(
			{'campaign_name': campaign_name}))			# Redirect to visual view.
		
class RemoveAllPlayers(webapp.RequestHandler):
	# Called by EncounterSetup
	def post(self):
		campaign_name = self.request.get('campaign_name')
		players = Player.all().ancestor(campaign_key(
					campaign_name)).order('name')		# Delete all players in campaign.
		db.delete(players)
		self.redirect('/encounterSetup?' + urllib.urlencode(
			{'campaign_name': campaign_name}))			# Redirect to visual view.
			

### Enemy managing pages ###		
class AddEnemy(webapp.RequestHandler):
	# Called by EncounterSetup 
	def post(self):
		campaign_name = self.request.get('campaign_name')
		for x in range(int(self.request.get('iterations'))):
			enemy = Enemy(parent=campaign_key(campaign_name))	
			
			enemy.campaign = campaign_name
			enemy.name = self.request.get('name') + " " + str(x+1) 
			enemy.cr = self.request.get('cr')
			enemy.numDie = int(self.request.get('numHD'))
			enemy.dieType = int(self.request.get('dietype'))
			enemy.hpMod = int(self.request.get('mod'))
			enemy.initiativemod = int(self.request.get('initiativemod'))

			#Set HP	
			hpcalc = (enemy.numDie * random.randint(1,enemy.dieType)) + enemy.hpMod
			if hpcalc < 1:
				enemy.hp = 1
			else:
				enemy.hp = hpcalc
			
			inicalc = random.randint(1,20) + enemy.initiativemod
			if inicalc < 1:
				enemy.initiative = 1
			else:
				enemy.initiative = inicalc
		
			enemy.put()
		
		self.redirect('/encounterSetup?' + urllib.urlencode({'campaign_name': campaign_name}))
		
class RemoveEnemy(webapp.RequestHandler):
	# Called by EncounterSetup and EndEncounter
	def post(self):
		campaign_name = self.request.get('campaign_name')
		db.delete(self.request.get('key'))
		self.redirect('/encounterSetup?' + urllib.urlencode({'campaign_name': campaign_name}))
		
class RemoveAllEnemies(webapp.RequestHandler):
	# Called by EncounterSetup and EndEncounter
	def post(self):
		campaign_name = self.request.get('campaign_name')
		enemies = Enemy.all().ancestor(campaign_key(
					campaign_name)).order('name')	
		db.delete(enemies)
		self.redirect('/encounterSetup?' + urllib.urlencode(
			{'campaign_name': campaign_name}))
			
class EndEncounter(webapp.RequestHandler):
	def post(self):
		campaign_name = self.request.get('campaign_name')
	
		XPValue = { 
			"1/8":50, "1/6":65, "1/4":100, "1/3":135, "1/2":200, 
			"1":400, "2":600, "3":800, "4":1200, "5":1600, "6": 2400, 
			"7":3200 , "8":4800 , "9":6400 , "10":9600 , "11":12800 ,
			"12":19200 , "13":25600 , "14":38400 , "15":51200 , 
			"16":78800 , "17":102400 , "18":153600 , "19":204800 , 
			"20":307200 , "21":409600 , "22":614400 , "23":819200 , 
			"24":1228800 , "25":1638400 }
		totalXP = 0
		
		enemies = Enemy.all().ancestor(campaign_key(
					campaign_name)).order('name')	
		players = Player.all().ancestor(campaign_key(
						campaign_name)).order('name')	
				
		for enemy in enemies:
			if (enemy.hp <= 0):
				totalXP = totalXP + XPValue[enemy.cr]
				
		indXP = totalXP / players.count()
		
		for player in players:
			addxp(player, indXP)
			checklevel(player)
			player.put()
		
		db.delete(enemies)
		self.redirect('/encounterSetup?' + urllib.urlencode(
			{'campaign_name': campaign_name}))
			


class ChangeHp(webapp.RequestHandler):
	def post(self):
		campaign_name = self.request.get('campaign_name')

		player = Player.get(self.request.get("key"))		
		
		player.hp += int(self.request.get('change'))
		player.put()
			
		self.redirect('/encounter?' + urllib.urlencode(
			{'campaign_name': campaign_name}))


	def post(self):
		campaign_name = self.request.get('campaign_name')		
		PoE = self.request.get('PoE') #Player or Enemy

		if PoE == "player":
			character = Player.get(self.request.get("key"))
		else:
			character = Enemy.get(self.request.get("key"))		

		character.hp += int(self.request.get('change'))
		character.put()

		self.redirect('/encounter?' + urllib.urlencode(
			{'campaign_name': campaign_name}))

			
##### Visual Views #####

### Campaign Selector ###		
# User inputs the name of their campaign and are redirected to 
# the encounter setup visual view.
class CampaignSelect(webapp.RequestHandler):
	# First page visited.
    def get(self):	
	   	user = users.get_current_user()

	   	if user:
	   		template_values = {	} # No template values needed.
			path = os.path.join(os.path.dirname(__file__), 'campaignSelect.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

### Encounter Setup ###			
# User creates PC and NPC. This view calls several 
# functional views
class EncounterSetup(webapp.RequestHandler):
	# Called by campaign select. 
	def get(self):
		user = users.get_current_user()

	   	if user:
			campaign_name = user.nickname()
			players = Player.all().ancestor(campaign_key(
						campaign_name)).order('name')	
			enemies = Enemy.all().ancestor(campaign_key(
						campaign_name)).order('name')	
			
			numPlayers = players.count()
			numEnemies = enemies.count()
		
			template_values = {
				'players' : players,
				'enemies' : enemies,
				'numPlayers' : numPlayers,
				'numEnemies' : numEnemies,
				'campaign_name' : campaign_name
				}
		
			path = os.path.join(os.path.dirname(__file__), 'encounterSetup.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class PlayerInitiative(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()

	   	if user:
			campaign_name = self.request.get('campaign_name')
			players = Player.all().ancestor(campaign_key(
							campaign_name)).order('name')
			numPlayers = players.count()
			template_values = {
				'players' : players,
				'numPlayers' : numPlayers,
				'campaign_name' : campaign_name
			}

			path = os.path.join(os.path.dirname(__file__), 'playerInitiative.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

	def post(self):
		user = users.get_current_user()

	   	if user:
			campaign_name = self.request.get('campaign_name')
			players = Player.all().ancestor(campaign_key(
							campaign_name)).order('name')
			for player in players:
				string = str(player.name) + "-" + str(player.xp)
				player.initiative = int(self.request.get(string))
				player.put()
			
				self.redirect('/encounter?' + urllib.urlencode(
					{'campaign_name': campaign_name}))
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
class Encounter(webapp.RequestHandler):
	def get(self):

		user = users.get_current_user()

		if user:

			campaign_name = self.request.get('campaign_name')
			players = Player.all().ancestor(campaign_key(
						campaign_name)).order('-initiative')	
			enemies = Enemy.all().ancestor(campaign_key(
						campaign_name)).order('-initiative')	
			
			template_values = {
				'players' : players,
				'enemies' : enemies,
				'campaign_name' : campaign_name
				}
			
			
			path = os.path.join(os.path.dirname(__file__), 'encounter.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class Home(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		url = 0
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			username = user.nickname()
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
			username = ""
		template_values = {
				'url': url,
				'url_linktext': url_linktext,
				'username': username,
			}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

		
			
def main():
    application = webapp.WSGIApplication([('/', Home),
										('/encounterSetup', EncounterSetup),
										('/encounter', Encounter),
										('/endEncounter', EndEncounter),
										('/addPlayer', AddPlayer),
										('/removePlayer', RemovePlayer),
										('/removeAllPlayers', RemoveAllPlayers),
										('/addEnemy', AddEnemy),
										('/removeEnemy', RemoveEnemy),
										('/removeAllEnemies', RemoveAllEnemies),
										('/changeHp', ChangeHp),
										('/initiative', PlayerInitiative)
										], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
