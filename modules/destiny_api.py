import pysyncdest


class DestinyApi:

    def __init__(self, key, lang):
        self.key = key
        self.lang = lang
        self.__url = 'https://www.bungie.net'
        self.destiny = pysyncdest.Pysyncdest(self.key)

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









