from logging import warning
import os
from sys import exit
import pickle
import time
import getpass
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import os
import zipfile

class Scraper:
	# This time is used when we are waiting for element to get loaded in the html
	wait_element_time = 5

	# In this folder we will save cookies from logged in users
	cookies_folder = 'cookies' + os.path.sep

	def __init__(self, url, headless = False, proxy = False):
		self.url = url
		self.headless = headless
		self.setup_driver_options(headless, proxy)
		self.setup_driver()

	# Automatically close driver on destruction of the object
	def __del__(self):
		if self.headless == False: 
			# print('closing browser')
			pass
			
		
	# Add these options in order to make chrome driver appear as a human instead of detecting it as a bot
	# Also change the 'cdc_' string in the chromedriver.exe with Notepad++ for example with 'abc_' to prevent detecting it as a bot
	def setup_driver_options(self, headless, proxy):
		self.driver_options = Options()

		arguments = [
			'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
			'--start-maximized',
			'--disable-blink-features=AutomationControlled',
			'--disable-dev-shm-usage',
			'--no-sandbox'
		]

		experimental_options = {
			'excludeSwitches': ['enable-automation', 'enable-logging'],
   			'prefs': {
       			'profile.default_content_setting_values.notifications': 2,
				
    			# Disable Save password popup
    			'credentials_enable_service': False,
     			'profile.password_manager_enabled': False
            }
		}

		for argument in arguments:
			self.driver_options.add_argument(argument)

		for key, value in experimental_options.items():
			self.driver_options.add_experimental_option(key, value)
		
		if headless:
			self.driver_options.add_argument('--headless')

		if proxy:
			# parts = proxy.split(':')
			# proxy = parts[0] + ':' + parts[1]
			# webdriver.DesiredCapabilities.CHROME['proxy'] = {
			# 	"httpProxy": proxy,
			# 	"ftpProxy": proxy,
			# 	"sslProxy": proxy,
			# 	"ProxyType": 'MANUAL',
			# }
			# webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True

			proxy= proxy.split(':')
			PROXY_HOST = proxy[0]
			PROXY_PORT = proxy[1]
			PROXY_USER = proxy[2]
			PROXY_PASS = proxy[3]

			manifest_json = """
			{
				"version": "1.0.0",
				"manifest_version": 2,
				"name": "Chrome Proxy",
				"permissions": [
					"proxy",
					"tabs",
					"unlimitedStorage",
					"storage",
					"<all_urls>",
					"webRequest",
					"webRequestBlocking"
				],
				"background": {
					"scripts": ["background.js"]
				},
				"minimum_chrome_version":"22.0.0"
			}
			"""

			background_js = """
			var config = {
					mode: "fixed_servers",
					rules: {
					singleProxy: {
						scheme: "http",
						host: "%s",
						port: parseInt(%s)
					},
					bypassList: ["localhost"]
					}
				};

			chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

			function callbackFn(details) {
				return {
					authCredentials: {
						username: "%s",
						password: "%s"
					}
				};
			}

			chrome.webRequest.onAuthRequired.addListener(
						callbackFn,
						{urls: ["<all_urls>"]},
						['blocking']
			);
			""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

			pluginfile = 'proxy_auth_plugin.zip'

			with zipfile.ZipFile(pluginfile, 'w') as zp:
				zp.writestr("manifest.json", manifest_json)
				zp.writestr("background.js", background_js)
			self.driver_options.add_extension(pluginfile)


	# Setup chrome driver with predefined options
	def setup_driver(self):
		executable_path = os.getcwd() + r"/chromedriver"
		self.s = Service(executable_path=executable_path)
		self.driver = webdriver.Chrome(service=self.s, options = self.driver_options)
		self.driver.get(self.url)

	# Add login functionality and load cookies if there are any with 'cookies_file_name'
	def add_login_functionality(self, login_url, is_logged_in_selector, login_function=None, cookies_file_name='cookie'):
		# Three step Login. 1:Using cookies, 2:By Selenium UI interaction with given credentials, 3:Manual login Then press any key
		self.login_url = login_url
		self.is_logged_in_selector = is_logged_in_selector
		self.cookies_file_name = cookies_file_name + '.pkl'
		self.cookies_file_path = self.cookies_folder + self.cookies_file_name

		# Step 1: Check if there is a cookie file saved
		if self.is_cookie_file():
			# Load cookies
			self.load_cookies()
			
			# Check if user is logged in after adding the cookies
			is_logged_in = self.is_logged_in(loop_count = 5)
			if is_logged_in:
				return True
		
		# Step 2: Call the login method for Selenium UI interaction
		if login_function:
			login_function()
		# Step 3: Manual Login
		else:
			input('Login manually, then press ENTER...')
			self.wait_random_time(2.0, 4.0)
		
		is_logged_in = self.is_logged_in(loop_count = 5)
		if is_logged_in:
			# User is logged in. So, save the cookies
			self.save_cookies()
			return True

		return False

	# Check if cookie file exists
	def is_cookie_file(self):
		return os.path.exists(self.cookies_file_path)

	# Load cookies from file
	def load_cookies(self):
		# Load cookies from the file
		cookies_file = open(self.cookies_file_path, 'rb')
		cookies = pickle.load(cookies_file)
		
		for cookie in cookies:
			self.driver.add_cookie(cookie)

		cookies_file.close()

		self.go_to_page(self.url)

		time.sleep(5)

	# Save cookies to file
	def save_cookies(self):
		# Do not save cookies if there is no cookies_file name 
		if not hasattr(self, 'cookies_file_path'):
			return

		# Create folder for cookies if there is no folder in the project
		if not os.path.exists(self.cookies_folder):
			os.mkdir(self.cookies_folder)

		# Open or create cookies file
		cookies_file = open(self.cookies_file_path, 'wb')
		
		# Get current cookies from the driver
		cookies = self.driver.get_cookies()

		# Save cookies in the cookie file as a byte stream
		pickle.dump(cookies, cookies_file)

		cookies_file.close()

	# Check if user is logged in based on a html element that is visible only for logged in users
	def is_logged_in(self, loop_count=1, wait_element_time = None):
		return self.find_element(self.is_logged_in_selector, loop_count=loop_count)

	# Wait random amount of seconds before taking some action so the server won't be able to tell if you are a bot
	def wait_random_time(self, a=0.20, b=1.20):
		random_sleep_seconds = round(random.uniform(a, b), 2)

		time.sleep(random_sleep_seconds)

	# Goes to a given page and waits random time before that to prevent detection as a bot
	def go_to_page(self, page):
		# Wait random time before refreshing the page to prevent the detection as a bot
		self.wait_random_time()

		# Refresh the site url with the loaded cookies so the user will be logged in
		self.driver.get(page)

	def find_element(self, css_selector='', xpath='', loop_count=1, exit_on_missing_element = False, wait_element_time = None, warnings=False):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		selector = css_selector or xpath
		# Intialize the condition to wait
		if css_selector:
			wait_until = EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
		elif xpath:
			wait_until = EC.element_to_be_clickable((By.XPATH, selector))
		else:
			print('ERROR: CSS_SELECTOR | XPATH is required')
			exit()

		for i in range(loop_count):
			try:
				# Wait for element to load
				element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
				return element
			except TimeoutException:
				if warnings:
					print(f'WARNING: TRY{i+1}: Unable to locate the element {selector} yet')
			time.sleep(1)
		
		if exit_on_missing_element:
			print(f'ERROR: Timed out waiting for the element with selector "{selector}" to load')
			exit()

		return None
	
	def find_elements(self, css_selector='', xpath='', loop_count=1, exit_on_missing_element = False, wait_element_time = None, warnings=False):

		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		selector = css_selector or xpath

		for i in range(loop_count):
			try:
				if css_selector:
					elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
				elif xpath:
					elements = self.driver.find_elements(By.XPATH, selector)
				else:
					print('ERROR: CSS_SELECTOR | XPATH is required')
					exit()
		
				return elements
			except TimeoutException:
				if warnings:
					print(f'WARNING: TRY{i+1}: Unable to locate the element {selector} yet')
			time.sleep(1)	
		
		if exit_on_missing_element:
			print(f'ERROR: Timed out waiting for the element with selector {selector} to load')
			exit()

		return None				

	def click_checkbox(self, selector_position):
		elements = self.driver.find_elements_by_tag_name('input[type="checkbox"]')[selector_position]
		elements.click()
	
	def select_dropdown(self, selector, val, text = False):
		element = self.find_element(selector)
		select = Select(element)
		if text:
			select.select_by_visible_text(val)
		else:
			if type(val) == int:
				val = str(val)
			select.select_by_value(val)

	def add_emoji(self, selector, text):
		JS_ADD_TEXT_TO_INPUT = """
		var elm = arguments[0], txt = arguments[1];
		elm.value += txt;
		elm.dispatchEvent(new Event('change'));
		"""
		element = self.driver.find_element_by_css_selector(selector)
		self.driver.execute_script(JS_ADD_TEXT_TO_INPUT, element, text)
		element.send_keys('.')
		element.send_keys(Keys.BACKSPACE)
		element.send_keys(Keys.TAB)

	def scroll_wait(self, selector, sleep_duration = 2):
		element = self.driver.find_element_by_css_selector(selector)
		self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto',block: 'center',inline: 'center'});", element);
		time.sleep(sleep_duration)
	
	# Wait random time before cliking on the element
	def element_click(self, css_selector='', xpath='', loop_count=1, exit_on_missing_element = False, warnings = False, delay = True):
		
		element = self.find_element(css_selector=css_selector, xpath=xpath, loop_count=loop_count, exit_on_missing_element=exit_on_missing_element, warnings=warnings)

		if element:
			if delay:
				self.wait_random_time()
			element.click()

		return element
		
	# Wait random time before sending the keys to the element
	def element_send_keys(self, text, css_selector='', xpath='', loop_count=1, exit_on_missing_element=False, warnings=False, delay = True):
		
		element = self.find_element(css_selector=css_selector, xpath=xpath, loop_count=loop_count, exit_on_missing_element=exit_on_missing_element, warnings=warnings)

		if element:
			if delay:
				self.wait_random_time()

			element.click()
			element.clear()
			element.send_keys(text)

		return element

 	# scraper.input_file_add_files('input[accept="image/jpeg,image/png,image/webp"]', images_path)
	def input_file_add_files(self, selector, files):
		# Intialize the condition to wait
		wait_until = EC.presence_of_element_located((By.CSS_SELECTOR, selector))

		try:
			# Wait for input_file to load
			input_file = WebDriverWait(self.driver, self.wait_element_time).until(wait_until)
		except TimeoutException:
			print('ERROR: Timed out waiting for the input_file with selector "' + selector + '" to load')
			# End the program execution because we cannot find the input_file
			exit()

		self.wait_random_time()

		try:
			input_file.send_keys(files)
		except InvalidArgumentException:
			print('ERROR: Exiting from the program! Please check if these file paths are correct:\n' + files)
			exit()

	# Wait random time before clearing the element (popup)
	def element_clear(self, css_selector='',xpath='', loop_count=1, exit_on_missing_element = False, warnings=False, delay = True):
		
		element = self.find_element(css_selector=css_selector, xpath=xpath, loop_count=loop_count, exit_on_missing_element=exit_on_missing_element, warnings=warnings)

		if element:
			if delay:
				self.wait_random_time()
			element.clear()

		return element 
		# Element is either webdriver element or None

	def element_wait_to_be_invisible(self, selector):
		wait_until = EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))

		try:
			WebDriverWait(self.driver, self.wait_element_time).until(wait_until)
		except:
			print('Error waiting the element with selector "' + selector + '" to be invisible')

	def open_new_tab(self, url):
		try:
			self.driver.execute_script(f"window.open('{url}');")	#Causing javascript error: missing ) after argument list.
			self.driver.switch_to.window(self.driver.window_handles[1])
			return True
		except:
			return False
  
	def close_tab_and_back_homepage(self):
		self.driver.close()
		self.driver.switch_to.window(self.driver.window_handles[0])

	def switch_to_tab(self, tab_index):
		tab_index = int(tab_index)
		self.driver.switch_to.window(self.driver.window_handles[tab_index])
  
	def find_element_on_element(self, ref_element, css_selector='', xpath='', loop_count=1, exit_on_missing_element=False, warnings=False):
		
		element = None
		selector = css_selector or xpath
  
		for i in range(loop_count):
			try:
				if css_selector:
					element = ref_element.find_element(By.CSS_SELECTOR, css_selector)
				elif xpath:
					element = ref_element.find_element(By.XPATH, xpath)
				else:
					print('ERROR: CSS_SELECTOR | XPATH is required')
					exit()
					
				return element

			except TimeoutException:
				if warnings:
					print(f'WARNING TRY {i+1}: element {selector} is not found yet')
				self.wait_random_time()

		if exit_on_missing_element:
			print(f'ERROR: Timed out waiting for the element with selector {selector} to load')
			exit()
   
		return None

	def find_elements_on_element(self, ref_element, css_selector='', xpath='', loop_count=1, exit_on_missing_element=False, warnings=False):
		
		elements = None
		selector = css_selector or xpath
  
		for i in range(loop_count):
			try:
				if css_selector:
					elements = ref_element.find_elements(By.CSS_SELECTOR, selector)
				elif xpath:
					elements = ref_element.find_elements(By.XPATH, selector)
				else:
					print('ERROR: CSS_SELECTOR | XPATH is required')
					exit()
					
				return elements

			except TimeoutException:
				if warnings:
					print(f'WARNING: TRY{i+1}: Unable to locate the element {selector} yet')
				self.wait_random_time()

		if exit_on_missing_element:
			print(f'ERROR: Timed out waiting for the element with selector {selector} to load')
			exit()
   
		return None
     
	def click_element_by_javaScript(self, element):
		# If the element is not clickable in normal way try this function
		self.driver.execute_script('arguments[0].click()', element)
		return element

	def get_network_log(self):
		logs = self.driver.execute_script('''
                                    var performance = window.performance || 
                                    window.mozPerformance || 
                                    window.msPerformance || 
                                    window.webkitPerformance || {}; 
                                    var network = performance.getEntries() || {}; 
                                    return network; 
                                    ''')
		return logs
