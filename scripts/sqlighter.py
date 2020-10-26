import sqlite3

from PSstore import PSstore
from random import choice

class SQlighter:

	phrases = ["Sorry, I don`t remember such games", "Can`t remember these ones...", 
					"I don`t know such games", "These game names are unfamiliar to me"]

	def __init__(self, database_file):
		"""Connect to the db and create 'cursor' object"""
		self.connection = sqlite3.connect(database_file, check_same_thread = False)
		self.cursor = self.connection.cursor()

	def game_exists(self, gameName):
		"""Check if the game exists"""
		with self.connection:
			result = self.cursor.execute("SELECT * FROM games WHERE game = ?", (gameName,)).fetchall()
			return bool(len(result)) # if the game doesn`t exist, len(result) = 0 = False

	def add_game(self, gameName):
		"""Add the game to the db"""
		with self.connection:
			game_list = SQlighter("gamesdb.db").get_games() # get a list of the games
			if game_list: # check if the db exists
				for game in game_list: # check if the game is already in the db
					if gameName == game.replace(" ", "_"):
						return True

				# the games that are not in the db we add
				self.cursor.execute("INSERT INTO games VALUES(?, ?)", (gameName, False))
				return False

			else: # if not, we just add without checking
				self.cursor.execute("INSERT INTO games VALUES(?, ?)", (gameName, False))
				return False

	def remove_game(self, gameName):
		"""Delete a game from the db"""
		with self.connection:
			if SQlighter("gamesdb.db").game_exists(gameName): # check if the game exists
				self.cursor.execute("DELETE FROM games WHERE game = ?", (gameName,))
				return gameName
			else: # if the game does not exist
				return False

	def show_discount(self, db_games):
		"""Returns a list of discounted games"""
		if db_games is False: # check if the db is empty
			return "You haven`t told me any games yet😕"

		else:
			result = PSstore().find_games(db_games) # get discounted games

			""" set 'discount' column in the db to 'True' if there are games from the db in the
				'result' argument """
			games_ondisc = []
			if type(result) is list: # check if there are games in the 'result' argument
				for result_el in result:
					for db_el in db_games:
						if result_el[-1] == db_el:
							games_ondisc.append(db_el)

					result_el.remove(result_el[-1])

			# set 'discount' column to True, if its game is in the 'games_ondisc' argument
			SQlighter("gamesdb.db").update_discounts(games_ondisc) 

			return result

	def update_discounts(self, db_games):
		"""Set 'discount' column to 'True' """
		with self.connection:
			for db_game in db_games:
				self.cursor.execute("UPDATE games SET discount = ? WHERE game = ?", (True, db_game.replace(" ", "_")))

	def get_games(self):
		"""Get all the games from the db"""
		with self.connection:
			db_games = self.cursor.execute("SELECT * FROM games").fetchall()
			if db_games: # check if the db is empty
				for i in range(0, len(db_games)):
					db_games[i] = db_games[i][0].strip().replace("_", " ")

				return db_games

			else:
				return False

	def edit_usermsg(self, msg):
		"""Edit 'msg' argument to send it to the user"""
		if type(msg) is list: # if there are games
			fullmessage = ""
			for el in msg:
				fullmessage += (el[0] + ":  " + el[2] + "  (" + el[1] + " - fullprice)" + " - " + el[3] + "\n" + el[4] + "\n\n")

			return fullmessage[:-1]

		else:
			return msg

	def edit_dbmsg(self, msg):
		"""Edit the 'msg' argument in the necessary format (for the db)"""
		dbmsg = msg.replace(" ", "_").lower().split(",")

		for i in range(0, len(dbmsg)):
			if dbmsg[i].startswith("_"):
				dbmsg[i] = dbmsg[i][1:]

		return dbmsg