from sys import exit
import os
import random
import time

from helpers.scraper import Scraper
from helpers.functions import formatted_time, data_countdown, countdown, execution_time
from helpers.files import read_csv, read_txt, write_to_csv, write_to_txt
from helpers.numbers import formatted_number_with_comma, numbers_within_text, str_to_int
from helpers.api_call import get_instagram_followers_api_call
from helpers.cookie_functions import read_cookie

# Start time of the program
START_TIME = time.time()

# Global variables Initialization
inputs = read_txt('inputs/credentials')
try:
    PASSWORD = inputs[2].split('=')[1].strip()
    USERNAME = inputs[1].split('=')[1].strip() or inputs[0].split('=')[1].strip()
except:
    pass

if USERNAME == '' or PASSWORD == '':
    print('Credentials.txt file or EMAIL or USERNAME or PASSWORD is missing')
    exit()

url = 'https://www.instagram.com'
query_username = input('Enter username: ').strip() or 'khloekardashian'
try:
    #Recommended to keep the max_limit less than 20k. Otherwise it will be detected as bot
    max_limit = str_to_int(input('Number of followers to scrape, press ENTER for all follower: '))
except:
    max_limit = None
    
scraper = Scraper(url)


def get_id_from_network_log():
    logs = scraper.get_network_log()
    for log in logs:
        req_url = log['name']
        if 'https://i.instagram.com/api/v1/friendships/' in req_url and '/followers/' in req_url:
            id = req_url.split('/')[6]
            try:
                return int(id)
            except:
                pass
    return None

def find_user_id(loop_count=10):
    id = None
    for i in range(loop_count):
        id = get_id_from_network_log()
        if id:
            break
        else:
            time.sleep(1)
    
    return id
        
def login():
    scraper.element_send_keys(USERNAME, 'input[name="username"]', loop_count=10)
    scraper.wait_random_time()
    scraper.element_send_keys(PASSWORD, 'input[name="password"]')
    
    # Clicking on Submit button
    scraper.wait_random_time()
    scraper.element_click('button[type="submit"]')
    scraper.wait_random_time(3.5, 5.0)

def total_followers(username):
    scraper.wait_random_time()
    scraper.go_to_page(f'https://www.instagram.com/{username}')
    scraper.wait_random_time(2.0, 4.0)
    
    a_tag = scraper.find_element(f'a[href="/{username}/followers/"]', loop_count=10)
    scraper.wait_random_time(0.2, 0.4)
    a_tag.click()
    span = scraper.find_element_on_element(a_tag, 'span')
    follower_count = span.get_attribute('title')
    try:
        return str_to_int(follower_count)
    except:
        return 0

# Three step Login. 1:Using cookies, 2:By Selenium UI interaction with given credentials, 3:Manual login Then press any key
cookie_file_name = 'insta_cookie'
login_status = scraper.add_login_functionality(url, 'svg[aria-label="Home"]', login, cookie_file_name)
if login_status == False:
    print('Sorry, We are failed to login Instagram.')
    exit()
cookie_str, csrf_token = read_cookie(cookie_file_name)


#Variable Initialization
followers = read_txt(f'outputs/{query_username}')         
previous_data_length = len(followers)

no_of_follower = total_followers(query_username)
print(f'{query_username} has {no_of_follower} followers.\n')


user_id = find_user_id()      #The id against a username. Required to send API requests.
if user_id:
    no_of_call = no_of_follower / 95
    no_of_call = no_of_call if int(no_of_call) == no_of_call else no_of_call + 1
    
    # Close the browser
    scraper.wait_random_time(2.0, 2.5)
    scraper.driver.close()
    
    max_id = ''
    for i in range(int(no_of_call)):
        new_followers, new_max_id, status = get_instagram_followers_api_call(user_id, max_id, cookie=cookie_str, csrftoken=csrf_token, warnings=True)
        if status == 'success' or status == 'last_page':
            max_id = new_max_id
            for f in new_followers:
                if f not in followers:
                    followers.append(f)
            
            write_to_txt(followers, 'USERNAMES', f'outputs/{query_username}')
            message_string = f'More {len(new_followers)} username collected. Total: {len(followers) - previous_data_length} Data, From: {i+1} API Request'
            data_countdown(message_string)
            
            if status == 'last_page': #Data end condition
                print('\nWe have reached end of the data')
                break
        
        elif status == 'bot':
            print('\nUnable to fetch data from API. Suspected as bot. Try few hours later.')
            break
        
        elif status == 'not_logged_in':        
            print('\nUnable to fetch data from API. We are not logged in, Try restarting the program.')
            break
        
        else:
            print(f'\nUnable to fetch data from API. {status}')
            x = input('1. Try API request again\n2. Exit the program\nPress 1 or 2: ')
            if x == '2':
                break
        
        if max_limit:
            if (len(followers) - previous_data_length) >= max_limit:
                print('\nWe have reached maximum data limit')
                break
        
        if i > 0 and i % 10 == 0:
            countdown(round(random.randint(180, 300)), '3-5 Minute Break after 10 API requests: ')
        else:
            scraper.wait_random_time(0.4, 2.0)

else:
    print(f'\nNo user id found with username: {query_username}')


# Footer for time & data reporting
execution_time(START_TIME, (len(followers) - previous_data_length))
     
