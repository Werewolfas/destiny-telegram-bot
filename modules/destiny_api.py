import pysyncdest


class DestinyApi:

    def __init__(self, config):
        self.lang = config['Lang']
        self.__url = 'https://www.bungie.net'
        self.destiny = pysyncdest.Pysyncdest(config['Key'], config['ClientId'], config['ClientSecret'])

    def get_nightfall(self):
        activities = self.destiny.api.get_public_milestones()['Response']
        milestones = {}
        milestones['public_event'] = \
            self.destiny.decode_hash(activities['463010297']['availableQuests'][0]['questItemHash'],
                                     'DestinyInventoryItemDefinition',
                                     self.lang)['displayProperties']['name']
        for quest in activities['2171429505']['availableQuests']:
            nightfall_info = self.destiny.decode_hash(quest['activity']['activityHash'], 'DestinyActivityDefinition',
                                                 self.lang)
            milestones['name'] = nightfall_info['displayProperties']['name']
            milestones['description'] = nightfall_info['displayProperties']['description']
            milestones['screen'] = self.__url + nightfall_info['pgcrImage']
            milestones['mods'] = []
            for mods in quest['activity']['modifierHashes']:
                modifier = self.destiny.decode_hash(mods, 'DestinyActivityModifierDefinition', self.lang)
                milestones['mods'].append({'name': modifier['displayProperties']['name'],
                                          'description': modifier['displayProperties']['description']})
        return milestones

    def get_trials_of_nine(self):
        activities = self.destiny.api.get_public_milestones()['Response']
        trials = {}
        try:
            activity = activities['3551755444']['availableQuests'][0]
            trials['error'] = 0
            trials['name'] = self.destiny.decode_hash(activity['questItemHash'],
                                                      'DestinyInventoryItemDefinition',
                                                      self.lang)['displayProperties']['name']
            map_info = self.destiny.decode_hash(activity['activity']['activityHash'],
                                                'DestinyActivityDefinition',
                                                self.lang)
            trials['map_name'] = map_info['displayProperties']['name']
            trials['map_description'] = map_info['displayProperties']['description']
            trials['map_screen'] = self.__url + map_info['pgcrImage']
            trials['mode'] = str.replace(self.destiny.decode_hash(activity['activity']['activityModeHash'],
                                                                  'DestinyActivityModeDefinition',
                                                                  self.lang)
                                         ['displayProperties']['name'],
                                         'Испытания Девяти: ', '')
        except KeyError:
            trials['error'] = 1
        return trials

    def get_clan_weekly_reward_state(self, clan_id):
        rewards = self.destiny.api.get_clan_weekly_reward_state(clan_id)['Response']
        definitions = self.destiny.api.get_milestone_definitions(rewards['milestoneHash'])['Response']['rewards']
        rewards_info = []
        for reward in rewards['rewards']:
            info = {}
            category = definitions[str(reward['rewardCategoryHash'])]
            info['name'] = category['displayProperties']['name']
            info['reward'] = []
            for entry in reward['entries']:
                entry_info = \
                    {'name': category['rewardEntries'][str(entry['rewardEntryHash'])]['displayProperties']['name'],
                     'earned': entry['earned']}
                info['reward'].append(entry_info)
            rewards_info.append(info)
        return rewards_info

    def get_token(self, refresh_token):
        return self.destiny.oauth.refresh_token(refresh_token)

    def get_xur_items(self, token):
        vendor = '2190858386'
        text = self.destiny.api.get_vendor(token, 2, 4611686018446750060, 2305843009262034932, vendor, ['402'])
        items = list(text['Response']['sales']['data'].values())
        xur_items = {}
        xur_items['error'] = 0
        xur_items['store'] = []
        xur_items['icons'] = []
        for item in items:
            store_item = {}
            item_info = self.destiny.decode_hash(item['itemHash'], 'DestinyInventoryItemDefinition', self.lang)
            store_item['name'] = item_info['displayProperties']['name']
            if 'itemTypeDisplayName' in item_info:
                store_item['description'] = item_info['itemTypeDisplayName']
            else:
                store_item['description'] = ''
            if 'classType' in item_info:
                store_item['class'] = item_info['classType']
            else:
                store_item['class'] = 3
            xur_items['icons'].append(self.__url + item_info['displayProperties']['icon'])
            store_item['price'] = item['costs'][0]['quantity']
            currency = self.destiny.decode_hash(item['costs'][0]['itemHash'],
                                                'DestinyInventoryItemDefinition',
                                                self.lang)
            store_item['currency_icon'] = self.__url + currency['displayProperties']['icon']
            store_item['currency_name'] = currency['displayProperties']['name']
            xur_items['store'].append(store_item)
        return xur_items

    def get_eververse_items(self, token):
        vendor = '3361454721'
        text = self.destiny.api.get_vendor(token, 2, 4611686018446750060, 2305843009262034932, vendor, ['402'])
        items = list(text['Response']['sales']['data'].values())
        xur_items = {}
        xur_items['error'] = 0
        xur_items['store'] = []
        xur_items['icons'] = []
        for item in items:
            store_item = {}
            if item['saleStatus'] != 9999 and len(item['costs']) != 0 and item['costs'][0]['itemHash'] != 3147280338:
                item_info = self.destiny.decode_hash(item['itemHash'], 'DestinyInventoryItemDefinition', self.lang)
                store_item['name'] = '{}: {}'.format(item_info['itemTypeAndTierDisplayName'],
                                                     item_info['displayProperties']['name'])
                xur_items['icons'].append(self.__url + item_info['displayProperties']['icon'])
                store_item['price'] = item['costs'][0]['quantity']
                currency = self.destiny.decode_hash(item['costs'][0]['itemHash'],
                                                    'DestinyInventoryItemDefinition',
                                                    self.lang)
                store_item['currency_icon'] = self.__url + currency['displayProperties']['icon']
                store_item['currency_name'] = currency['displayProperties']['name']
                xur_items['store'].append(store_item)
        return xur_items





