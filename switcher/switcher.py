import numpy as np
from kivy.app import App
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from functools import partial
from kivy.uix.slider import Slider
from player import PlayerWidget
from align import align_audios

class SwitcherWidget(Widget):
    """
    Class responsible for initializing each audio player, calling the alignment functions and switching between audios
    """
    # initializing
    def __init__(self, filelist, **kwargs):
        super().__init__(**kwargs) # Necessary since it inherits from Widget
        self.players = []
        for filename in filelist:
            self.players.append(PlayerWidget(filename))
        self.warp_dict = align_audios(filelist)
        self.currentPlayer = self.players[0]

    # Method for getting the index of the corresponding frame of an original frame
    # first takes first match
    # last takes last match
    # avg takes the rounded average of the indexes matching original frame and uses it to get the corresponding frame
    def get_corresponding_frame(self, origin, target, origin_frame, method = 'avg'):
        if method =='first':
            idx = np.where(self.warp_dict[(origin, target)][:,0] == origin_frame)[0][0]
        elif method =='last':
            idx = np.where(self.warp_dict[(origin, target)][:,0] == origin_frame)[0][-1]
        elif method == 'avg':
            idx = int(round(np.average(np.where(self.warp_dict[(origin, target)][:,0] == origin_frame)[0])))
        else:
            raise ValueError('Invalid method. Please use \'avg\', \'first\' or \'last\'')
        return self.warp_dict[(origin, target)][idx, 1]


    # method for switching between two players
    def switch(self, target, center = False, *args):
        origin = self.players.index(self.currentPlayer) # Getting index of original player
        if origin != target: # If they are the same no need to do anything
            # Pausing origin player
            continue_play = self.players[origin].is_playing # record if it is playing so that we can continue to play
            self.players[origin].pause()

            # Setting target player to corresponding position
            origin_frame = self.players[origin].get_frame()
            target_frame = self.get_corresponding_frame(origin, target, origin_frame)
            self.players[target].set_frame(target_frame, center = center)

            # Set target player as current player
            self.currentPlayer = self.players[target]
            if continue_play == True:
                self.players[target].play()

    # method for pausing
    def pause(self):
        player = self.currentPlayer
        player.pause()

    # method for playing
    def play(self):
        player = self.currentPlayer
        player.play()

    def close(self):
        for player in self.players:
            player.close()

class SwitcherLayout(StackLayout):
    def __init__(self, filelist, **kwargs):
        super().__init__(**kwargs)
        self.switcher = SwitcherWidget(filelist)
        pause = Button(text = 'Pause', text_size = self.size, size_hint = (0.5, 0.5), halign = 'center', valign = 'center')
        pause.on_press = self.switcher.pause
        play = Button(text = 'Play', text_size = self.size, size_hint = (0.5, 0.5), halign = 'center', valign = 'center')
        play.on_press = self.switcher.play
        self.add_widget(play)
        self.add_widget(pause)
        for player in self.switcher.players:
            btn = Button(text = str(self.switcher.players.index(player)), size_hint = (1/len(self.switcher.players), 0.5))
            btn.bind(on_press = partial(self.switcher.switch, self.switcher.players.index(player)))
            self.add_widget(btn)

# class TestApp(App):
#     def build(self):
#         self.switcher_layout = SwitcherLayout(['Chopin Prelude Op. 28 No. 7 MIDI.wav', 'Chopin Prelude Op. 28 No. 7 N. Freire.wav', 'Chopin Prelude Op. 28 No. 7 M. Pollini.wav'])
#         Window.bind(on_request_close=self.on_request_close)
#         return self.switcher_layout
#
#     def on_request_close(self, *args):
#         self.switcher_layout.switcher.close()
#         Window.close()
#         return True
#
# if __name__ == '__main__':
#     app = TestApp()
#     app.run()
