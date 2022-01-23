from datetime import datetime
from random import randint # could also use randrange
from time import sleep
import yaml
import requests
from bs4 import BeautifulSoup

def log(message):
    date_string = datetime.now().strftime(config['log-date-format'])
    line = f'[{date_string}] {message}'

    print(line)
    with open(config['log-path'], 'a') as f:
        f.write(f'{line}\n')

class WGSession(requests.Session):
    def __init__(self, email, password):
        super().__init__()

        url = "https://www.wg-gesucht.de/ajax/sessions.php?action=login"
        data = {
            "login_email_username": email,
            "login_password": password,
            "login_form_autologin": "1",
            "display_language": "de"
        }

        login_response = self.post(url, json=data) # attempt login with provided data
        if login_response.status_code != 200:
            msg = f"Error logging in: {login_response.status_code}"
            log(msg)
            self.ad_ids = []
            return

        response = self.get("https://www.wg-gesucht.de/meine-anzeigen.html")
        soup = BeautifulSoup(response.text, 'html.parser')

        logout_btn = soup.find('a', class_='logout_button')
        ads = soup.find(id='my_requests').find_all('div', class_='wgg_card') # select only active ads
        
        self.ad_ids = [ad.attrs['id'].split('_')[-1] for ad in ads]
        self.csrf_token = logout_btn.attrs['data-csrf_token']
        self.user_id = logout_btn.attrs["data-user_id"]

        log(f'Login successful. csrf_token: {self.csrf_token}, ad ids: {self.ad_ids}')

    def toggle_activation(self, ad_id):
        api_url = f"https://www.wg-gesucht.de/api/requests/{ad_id}/users/{self.user_id}"
        headers = {
            "X-User-ID": self.user_id,
            "X-Client-ID": "wg_desktop_website",
            "X-Authorization": "Bearer " + self.cookies.get("X-Access-Token"),
            "X-Dev-Ref-No": self.cookies.get("X-Dev-Ref-No")
        }

        self.patch(api_url, 
            json={"deactivated": "1", "csrf_token": self.csrf_token}, headers=headers)
        r = self.patch(api_url, 
            json={"deactivated": "0", "csrf_token": self.csrf_token}, headers=headers)
       
        log(f"Updated ad #{ad_id}: {r.status_code}")

if __name__ == '__main__':
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    with open('secrets.yml', 'r') as secrets_file:
        secrets = yaml.safe_load(secrets_file)

    while True:
        with WGSession(secrets['email'], secrets['password']) as session:
            for ad in session.ad_ids:
                session.toggle_activation(ad)

        sleep_len = randint(config['sleep-min'], config['sleep-max']) * 60
        log(f"Sleeping for {sleep_len//60} minutes.")
        sleep(sleep_len)