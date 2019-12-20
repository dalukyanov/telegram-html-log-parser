import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import argparse


def parse_telegram_log(text):
    """
    :param text: contents of messagesN.html
    :return: Pandas dataframe with chat history
    """

    soup = BeautifulSoup(text, 'lxml')

    message_default_clearfixes = []

    for message_default_clearfix in soup.find_all('div', {'class': 'message default clearfix'}):
        message_default_clearfixes.append(message_default_clearfix)

    chat_log = []

    for mdc in message_default_clearfixes:
        try:
            time = mdc.find('div', {'class': ['pull_right date details']}).get('title')
        except AttributeError:
            time = None
        try:
            name = mdc.find('div', {'class': ['from_name']}).text.strip()
        except AttributeError:
            name = None
        try:
            text = mdc.find('div', {'class': ['text']}).text.strip()
        except AttributeError:
            text = None
        chat_item = [time, name, text]
        chat_log.append(chat_item)

    chat_data = pd.DataFrame(chat_log, columns=['timestamp', 'username', 'text'])
    return chat_data.dropna()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parses Telegram Desktop html chat log into chat_full.csv')
    chat_full = None

    parser.add_argument('--path', dest='path', action='store',
                        help='Full path to ChatExport_DD_MM_YYYY directory', required=True)

    args = parser.parse_args()
    path = args.path

    htmls = [html for html in os.listdir(path) if html.endswith('.html')]
    for html in htmls:
        full_path = path + '\\' + html
        text = ''
        with open(full_path, encoding='utf-8') as f:
            for line in f.readlines():
                text += line
        res = parse_telegram_log(text)
        chat_full = res if chat_full is None else chat_full.append(res)
        chat_full.info()

    chat_full.to_csv(r'chat_full.csv', index=None, header=True)