from Scraper.WebsiteScraper import WebsiteScraper
from Scraper.HttpHandler import HttpHandler

def main():
	httpHandler = HttpHandler()
	websiteScraper = WebsiteScraper("config/Links.txt", "config/MainPage.txt", httpHandler)
	websiteScraper.run()

if __name__ == '__main__':
      main()