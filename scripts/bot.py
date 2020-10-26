import telebot
import config

from sqlighter import SQlighter
from telebot import types
from random import choice
from time import sleep

db = SQlighter("gamesdb.db") # connect to db

add_phrases_added = ["Memorized😼: ", "Done✔️: ", "Successfully added: ", "Made a note🖊: ",
					"I`ll remember: ", "Note to self: ", "I`ll make a note📝: ", 
					"Success! 'mygames' updated: ", "Added: ", "Saved: "]

add_phrases_exists = ["Already exists: ", "I`ve seen it before: ", "Oh, I already have this game: ", 
						"Hmm, seems familiar: ", "Already have: ", "I remember this one: "]

delete_phrases = ["The games have been deleted", "Success! The games are deleted✂️",
					"I`ve removed the games", "Now 'mygames' has fewer games", "Done"]

dont_remember_phrases = ["I don`t know this: '", "Can`t remember this: '",
						"Seems unfamiliar to me: '"]

wait_phrases = ["One minute...", "Just a minute...", "In a minute...", "One moment...", 
					"Just a moment...", "In a moment...", "Un momento..."]

ask_gamename = ["Okay, enter the names of the games", "Game names?", "Write game names",
					"Write the names of the games", "Enter game names"]

text_phrases = ["Can`t recognaize that", "Don`t know such a command", "I couldn`t understand",
					"Don`t understand you", "I have no idea what you mean"]

bot = telebot.TeleBot(config.token)

"""Handling '/start' command (when the user starts the bot for the first time)"""
@bot.message_handler(commands=['start'])
def greet_func(message):
	bot.send_message(message.chat.id, "Howdy {0.first_name}, nice day to buy a game with a discounted,\
		isn`t it? Then tell me the games you`re interested in".format(message.from_user))

	# for the first time the user stars the bot, we suggest him create him 'mygames'
	bot.register_next_step_handler(message, user_games)

"""Handling '/getlink' command (link to PS store)"""
@bot.message_handler(commands=['getlink'])
def get_link(message):
	bot.send_message(message.chat.id, "Link to PS store\nhttps://store.playstation.com/ru-ru/grid/STORE-MSF75508-PRICEDROPSCHI")

"""Handling '/addgame' command (addgame the game(s) to the db)"""
@bot.message_handler(commands=['addgame'])
def add_game(message): # ask the user the names of the games
	bot.send_message(message.chat.id, choice(ask_gamename))
	bot.register_next_step_handler(message, add_to_db)

def add_to_db(message): # add to the db
	if message.text.startswith('/'): # if the user after '/deletegame' enters some other command
		bot.reply_to(message, "Hey, that is not the name of the game")

	else:
		for el in db.edit_dbmsg(message.text): # edit entered games by the user to the necessary format (for the db)
			ifexists = db.add_game(el) # checking if the game is already in the db, 'ifexists' = True

			if ifexists: # if the game exists
				bot.send_message(message.chat.id, choice(add_phrases_exists) + el.replace("_", " ").title())

			else: # if not
				bot.send_message(message.chat.id, choice(add_phrases_added) + el.replace("_", " ").title())

"""Handling '/deletegame' command (delete the game(s) from the db)"""
@bot.message_handler(commands=['deletegame'])
def delete_game(message): # ask the user the names of the games
	bot.send_message(message.chat.id, choice(ask_gamename))
	bot.register_next_step_handler(message, delete_from_db)

def delete_from_db(message): # delete from the db
	if message.text.startswith('/'): # if the user after '/deletegame' enters some other command
		bot.reply_to(message, "Hey, that is not the name of the game")

	else:
		game_list = []

		for el in db.edit_dbmsg(message.text): # edit entered games by the user to the necessary format (for the db)
			temp = db.remove_game(el) # delete the game
			if temp == False: # if the game doesn`t exist
				bot.send_message(message.chat.id, choice(dont_remember_phrases) + el.replace("_", " ").title() + "'")

			else: # if the game exists
				game_list.append(temp.replace("_", " ").title())

		if game_list: # checking if the user entered only the games that are not in the db
			bot.send_message(message.chat.id, choice(delete_phrases))

"""Handling '/checkgames' command (send to the user a msg if there are discounts on his games)"""
@bot.message_handler(commands=['checkgames'])
def check_games(message):
	bot.send_message(message.chat.id, choice(wait_phrases))
	bot.send_message(message.chat.id, db.edit_usermsg(db.show_discount(db.get_games())))

"""Handling '/mygames' command (send to the user his list of games from the db)"""
@bot.message_handler(commands=['mygames'])
def get_mygames(message):
	allgames = ""
	try:
		for game in db.get_games(): # each game from the db
			allgames += (game.title() + ", ")

		bot.send_message(message.chat.id, allgames[:-2])

	except TypeError: # if there are no games in the db, 'get_games()' method returns 'False'
		bot.send_message(message.chat.id, "Sorry man, I don`t remember you telling me any games")

"""If the user doesn`t use bot commands and sends random messages"""
@bot.message_handler(content_types=['text'])
def text_handler(message):
	bot.reply_to(message, choice(text_phrases))

"""Create 'mygames' """
def user_games(message):
	add_to_db(message) # add user games to db

	# ask if the user wants to check the discount (to 'callback_inline' func)
	markup1 = types.InlineKeyboardMarkup(row_width = 2)

	item1 = types.InlineKeyboardButton('sure', callback_data = 'yes')
	item2 = types.InlineKeyboardButton('no', callback_data = 'no')

	markup1.add(item1, item2)

	sleep(2)
	bot.send_message(message.chat.id, "Now do you want to check the discount on them?", reply_markup = markup1)

"""Handling user`s response from the 'user_games' func"""
@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
	if call.message:
		if call.data == 'yes':
			# check if there are discounts
			bot.send_message(call.message.chat.id, choice(wait_phrases))
			bot.send_message(call.message.chat.id, db.edit_usermsg(db.show_discount(db.get_games())))

		elif call.data == 'no':
			bot.send_message(call.message.chat.id, "Okay, check my commands out then,\
				I`ll be waiting for you😏")

bot.polling(none_stop=True)