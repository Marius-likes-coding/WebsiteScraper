class Subpage:
	class Item:
		def __init__(self, _link):
			self.link = _link

			self.Brandname = ""
			self.Productname = ""
			self.Colors = ""
			self.Sizes = ""
			self.Description = ""
			self.Materials = ""
			self.Maintenance = ""
			self.RegularPrice = -1.0
			self.CurrentPrice = -1.0

		def __str__(self):
			return " Content:\n" \
			+ self.Brandname + "\n" \
			+ self.Productname + "\n" \
			+ self.Colors + "\n" \
			+ self.Sizes + "\n" \
			+ self.Description + "\n" \
			+ self.Materials + "\n" \
			+ self.Maintenance + "\n" \
			+ self.RegularPrice + "\n" \
			+ self.CurrentPrice

		def __iter__(self):
			return iter([self.Brandname, self.Productname, self.Colors, \
        				self.Sizes, self.Description, self.Materials, \
        				self.Maintenance, self.RegularPrice, self.CurrentPrice])


	def __init__(self, _link, _subPageName, _mainPage):
		self.link = _link
		self.subPageName = _subPageName
		self.mainPage = _mainPage
		self.currentPageNbr = 1
		self.currentItemIndex = 0
		self.items = list()

	def setNbrPages(self, _nbrPages):
		self.nbrPages = _nbrPages

	def hasNextPage(self):
		return self.currentPageNbr <= self.nbrPages

	def getNextPageLink(self):
		"""
			Return the link to the next page of the subpage and increments the counter
			for the next call.
		"""
		newLink = self.link + "?page=" + str(self.currentPageNbr)
		self.currentPageNbr += 1
		return newLink

	def resetItemIndex(self):
		self.currentItemIndex = 0

	def hasNextItem(self):
		return self.currentItemIndex < len(self.items)

	def getNextItem(self):
		"""
			Return the next item of the subpage.
		"""
		item = self.items[self.currentItemIndex]
		self.currentItemIndex += 1
		return item

	def addItem(self, itemLink):
		self.items.append( Subpage.Item(self.mainPage + itemLink) )