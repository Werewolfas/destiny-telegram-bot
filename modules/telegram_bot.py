# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
from emoji import emojize
from modules.destiny_api import DestinyApi
import configparser


class TelegramBot:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.destiny = DestinyApi(self.config['Bungie']['Key'], self.config['Bungie']['Lang'])

        self.updater = Updater(self.config['Telegram']['Key'])

        self.updater.dispatcher.add_handler(CommandHandler('weekly', self.weekly))
        self.updater.dispatcher.add_handler(CommandHandler('rewards', self.clan_rewards))
        self.updater.dispatcher.add_handler(CommandHandler('help', self.help))

        self.updater.start_polling()
        self.updater.idle()

    def weekly(self, bot, update):
        weekly = self.destiny.get_nightfall()
        text = '*{}*\n\n'.format(weekly['public_event'])
        text = '{}*{}* \n{} \n*Модификаторы:* \n'.format(text, weekly['name'], weekly['description'])
        for mod in weekly['mods']:
            text = '{} – {}. {}\n'.format(text, mod['name'], mod['description'])
        text = '{}\n[\u200B]({})'.format(text, weekly['screen'])
        bot.send_message(chat_id=update.message.chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

    def clan_rewards(self, bot, update):
        rewards = self.destiny.get_clan_weekly_reward_state(self.config['Bungie']['ClanId'])
        text = ''
        for category in rewards:
            text = '{}<b>{}</b>\n'.format(text, category['name'])
            for reward in category['reward']:
                if reward['earned']:
                    earned = ':white_check_mark:'
                else:
                    earned = ':x:'
                text = '{}  - {}: {}\n'.format(text, reward['name'], earned)

        bot.send_message(chat_id=update.message.chat_id,
                         text=emojize(text, use_aliases=True),
                         parse_mode=ParseMode.HTML)

    def help(self, bot, update):
        text = '<b>/rewards</b> - информация о закрытых еженедельных клановых активностях\n' \
               '<b>/weekly</b> - информация о недельных заданиях\n'
        bot.send_message(chat_id=update.message.chat_id,
                         text=text,
                         parse_mode=ParseMode.HTML)
