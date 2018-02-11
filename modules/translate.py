
class Translate:

    translations = {
        'Clan Rewards': 'Награды клана',
        'Crucible': 'Горнило',
        'Nightfall': 'Сумрачный налет',
        'Raid': 'Рейд',
        'Trials of the Nine': 'Испытания Девяти',
        'Last Week\'s Clan Rewards': 'Награды клана за прошлую неделю'
    }

    classes = {
        #  Titan
        0: 'Титан',
        #  Hunter
        1: 'Охотник',
        #  Warlock
        2: 'Варлок'
    }

    def make_translation(self, trans_string):
        try:
            return self.translations[trans_string]
        except KeyError:
            return trans_string

    def get_game_class(self, class_id):
        try:
            return self.classes[class_id]
        except KeyError:
            return class_id

