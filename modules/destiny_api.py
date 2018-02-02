import pysyncdest


class DestinyApi:

    def __init__(self, key, lang):
        self.key = key
        self.lang = lang
        self.__url = 'https://www.bungie.net'
        self.destiny = pysyncdest.Pysyncdest(self.key)

    def get_nightfall(self):
        activites = self.destiny.api.get_public_milestones()
        nightfall = {}
        for quest in activites['Response']['2171429505']['availableQuests']:
            nightfall_info = self.destiny.decode_hash(quest['activity']['activityHash'], 'DestinyActivityDefinition',
                                                 self.lang)
            nightfall['name'] = nightfall_info['displayProperties']['name']
            nightfall['description'] = nightfall_info['displayProperties']['description']
            nightfall['screen'] = self.__url + nightfall_info['pgcrImage']
            nightfall['mods'] = []
            for mods in quest['activity']['modifierHashes']:
                modifier = self.destiny.decode_hash(mods, 'DestinyActivityModifierDefinition', self.lang)
                nightfall['mods'].append({'name': modifier['displayProperties']['name'],
                                          'description': modifier['displayProperties']['description']})
        return nightfall

    def get_clan_weekly_reward_state(self):
        rewards = self.destiny.api.get_clan_weekly_reward_state(2031167)['Response']
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









