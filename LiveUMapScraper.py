from bs4 import BeautifulSoup
from requests_html import HTMLSession
import mysql.connector
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

class Scraper:
	def __init__(self, url):
		self.__url = url
		self.__events = None

	def get_events_count(self):
		return len(self.__events)

	def scrape_events(self, limit):
		print("[SCRAPING EVENTS FROM www.liveuamap.com...]")
		session = HTMLSession()
		resp = session.get(self.__url)
		resp.html.render(timeout=60)

		soup = BeautifulSoup(resp.html.html, 'html5lib')
		self.__events = soup.find_all("div", class_="event cat2 sourcees", limit=limit)

	def set_event(self, index):
		return self.Event(self.__events[index])

	class Event():
		def __init__(self, event):
			self.__event = event

		def get_id(self):
			return self.__event.attrs.get("data-id")

		def get_time(self):
			now = datetime.now()
			try:
				time_added = self.__event.find("span", class_ = "date_add").text
				x = [int(x) for x in time_added.split() if x.isdigit()][0]

				return (now - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
			except:
				return now.strftime("%Y-%m-%d %H:%M:%S")

		def get_title(self):
			return self.__event.find("div", class_ = "title").text

		def get_source(self):
			return self.__event.find("a", class_ = "source-link").attrs.get("href")

		def get_img(self):
			img = self.__event.find("div", class_="img").find("img")

			return img['src'] if img is not None else None

class Database:
	def __init__(self, host, user, password, database):
		self.__db = mysql.connector.connect(
			host=host, 
			user=user, 
			password=password, 
			database=database
		)
		self.__cursor = self.__db.cursor()

	def get(self, sql):
		self.__cursor.execute(sql)

		return self.__cursor.fetchall()

	def insert(self, data):
		sql = "INSERT INTO events (id, title, source, image, created_at) VALUES (%s, %s, %s, %s, %s)"
		self.__cursor.execute(sql, data)
		self.__db.commit()
		print('[SUCCESS] New event fetched. [ID: ' + str(data[0]) + ']')

	def id_doesnt_exists(self, id):
		event = self.get("SELECT * FROM events WHERE id = " + str(id))

		if not event:
			return True

		return False


def set_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)

        print("Time left before next scraping: " + timer, end="\r")

        time.sleep(1)
        seconds -= 1

def main():
	load_dotenv()

	DEBUG = eval(os.environ.get("DEBUG"))

	scraper = Scraper("https://liveuamap.com/")

	try:
		db = Database(
			os.environ.get("DB_HOST"),
			os.environ.get("DB_USER"),
			os.environ.get("DB_PASSWORD"),
			os.environ.get("DB_DATABASE")
		)

		on = True

	except Exception as e:
		if DEBUG:
			print('[DEBUG] ' + e)
		print("\n[ERROR] FAILED CONNECTING TO DADTABASE")
		on = False

	while on:
		try:
			scraper.scrape_events(10)

			for index in range(scraper.get_events_count()):
				try:
					event = scraper.set_event(index)

					unique_id = event.get_id()

					if db.id_doesnt_exists(unique_id):					
						title = event.get_title()
						source = event.get_source()
						image = event.get_img()
						created_at = event.get_time()

						data = (int(unique_id), title, source, image, created_at)

						db.insert(data)

				except Exception as e:
					print(e)
					print('\n[ERROR] EVENT FAILED: ' + unique_id if not None else 'unknown.')

			set_timer(300)
		except Exception as e:
			print(e)
			print('\n[ERROR] SCRAPING FAILED')
			set_timer(30)

if __name__ == "__main__":
	main()
