import yaml
from datetime import datetime
from random import randint # could also use randrange
from time import sleep

def log(message):
    date_string = datetime.now().strftime(config['log-date-format'])
    line = f'[{date_string}] {message}'

    print(line)
    with open(config['log-path'], 'a') as f:
        f.write(f'{line}\n')

if __name__ == '__main__':
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    while True:
        log("Hello")

        sleep_len = randint(config['sleep-min'], config['sleep-max'])
        sleep(sleep_len)