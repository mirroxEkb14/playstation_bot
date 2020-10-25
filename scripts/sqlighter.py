import sqlite3

from PSstore import PSstore
from random import choice

class SQlighter:

	phrases = ["Sorry, I don`t remember such games", "Can`t remember these ones...", 
					"I don`t know such games", "These game names are unfamiliar to me"]

	def __init__(self, database_file):
		self.connection = sqlite3.connect(database_file, check_same_thread = False)
		self.cursor = self.connection.cursor()

	def game_exists(self, gameName):
		with self.connection:
			result = self.cursor.execute("SELECT * FROM games WHERE game = ?", (gameName,)).fetchall()
			return bool(len(result))

	def add_game(self, gameName):
		with self.connection:
			game_list = SQlighter("gamesdb.db").get_games()
			if game_list:
				for game in game_list:
					if gameName == game.replace(" ", "_"):
						return True

				self.cursor.execute("INSERT INTO games VALUES(?, ?)", (gameName, False))
				return False

			else:
				self.cursor.execute("INSERT INTO games VALUES(?, ?)", (gameName, False))
				return False

	def remove_game(self, gameName):
		with self.connection:
			if SQlighter("gamesdb.db").game_exists(gameName):
				self.cursor.execute("DELETE FROM games WHERE game = ?", (gameName,))
				return gameName
			else:
				return False

	def show_discount(self, db_games):
		if db_games is False:
			return "You haven`t told me any games yet😕"

		else:
			result = PSstore().find_games(db_games)

			games_ondisc = []
			if type(result) is list:
				for result_el in result:
					for db_el in db_games:
						if result_el[-1] == db_el:
							games_ondisc.append(db_el)

					result_el.remove(result_el[-1])

			SQlighter("gamesdb.db").update_discounts(games_ondisc) 

			return result

	def update_discounts(self, db_games):
		with self.connection:
			for db_game in db_games:
				self.cursor.execute("UPDATE games SET discount = ? WHERE game = ?", (True, db_game.replace(" ", "_")))

	def get_games(self):
		with self.connection:
			db_games = self.cursor.execute("SELECT * FROM games").fetchall()
			if db_games:
				for i in range(0, len(db_games)):
					db_games[i] = db_games[i][0].strip().replace("_", " ")

				return db_games

			else:
				return False

	def edit_usermsg(self, msg):
		if type(msg) is list:
			fullmessage = ""
			for el in msg:
				fullmessage += (el[0] + ":  " + el[2] + "  (" + el[1] + " - fullprice)" + " - " + el[3] + "\n" + el[4] + "\n\n")

			return fullmessage[:-1]

		else:
			return msg

	def edit_dbmsg(self, msg):
		dbmsg = msg.replace(" ", "_").lower().split(",")

		for i in range(0, len(dbmsg)):
			if dbmsg[i].startswith("_"):
				dbmsg[i] = dbmsg[i][1:]

		return dbmsg