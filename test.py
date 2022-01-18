import requests

sess = requests.Session()
data = {
    "display_language": "de",
    "login_email_username": "m.hoffmann@systemli.org",
    "login_form_auto_login": "1",
    "login_password": "p*%J7AuN%cR$2p7",
}
response = sess.post('https://www.wg-gesucht.de/ajax/sessions.php?action=login', json=data)

print(response)