from selenium import webdriver
import json, time, os

sslPort = ''
fxBinaryPath = ''
geckodriverPath = ''
pageDownJS = 'document.documentElement.scrollTop = 100000000'
outputPath = ''
wgetPath = ''
httpsProxy = 'https://127.0.0.1:{}/'.format(str(sslPort))

fxProfile = webdriver.firefox.firefox_profile.FirefoxProfile()
fxProfile.set_preference('network.proxy.type', 1)
fxProfile.set_preference('network.proxy.ssl', '127.0.0.1')
fxProfile.set_preference('network.proxy.ssl_port', sslPort)
fxProfile.set_preference('network.proxy.socks_remote_dns', True)
fxProfile.set_preference('network.trr.mode', 2)
fxProfile.set_preference('permissions.default.image', 2)
fxProfile.set_preference('intl.accept_languages', 'zh-CN, zh, zh-TW, zh-HK, en-US, en')
fxDriver = webdriver.firefox.webdriver.WebDriver(firefox_profile=fxProfile, firefox_binary=fxBinaryPath, executable_path=geckodriverPath)

class POST:
	
	def __init__(self, url):
		self.url = url
	
	def GetInfo(self):		
		for e in fxDriver.find_elements_by_xpath('//script[@type="text/javascript"]'):
			try:
				jsonText = e.get_attribute('textContent')
				if 'viewerId' in jsonText:
					jsonData = json.loads(jsonText[jsonText.find('{'): jsonText.rfind('}') + 1])['entry_data']['PostPage'][0]['graphql']['shortcode_media']
					break
			except:
				continue
		
		uploadTimeStamp = jsonData['taken_at_timestamp']
		uploadTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(uploadTimeStamp))
		username = jsonData['owner']['username']
		fullName = jsonData['owner']['full_name']
		likes = jsonData['edge_media_preview_like']['count']
		comments = jsonData['edge_media_preview_comment']['count']
		try:
			text = jsonData['edge_media_to_caption']['edges'][0]['node']['text']
		except:
			text = ''
		
		try:
			mediaList = []
			for obj in jsonData['edge_sidecar_to_children']['edges']:
				try:
					vidUrl = obj['node']['video_url']
					vidViewCount = obj['node']['video_view_count']
					mediaList.append((vidUrl, vidViewCount))
				except:
					picUrl = obj['node']['display_url']
					picDescription = obj['node']['accessibility_caption']
					mediaList.append((picUrl, picDescription))
			return uploadTime, username, fullName, likes, comments, text, mediaList, 'm'
		except:
			try:
				vidUrl = jsonData['video_url']
				vidViewCount = jsonData['video_view_count']
				return uploadTime, username, fullName, likes, comments, text, vidUrl, vidViewCount, 'v'
			except:
				picUrl = jsonData['display_url']
				picDescription = jsonData['accessibility_caption']
				return uploadTime, username, fullName, likes, comments, text, picUrl, picDescription, 'p'
	
	def DownloadInfo(self, info):
		now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
		uploadTime = info[0]
		username = info[1]
		fullName = info[2]
		likes = info[3]
		comments = info[4]
		text = info[5]
		folder = '{}\\{}\\{}'.format(outputPath, username, ''.join([x for x in uploadTime if x.isdigit()]))
		
		try:
			os.makedirs(folder)
		except Exception as e:
			print(e)
		
		with open('{}\\info.txt'.format(folder), 'w', encoding='utf-8') as f:
			f.write('Now: {}'.format(now))
			f.write('\nUpload time: {}'.format(uploadTime))
			f.write('\nUsername: {}'.format(username))
			f.write('\nFull name: {}'.format(fullName))
			f.write('\nText: {}'.format(text))
			f.write('\nLikes: {}'.format(likes))
			f.write('\nComments: {}'.format(comments))
			
			if info[-1] == 'm':
				mediaList = info[6]
				i = 1
				for mediaTuple in mediaList:
					if str(mediaTuple[1]).isdigit():
						vidUrl = mediaTuple[0]; vidViewCount = str(mediaTuple[1])
						f.write('\n{}. Video view count: {} Video url: {}'.format(str(i), vidViewCount, vidUrl))
					else:
						picUrl = mediaTuple[0]; picDescription = mediaTuple[1]
						f.write('\n{}. Picture description: {} Picture url: {}'.format(str(i), picDescription, picUrl))
					i += 1
			elif info[-1] == 'v':
				vidUrl = info[6]
				vidViewCount = info[7]
				f.write('\nVideo view count: {}'.format(vidViewCount))
				f.write('\nVideo url: {}'.format(vidUrl))
			elif info[-1] == 'p':
				picUrl = info[6]
				picDescription = info[7]
				f.write('\nPicture description: {}'.format(picDescription))
				f.write('\nPicture url: {}'.format(picUrl))
	
	def DownloadFile(self, info):
		uploadTime = info[0]
		username = info[1]
		folder = '{}\\{}\\{}'.format(outputPath, username, ''.join([x for x in uploadTime if x.isdigit()]))
		
		try:
			os.makedirs(folder)
		except Exception as e:
			print(e)
		
		if info[-1] == 'm':
			mediaList = info[6]
			i = 1
			for mediaTuple in mediaList:
				if str(mediaTuple[1]).isdigit():
					vidUrl = mediaTuple[0]
					os.system('{} --output-document={}\\{}.mp4 --no-check-certificate --execute https_proxy={} --execute robots=off --continue "{}"'.format(wgetPath, folder, str(i), httpsProxy, vidUrl))
				else:
					picUrl = mediaTuple[0]
					os.system('{} --output-document={}\\{}.jpg --no-check-certificate --execute https_proxy={} --execute robots=off --continue "{}"'.format(wgetPath, folder, str(i), httpsProxy, picUrl))
				i += 1
		elif info[-1] == 'v':
			vidUrl = info[6]
			os.system('{} --output-document={}\\1.mp4 --no-check-certificate --execute https_proxy={} --execute robots=off --continue "{}"'.format(wgetPath, folder, httpsProxy, vidUrl))
		elif info[-1] == 'p':
			picUrl = info[6]
			os.system('{} --output-document={}\\1.jpg --no-check-certificate --execute https_proxy={} --execute robots=off --continue "{}"'.format(wgetPath, folder, httpsProxy, picUrl))
	
	def Main(self):
		try:
			fxDriver.get(self.url)
			info = self.GetInfo()
			self.DownloadInfo(info)
			self.DownloadFile(info)
		except Exception as e:
			print(e)

