
class Translate:

    translations = {
        'Clan Rewards': 'Награды клана',
        'Crucible': 'Горнило',
        'Nightfall': 'Сумрачный налет',
        'Raid': 'Рейд',
        'Trials of the Nine': 'Испытания Девяти',
        'Last Week\'s Clan Rewards': 'Награды клана за прошлую неделю'
    }

    def make_translation(self, trans_string):
        try:
            return self.translations[trans_string]
        except KeyError:
            return trans_string


