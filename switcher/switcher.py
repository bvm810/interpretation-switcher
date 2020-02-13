from kivy.uix.widget import Widget
from player import PlayerWidget
from align import align_audios

class SwitcherWidget(Widget):
    """
    Class responsible for initializing each audio player, calling the alignment functions and switching between audios
    """

    def __init__(self, filelist, **kwargs):
        super().__init__(**kwargs) # Necessary since it inherits from Widget
        self.players = []
        for filename in filelist:
            self.players.append(PlayerWidget(filename))

        self.warp_dict = align_audios(filelist)
