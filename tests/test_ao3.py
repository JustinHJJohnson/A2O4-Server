import unittest
import mock
from A2O4 import ao3, common

class Test_Ao3(unittest.TestCase):
    def test_map(self):
        config = common.Config({
            'download_path': '',
            'ao3_username': '',
            'ao3_password': '',
            'devices': [],
            'fandom_filter': {},
            'fandom_map': {
                'Fallout 4': 'Fallout',
                'Fallout (Video Games)': 'Fallout',
                "Baldur's Gate (Video Games)": "Baldur's Gate",
                'Cyberpunk 2077 (Video Game)': 'Cyberpunk 2077',
                'Cyberpunk & Cyberpunk 2020 (Roleplaying Games)': 'Cyberpunk 2077',
                'Persona 5': 'Persona',
                'Persona 4': 'Persona',
                'Persona 3': 'Persona',
                'Shin Megami Tensei Series': 'Shin Megami Tensei',
                '逆転裁判 | Gyakuten Saiban | Ace Attorney': 'Ace Attorney',
                '大逆転裁判 | Dai Gyakuten Saiban | The Great Ace Attorney Chronicles (Video Games)': 'Ace Attorney',
                'NieR = Automata (Video Game)': 'NieR',
                'Dungeons & Dragons (Roleplaying Game)': 'Dungeons & Dragons'
            },
        })

        filter_fandoms = ao3.map_and_filter_fandoms(
            [
                'Fallout 4',
                "Cyberpunk & Cyberpunk 2020 (Roleplaying Games)",
                "大逆転裁判 | Dai Gyakuten Saiban | The Great Ace Attorney Chronicles (Video Games)",
                "Baldur's Gate (Video Games)"
            ],
            config
        )
        
        self.assertCountEqual(filter_fandoms, ["Baldur's Gate", 'Cyberpunk 2077', 'Ace Attorney', 'Fallout'])

    def test_filter(self):
        config = common.Config({
            'download_path': '',
            'ao3_username': '',
            'ao3_password': '',
            'devices': [],
            'fandom_filter': {
                'Work 1': ['Work 1-2', 'Work 1-3'],
                'Work 2': ['Work 2-1']
            },
            'fandom_map': {}
        })

        filter_fandoms = ao3.map_and_filter_fandoms(
            [
                'Work 1',
                'Work 2',
                'Work 1-2',
                'Work 1-3',
                'Work 2-1'
            ],
            config
        )
        
        self.assertCountEqual(filter_fandoms, ['Work 1', 'Work 2'])

    def test_both(self):
        config = common.Config({
            'download_path': '',
            'ao3_username': '',
            'ao3_password': '',
            'devices': [],
            'fandom_map': {
                'Fallout 4': 'Fallout',
                'Fallout (Video Games)': 'Fallout',
                "Baldur's Gate (Video Games)": "Baldur's Gate",
                'Cyberpunk 2077 (Video Game)': 'Cyberpunk 2077',
                'Cyberpunk & Cyberpunk 2020 (Roleplaying Games)': 'Cyberpunk 2077',
                'Persona 5': 'Persona',
                'Persona 4': 'Persona',
                'Persona 3': 'Persona',
                'Shin Megami Tensei Series': 'Shin Megami Tensei',
                '逆転裁判 | Gyakuten Saiban | Ace Attorney': 'Ace Attorney',
                '大逆転裁判 | Dai Gyakuten Saiban | The Great Ace Attorney Chronicles (Video Games)': 'Ace Attorney',
                'NieR = Automata (Video Game)': 'NieR',
                'Dungeons & Dragons (Roleplaying Game)': 'Dungeons & Dragons'
            },
            'fandom_filter': {
                "Baldur's Gate": ['Dungeons & Dragons'],
                'Persona': ['Shin Megami Tensei']
            }
        })

        filter_fandoms = ao3.map_and_filter_fandoms(
            [
                'Dungeons & Dragons (Roleplaying Game)',
                'Fallout 4',
                "Cyberpunk & Cyberpunk 2020 (Roleplaying Games)",
                "大逆転裁判 | Dai Gyakuten Saiban | The Great Ace Attorney Chronicles (Video Games)",
                "Baldur's Gate (Video Games)"
            ],
            config
        )
        
        self.assertCountEqual(filter_fandoms, ["Baldur's Gate", 'Cyberpunk 2077', 'Ace Attorney', 'Fallout'])



if __name__ == '__main__':
    unittest.main()