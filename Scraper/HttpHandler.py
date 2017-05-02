import urllib3 as url

class HttpHandler:
	def __init__(self):
		url.disable_warnings()
		self.urlManager = url.PoolManager()

	def getHtmlContentFromLink(self, link):
		"""
			Open the html page of the given link with a Get request
			and return the content.
		"""
		try:
			content =  self.urlManager.request('GET', link)
			return content.data
		except:
			print("HttpHandler::getHtmlContentFromLink -> could not open link : ", link)