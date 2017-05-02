from bs4 import BeautifulSoup
from Scraper.Subpage import Subpage
from Scraper.HttpHandler import HttpHandler
import csv

class WebsiteScraper:
	def __init__(self, _linkFilePath, _mainPageFilePath, _HttpHandler):
		self.linkFilePath = _linkFilePath
		self.mainPageFilePath = _mainPageFilePath
		self.HttpHandler = _HttpHandler
		self.subpages = list()

	def getNbrPages(self, soupPage):
		"""
			Searches the tag with the number of pages in the category (for example Herren/Schuhe)
			and returns the total number of pages.

			The format of the span class containing the information is:
			"<span class="pagination-currentPageLabel">Seite&nbsp;2&nbsp;/&nbsp;14</span>"
			We extract the number 14.
		"""
		try:
			tagContent = soupPage.select("span.pagination-currentPageLabel")[0].contents[0]
			return int(tagContent.split("/")[1])
		except (AttributeError, TypeError) as e:
			print("WebsiteScraper::getNbrPages -> element not found ", str(e))


	def getAllPageNumbers(self):
		"""
			For each Subpage it scrapes and sets the number of pages.
		"""
		for subpage in self.subpages:
			htmlcontent = self.HttpHandler.getHtmlContentFromLink(subpage.link)
			soupPage = BeautifulSoup(htmlcontent, "html.parser")
			subpage.setNbrPages( self.getNbrPages(soupPage) )

	def loadLinks(self):
		"""
			Reads all the links from the link file (one per line)
			and saves them in a list.
		"""
		mainPageFile = open(self.mainPageFilePath, 'r')
		try:
			lines = mainPageFile.readlines()
			if len(lines) > 0:
				self.mainPage = lines[0]
			else:
				print("No link in : ", self.mainPageFilePath)
		finally:
		    mainPageFile.close()

		linkFile = open(self.linkFilePath, 'r')
		try:
			# add all links to a list
			for line in linkFile.readlines():
				if "http" in line:
					subPageName = line.split(".de")[1].replace("/", "")
					self.subpages.append( Subpage(line.strip(' \t\n\r'),subPageName,self.mainPage) )
		finally:
		    linkFile.close()

	def collectItemLinksFromPage(self, subpage):
		"""
			For all the pages of a subpage, it collects the links
			to the products (items).
		"""
		while subpage.hasNextPage():
			# load page and fetch html content
			link = subpage.getNextPageLink()
			htmlcontent = self.HttpHandler.getHtmlContentFromLink(link)
			soupPage = BeautifulSoup(htmlcontent, "html.parser")

			# collect item links on page
			try:
				for item in soupPage.findAll("a", { "class" : "js-productTile-link" }):
					itemLink = item["href"]
					subpage.addItem(itemLink)

			except (AttributeError, TypeError) as e:
				print("WebsiteScraper::collectItemLinksFromPage -> element not found ", str(e))

	def scrapeInfoForItem(self, subpage, item):
		"""
			For one item, scrape its page and set the corresponding attributes
			for each information
		"""
		htmlcontent = self.HttpHandler.getHtmlContentFromLink(item.link)
		soupPage = BeautifulSoup(htmlcontent, "html.parser")

		# brand
		result = soupPage.findAll("p", { "class" : "product-brand--details" })
		if len(result) > 0:
			res1 = result[0].find("a")
			if res1 == None:
				item.Brandname = str(result[0].contents[0])
			elif len(res1) > 0:
				item.Brandname = str(res1.contents[0])

		# Name
		result = soupPage.findAll("h1", { "class" : "product-title--details" })
		if len(result) > 0:
			res1 = result[0].find("span", { "itemprop" : "name" })
			if len(res1) > 0:
				item.Productname = str(res1.contents[0])

		# Color
		results = soupPage.findAll("a", { "class" : "js-switch-colourVariant" })
		if len(results) == 0:
			result2 = soupPage.findAll("h1", { "class" : "product-title--details" })
			if len(result) > 0:
				res2 = result2[0].find("span", { "itemprop" : "color" })
				if len(res2) > 0:
					item.Colors = str(res2.contents[0])
		else:
			item.Colors = "|".join([res["title"] for res in results])

		# size
		results = soupPage.findAll("span", { "class" : "product-sizeLabel" })
		item.Sizes = "|".join([res.contents[0] for res in results])

		# beschreibung
		result = soupPage.find("ul", { "class" : "product-infoList--twoCol" })
		if result:
			results = result.findAll("span")
			item.Description = "|".join([res.contents[0] for res in results])

		# material 
		results = soupPage.find("ul", { "class" : "product-infoList" })
		if results:
			results = results.findAll("span")
			item.Materials = "|".join([res.contents[0] for res in results])

		# pflege
		results = soupPage.find("ul", { "class" : "product-care" })
		if results:
			results = results.findAll("li")
			item.Maintenance = "|".join([res.get_text() for res in results])

		# current, regular price (current can be reduced)
		result = soupPage.find("meta", { "itemprop" : "price" })
		if result:
			result = result["content"]
			if "," in result:
				result = str(result).replace(',','.')
			if u'\xa0' in result:
				result = result.replace(u'\xa0', u' ')[:-1] # there is a € sign at the end
			if "ab" in result:
				item.CurrentPrice = result
			else:
				item.CurrentPrice = float(result)
		result = soupPage.find("span", { "class" : "is-regular" })
		if result:
			if "," in result.contents[0]:
				result = str(result.contents[0]).replace(',','.')
			if u'\xa0' in result:
				result = result.replace(u'\xa0', u' ')[:-1] # there is a € sign at the end
			if "ab" in result:
				item.RegularPrice = result
			else:
				item.RegularPrice = float(result)
		else:
			item.RegularPrice = item.CurrentPrice


	def writeItemsToCSV(self, fileName, itemList):
		"""
			Write the items of a subpage to a .csv file
		"""
		with open(fileName, 'w') as csvFile:
		    csvWriter = csv.writer(csvFile, delimiter=',')
		    # Column titles
		    csvWriter.writerow(["Brandname","Productname","Colors","Sizes","Description","Materials","Maintenance","RegularPrice","CurrentPrice"])
		    for item in itemList:
		        csvWriter.writerow(list(item))

	def run(self):
		print("Loading subpage links from file ...")
		self.loadLinks()

		print("Fetching number of pages for the subpages ...")
		self.getAllPageNumbers()

		print("Collecting item links and informations from subpages ...")
		for subpage in self.subpages:
			print(subpage.link)
			self.collectItemLinksFromPage(subpage)
			while subpage.hasNextItem():
				# load page and fetch html content
				item = subpage.getNextItem()
				self.scrapeInfoForItem(subpage, item)

			self.writeItemsToCSV("./results/"+subpage.subPageName+".csv", subpage.items)