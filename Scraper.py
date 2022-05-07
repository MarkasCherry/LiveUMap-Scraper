from bs4 import BeautifulSoup
from requests_html import HTMLSession
from datetime import datetime, timedelta

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
		self.__events = soup.find_all("div", class_="sourcees", limit=limit)

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