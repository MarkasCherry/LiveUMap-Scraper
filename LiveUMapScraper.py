import time
from dotenv import load_dotenv
import os
from Database import Database
from Scraper import Scraper

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
		print("\n[ERROR] FAILED CONNECTING TO DATABASE")
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

						db.insert_event(data)

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