class PROFILE:
	
	def __init__(self, profileUrl):
		self.profileUrl = profileUrl
	
	def Update(self):
		for e in fxDriver.find_elements_by_xpath('//script[@type="text/javascript"]'):
			try:
				jsonText = e.get_attribute('textContent')
				if 'viewerId' in jsonText:
					jsonData = json.loads(jsonText[jsonText.find('{'): jsonText.rfind('}') + 1])['entry_data']['ProfilePage'][0]['graphql']['user']
					break
			except:
				continue
		
		postCount = jsonData['edge_owner_to_timeline_media']['count']
		username = jsonData['username']
		folder = '{}\\{}'.format(outputPath, username)
		
		if os.path.exists(folder):
			downloadCount = len([x for x in os.listdir(folder) if os.path.isdir('{}\\{}'.format(folder, x))])
		else:
			downloadCount = 0
		
		updateCount = postCount - downloadCount
		
		return updateCount
	
	def GetLocY(self):
		urlDict = {}
		
		for e in fxDriver.find_elements_by_xpath('//a[contains(@href, "/p/")]'):
			locY = e.location['y']
			locX = e.location['x']
			url = e.get_attribute('href')
			urlDict[url] = locX/1000 + locY
		
		return locY, urlDict
	
	def JudgeLoading(self, locY, urlDict):
		time.sleep(0.5)		
		locYNew, urlDictNew = self.GetLocY()
		
		if locYNew > locY:
			urlDictNew.update(urlDict)
		else:
			locYNew = None
		
		return locYNew, urlDictNew
	
	def GetWholePage(self):
		updateCount = self.Update()
		fxDriver.execute_script(pageDownJS)
		
		try:
			fxDriver.find_element_by_xpath('//div[contains(text(), "更多帖子")]').click()
		except Exception as e:
			print(e)
		
		locY, urlDict = self.GetLocY()
		
		while 1:
			fxDriver.execute_script(pageDownJS)						
			while 1:
				locYNew, urlDictNew = self.JudgeLoading(locY, urlDict)				
				urlList = [t[0] for t in sorted(urlDictNew.items(), key = lambda x:x[1])]
				
				if len(urlList) >= updateCount:
					return urlList[: updateCount]
				
				if locYNew == None:
					continue
				else:
					locY = locYNew
					urlDict = urlDictNew
					break
	
	def Main(self):
		try:
			fxDriver.get(self.profileUrl)
			urlList = self.GetWholePage()
			return urlList
		except Exception as e:
			print(e)

def Main():
	inputUrl = input('Please input the instagram link: ')
	
	if '/p/' in inputUrl:
		POST(inputUrl).Main()
	else:
		if not 'www.instagram.com' in inputUrl:
			inputUrl = 'https://www.instagram.com/{}/'.format(inputUrl)
		
		urlList = PROFILE(inputUrl).Main()
		
		if urlList:
			for url in urlList:
				POST(url).Main()
	
	Main()

if __name__ == '__main__':
	Main()
