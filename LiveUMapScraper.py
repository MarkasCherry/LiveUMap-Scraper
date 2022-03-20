from bs4 import BeautifulSoup
from requests_html import HTMLSession
import time

class Scraper:
	def __init__(self, url):
		self.__url = url
		self.__events = None

	def get_events_count(self):
		return len(self.__events)

	def scrape_events(self, limit):
		print('....scraping....')
		session = HTMLSession()
		resp = session.get(self.__url)
		resp.html.render()

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
			return self.__event.find("span", class_ = "date_add").text

		def get_title(self):
			return self.__event.find("div", class_ = "title").text

		def get_source(self):
			return self.__event.find("a", class_ = "source-link").attrs.get("href")

		def get_img(self):
			img = self.__event.find("div", class_="img").find("img")

			return img['src'] if img is not None else None

def set_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print("Time left before next scraping: " + timer, end="\r")
        time.sleep(1)
        seconds -= 1


def main():
	scraper = Scraper("https://liveuamap.com/")

	while True:
		scraper.scrape_events(10)

		for index in range(scraper.get_events_count()):
			event = scraper.set_event(index)

			unique_id = event.get_id()
			added_min = event.get_time()
			title = event.get_title()
			source = event.get_source()
			img = event.get_img()

			print(title, source)

		set_timer(300)


if __name__ == "__main__":
	main()
