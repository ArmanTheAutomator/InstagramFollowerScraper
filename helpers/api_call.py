from asyncio import exceptions
import requests

def get_instagram_followers_api_call(user_id, max_id, cookie, csrftoken, warnings=False):
    
    max_id_query = f'&max_id={max_id}' if max_id else ''

    url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=100{max_id_query}&search_surface=follow_list_page"

    headers = {
    "cookie": f'{cookie}',
    "x-csrftoken": f"{csrftoken}",
    "authority": "i.instagram.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.instagram.com",
    "referer": "https://www.instagram.com/",
    "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "x-asbd-id": "198387",
    "x-ig-app-id": "936619743392459",
    "x-ig-www-claim": "hmac.AR0MfR8zteN3hi01smjJBx30LFs4ZCjyViU52EtsS-YLoi8B"
    }

    users = []
    next_max_id = ''
    status = ''
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        
        res_status = data['status']
        if res_status == 'ok':
            users = data['users']
            try:
                next_max_id = data['next_max_id']
                status = 'success'
            except:
                next_max_id = ''
                status = 'last_page'
        elif res_status == 'fail':
            try:
                spam = data['spam']
                if spam == True:
                    status = 'bot'
            except:
                status = data['message']
            
    except:
        status = 'not_logged_in'
        if warnings:
                print('\nRequesting API:')
                print('Request URL: ', url)
                print('Request Headers: ')
                for key in headers.keys():
                    print(f"'{key}' : '{headers[key]}'")


    # Extract usernames
    usernames = []
    for user in users:
        usernames.append(user['username'])
    
    return usernames, next_max_id, status

# data, _ = get_instagram_followers_api_call('208560325', '')
# print('\nDATA: ', data)