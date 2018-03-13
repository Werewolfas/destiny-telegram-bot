# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
from emoji import emojize
from modules.destiny_api import DestinyApi
from modules.translate import Translate
from modules.image_magic import ImageMagic
from modules.dbase import DBase
import datetime
import json
import configparser
import logging


class TelegramBot:

    def __init__(self):
        logging.basicConfig(level=logging.WARNING,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.translations = Translate()
        self.destiny = DestinyApi(self.config['Bungie'])
        self.images = ImageMagic()
        self.dbase = DBase(self.config['Mysql'])
        self.chat_id = self.config['Telegram']['ChatId']

        self.updater = Updater(self.config['Telegram']['Key'])
        current_time = datetime.datetime.utcnow()
        xur_time = self.__get_next_weekday(current_time.replace(hour=17, minute=2, second=0), 4)
        eververse_time = self.__get_next_weekday(current_time.replace(hour=17, minute=2, second=15), 1)
        weekly_time = self.__get_next_weekday(current_time.replace(hour=17, minute=2, second=0), 1)
        self.updater.job_queue.run_repeating(self.xur_scheduled, interval=datetime.timedelta(days=7),
                                             first=xur_time)
        self.updater.job_queue.run_repeating(self.eververse_scheduled, interval=datetime.timedelta(days=7),
                                             first=eververse_time)
        self.updater.job_queue.run_repeating(self.weekly_scheduled, interval=datetime.timedelta(days=7),
                                             first=weekly_time)
        self.updater.dispatcher.add_handler(CommandHandler('weekly', self.weekly))
        self.updater.dispatcher.add_handler(CommandHandler('trials', self.trials))
        self.updater.dispatcher.add_handler(CommandHandler('rewards', self.clan_rewards))
        self.updater.dispatcher.add_handler(CommandHandler('xur', self.xur))
        self.updater.dispatcher.add_handler(CommandHandler('eververse', self.eververse))
        self.updater.dispatcher.add_handler(CommandHandler('help', self.help))

        self.updater.start_polling()
        self.updater.idle()

    def weekly(self, bot, update):
        weekly = self.__get_weekly()
        bot.send_message(chat_id=update.message.chat_id,
                         text=weekly['text'],
                         parse_mode=ParseMode.MARKDOWN)

    def weekly_scheduled(self, bot, update):
        weekly = self.__get_weekly()
        if weekly['error'] == 1:
            bot.send_message(chat_id=self.chat_id,
                             text=weekly['text'],
                             parse_mode=ParseMode.MARKDOWN)

    def clan_rewards(self, bot, update):
        rewards = self.destiny.get_clan_weekly_reward_state(self.config['Bungie']['ClanId'])
        if rewards['error'] == 1:
            text = ''
            for category in rewards['rewards']:
                text = '{}<b>{}</b>\n'.format(text, self.translations.make_translation(category['name']))
                sorted_reward = sorted(category['reward'], key=lambda k: k['name'])
                for reward in sorted_reward:
                    if reward['earned']:
                        earned = ':white_check_mark:'
                    else:
                        earned = ':x:'
                    name = str.replace(reward['name'], ' - Last Week', '')
                    text = '{}  - {}: {}\n'.format(text, self.translations.make_translation(name), earned)
                text = text + '\n'
        else:
            text = self.translations.make_translation(rewards['errorMessage'])
        bot.send_message(chat_id=update.message.chat_id,
                         text=emojize(text, use_aliases=True),
                         parse_mode=ParseMode.HTML)

    def trials(self, bot, update):
        trials = self.destiny.get_trials_of_nine()
        if trials['error'] == 1:
            text = '*{}*\n\n'.format(trials['name'])
            text = '{} Карта: {}\n'.format(text, trials['map_name'])
            text = '{} Место: {}\n'.format(text, trials['map_description'])
            text = '{} Режим: {}\n'.format(text, trials['mode'])
            text = '{}[\u200B]({})'.format(text, trials['map_screen'])
        else:
            text = 'Данных о событии нет'
        bot.send_message(chat_id=update.message.chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

    def xur(self, bot, update):
        xur_info = self.__get_xur_info()
        bot.send_message(chat_id=update.message.chat_id,
                         text=xur_info['text'],
                         parse_mode=ParseMode.MARKDOWN)
        if xur_info['image'] != '':
            bot.send_photo(chat_id=update.message.chat_id, photo=open('images/{}.jpg'.format(xur_info['image']), 'rb'))

    def xur_scheduled(self, bot, update):
        xur_info = self.__get_xur_info()
        bot.send_message(chat_id=self.chat_id,
                         text=xur_info['text'],
                         parse_mode=ParseMode.MARKDOWN)
        if xur_info['image'] != '':
            bot.send_photo(chat_id=self.chat_id, photo=open('images/{}.jpg'.format(xur_info['image']), 'rb'))

    def eververse(self, bot, update):
        info = self.__get_eververse()
        bot.send_message(chat_id=update.message.chat_id,
                         text=info['text'],
                         parse_mode=ParseMode.MARKDOWN)
        if info['image'] != '':
            bot.send_photo(chat_id=update.message.chat_id, photo=open('images/{}.jpg'.format(info['image']), 'rb'))

    def eververse_scheduled(self, bot, update):
        info = self.__get_eververse()
        if info['error'] == 1:
            bot.send_message(chat_id=self.chat_id,
                             text=info['text'],
                             parse_mode=ParseMode.MARKDOWN)
            if info['image'] != '':
                bot.send_photo(chat_id=self.chat_id, photo=open('images/{}.jpg'.format(info['image']), 'rb'))

    def help(self, bot, update):
        text = '<b>/rewards</b> - информация о закрытых еженедельных клановых активностях\n' \
               '<b>/weekly</b> - информация о недельных заданиях\n' \
               '<b>/trials</b> - информация о Испытаниях девяти\n'
        bot.send_message(chat_id=update.message.chat_id,
                         text=text,
                         parse_mode=ParseMode.HTML)

    def __token(self):
        user = self.dbase.get_user(self.config['Bungie']['User'])
        current_time = datetime.datetime.now()
        if user['access_token_expire'] > current_time:
            return user['access_token']
        else:
            if user['refresh_token_expire'] > current_time:
                info = self.destiny.get_token(user['refresh_token'])
                user['access_token'] = info['access_token']
                user['refresh_token'] = info['refresh_token']
                user['access_token_expire'] = current_time + datetime.timedelta(seconds=info['expires_in']-60)
                user['refresh_token_expire'] = current_time + datetime.timedelta(seconds=info['refresh_expires_in']-60)
                self.dbase.update_user_tokens(user)
                return user['access_token']
            else:
                print('No info')

    def __get_next_weekday(self, date, weekday):
        if date.weekday() == weekday:
            date += datetime.timedelta(1)
        while date.weekday() != weekday:
            date += datetime.timedelta(1)
        return date

    def __get_xur_info(self):
        current_time = datetime.datetime.utcnow()
        xur_info = {}
        if (current_time.weekday() in [0, 5, 6]) or (current_time.weekday() == 1 and current_time.hour < 17) or (
                current_time.weekday() == 4 and current_time.hour >= 17):
            parsed_data = self.dbase.get_parsed_data('xur', current_time)
            if parsed_data is None:
                token = self.__token()
                items = self.destiny.get_xur_items(token)
                image_name = 'xur{}{}{}'.format(current_time.year,
                                                current_time.month,
                                                current_time.day,
                                                current_time.hour)
                self.images.merge_images(items['icons'], image_name)
                expire_date = self.__get_next_weekday(current_time.replace(hour=17, minute=2, second=0), 1)
                self.dbase.add_parsed_data('xur',
                                           json.dumps(items, ensure_ascii=False).encode('utf8'),
                                           json.dumps(items, ensure_ascii=False).encode('utf8'),
                                           current_time,
                                           expire_date,
                                           image_name)
            else:
                items = json.loads(parsed_data['json_data'])
                image_name = parsed_data['image_name']
            if items['error'] == 0:
                text = ''
                for item in items['store']:
                    text = '{}\n\n*{}*\n'.format(text, item['name'])
                    if item['description'] != '':
                        text = '{} {}'.format(text, item['description'])
                        if item['class'] != 3:
                            text = '{}. {}'.format(text, self.translations.get_game_class(item['class']))
                        text = '{}\n'.format(text)
                    text = '{} Цена: {} {}'.format(text, item['price'], item['currency_name'])
                xur_info['text'] = text
                xur_info['image'] = image_name
        else:
            xur_info['text'] = 'Xur еще не прилетел'
            xur_info['image'] = ''
        return xur_info

    def __get_eververse(self):
        current_time = datetime.datetime.utcnow()
        parsed_data = self.dbase.get_parsed_data('eververse', current_time)
        eververse_info = {}
        image_name = ''
        text = ''
        if parsed_data is None:
            token = self.__token()
            items = self.destiny.get_eververse_items(token)
            if items['error'] == 1:
                image_name = 'eververse{}{}{}'.format(current_time.year,
                                                      current_time.month,
                                                      current_time.day,
                                                      current_time.hour)
                self.images.merge_images(items['icons'], image_name)
                expire_date = self.__get_next_weekday(current_time.replace(hour=17, minute=2, second=0), 1)
                if items['error'] == 1:
                    for item in items['store']:
                        text = '{}\n\n*{}*\n'.format(text, item['name'])
                        text = '{} Цена: {} {}'.format(text, item['price'], item['currency_name'])
                    self.dbase.add_parsed_data('eververse',
                                               json.dumps(items, ensure_ascii=False).encode('utf8'),
                                               text,
                                               current_time,
                                               expire_date,
                                               image_name)
        else:
            items = json.loads(parsed_data['json_data'])
            text = parsed_data['text_data']
            image_name = parsed_data['image_name']
        eververse_info['error'] = items['error']
        if items['error'] == 1:
            eververse_info['text'] = text
            eververse_info['image'] = image_name
        else:
            eververse_info['text'] = self.translations.make_translation(items['errorMessage'])
            eververse_info['image'] = ''
        return eververse_info

    def __get_weekly(self):
        weekly = self.destiny.get_nightfall()
        information = {}
        if weekly['error'] == 1:
            text = '*{}*\n\n'.format(weekly['public_event'])
            text = '{}*{}* \n{}'.format(text, weekly['name'], weekly['description'])
            information['text'] = '{}\n[\u200B]({})'.format(text, weekly['screen'])
        else:
            information['text'] = self.translations.make_translation(weekly['errorMessage'])
        information['error'] = weekly['error']
        return information


