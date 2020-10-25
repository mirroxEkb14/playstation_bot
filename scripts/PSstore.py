import requests
import re

from bs4 import BeautifulSoup
from random import choice

class PSstore:
	host = "https://store.playstation.com"
	url = "https://store.playstation.com/ru-ru/grid/STORE-MSF75508-PRICEDROPSCHI"

	phrases = ["Bad news - there are no discounts on your games🙀", "Sorry, I found no\
				discounts on your games😔", "No discounts, sorry😿", "Pardon, there are no discounts\
				on your games at the moment"]
	
	def find_games(self, db_games):
		source = requests.get(self.url).text
		soup = BeautifulSoup(source, 'lxml')

		"""get the number of the pages"""
		page_ceil = soup.find('div', class_='paginator-control__container').find_all('a')
		page_ceil = int(re.sub(r'[^0-9]', "", page_ceil[-1].get('href'))[-1])

		"""get the games at a discount"""
		result_list = []
		for page in range(1, page_ceil + 1):
			source = requests.get(self.url + '/' + str(page)).text
			soup = BeautifulSoup(source, 'lxml')

			items = soup.find_all('div', class_='grid-cell__body')

			for item in items:
				for game in db_games:

					web_game = item.text.split('PS4')[0].replace("\n", "").strip()
					if game.upper() in web_game or game.title() in web_game:

						# delete extra spaces
						for i in range(0, len(web_game)):
							if web_game[i] == " " and web_game[i + 1] == " ":
								temp_list = list(web_game)
								for j in range(0, len(temp_list)):
									if temp_list[j] == " " and temp_list[j + 1] == " ":
										temp_list.pop(j)
										break

								web_game = "".join(temp_list)
								break

						# connect to game page
						game_page = self.host + item.find('a').get('href')

						source = requests.get(game_page).text
						soup = BeautifulSoup(source, 'lxml')

						price_item = soup.find('div', class_='sku-info__price-display')

						# 'RUB' to the end for full price
						fullprice = list(re.sub(r"[^A-Z0-9. ]", "", price_item.find('span').text))

						while fullprice[0].isalpha():
							fullprice.append(fullprice[0])
							fullprice.pop(0)

						fullprice = "".join(fullprice)

						# 'RUB' to the end for discounted price
						discprice = list(re.sub(r"[^A-Z0-9. ]", "", price_item.find('h3').text))

						while discprice[0].isalpha():
							discprice.append(discprice[0])
							discprice.pop(0)

						discprice = "".join(discprice)

						disc_badge = re.sub(r'[^a-zA-Zа-яА-Я0-9% ]', "", soup.find('div', class_='product-image__discount-badge').text)

						result_list.append([web_game, fullprice, discprice, disc_badge, game_page, game])

		if result_list:
			return result_list

		else:
			return choice(self.phrases)