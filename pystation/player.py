from configparser import ConfigParser
from os import environ
from platform import system
from tkinter import Tk, filedialog, StringVar, Message, messagebox
from tkinter.ttk import Button, Entry, Label, Progressbar, Treeview, Scrollbar, Frame, Style, Scale

from config import ConfigWindow
from playlist import Playlist
from recorder import Recorder
from shout import Shouter
from thread_decorator import thread

filetypes = ('*.mp3', '*.flac', '*.ogg', '*.aac', '*.webm', '*.mp4')
FILEDIALOG_TYPES = ' '.join(filetypes)


class Player(Tk):
    def __init__(self):
        super(Player, self).__init__()

        # TODO add sections for organization

        user_params = ConfigParser()
        user_params.read('config/conf.ini')

        # Window initialization

        if int(user_params.get('SYSTEM', 'toplevel')):
            self.call('wm', 'attributes', '.', '-topmost', '1')  # keep window on top

        self.scale = 1
        if system() == 'Linux':
            self.scale = 2

        self.width = 600 * self.scale
        self.height = 500 * self.scale

        self.x_center = self.winfo_screenwidth() / 2 - self.width / 2
        self.y_center = self.winfo_screenheight() / 2 - self.height / 2

        self.configure(background='gray92')
        self.protocol('WM_DELETE_WINDOW', self.disconnect)

        self.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x_center, self.y_center))

        speaker_id = user_params.get('SYSTEM', 'speakerid')
        microphone_id = user_params.get('SYSTEM', 'microphoneid')

        self.recorder = Recorder(speaker_id, microphone_id)
        self.recorder.start()

        self.chunk_size = user_params.getint('ICECAST', 'chunksize')
        self.host = user_params.get('ICECAST', 'host')
        self.mount = user_params.get('ICECAST', 'mount')
        self.name = user_params.get('ICECAST', 'name')

        self.playlist = Playlist(self.chunk_size)

        self.shouter = Shouter(user_params, self.playlist, self.chunk_size)
        self.shouter.start()

        self.update_time = 100  # milleseconds

        self.focused_items = ()

        self.style = Style()

        self.upload_button = Button(self, text='Upload', takefocus=False, command=self.choose_upload)

        self.pause_button = Button(self, text='Pause', takefocus=False, command=self.toggle_pause)

        self.skip_button = Button(self, text='Skip', takefocus=False, command=self.skip)

        self.recorder_frame = Frame(self)

        self.speaker_frame = Frame(self.recorder_frame)

        self.microphone_frame = Frame(self.recorder_frame)

        self.recording_symbol = chr(9679)
        self.disconnected_symbol = chr(10005)
        self.connected_symbol = chr(10003)

        self.record_speaker_button = Button(self.speaker_frame, width=11,
                                            text=f'Speaker {self.disconnected_symbol}',
                                            takefocus=False, command=self.record_speaker)

        self.record_microphone_button = Button(self.microphone_frame, width=11,
                                               text=f'Microphone {self.disconnected_symbol}',
                                               takefocus=False, command=self.record_microphone)

        self.volume_scale = Scale(self, length=200 * self.scale, from_=0, to=2, value=1, command=self.set_volume)

        self.now_playing_label_text = StringVar()

        self.now_playing_label = Message(self, width=500 * self.scale, justify='center', background='gray92',
                                         textvariable=self.now_playing_label_text)
        # TODO change to multiline tkinter.text

        self.progress_bar = Progressbar(self, orient='horizontal', length=300 * self.scale, mode='determinate',
                                        maximum=1000)

        self.progress_label = Label(self, font='Menlo', background='gray92')

        self.youtube_input = Entry(self, width=40, font='Menlo')

        self.playlist_frame = Frame(self)

        self.playlist_frame_display = Frame(self.playlist_frame)

        self.playlist_frame_controls = Frame(self.playlist_frame)

        self.playlist_tree = Treeview(self.playlist_frame_display, height=10, columns='Length', selectmode='extended')

        self.playlist_scrollbar = Scrollbar(self.playlist_frame_display, command=self.playlist_tree.yview)

        self.move_tracks_up_button = Button(self.playlist_frame_controls, text='Up', takefocus=False,
                                            command=self.move_tracks_up)

        self.move_tracks_down_button = Button(self.playlist_frame_controls, text='Down', takefocus=False,
                                              command=self.move_tracks_down)

        self.remove_track_button = Button(self.playlist_frame_controls, text='Remove', takefocus=False,
                                          command=self.remove_tracks)

        self.init_ui()

        self.update_player()

    def init_ui(self):
        self.style.configure('TFrame', background='gray92')
        self.style.configure('Treeview', rowheight=20 * self.scale)

        self.upload_button.pack()

        self.pause_button.pack()

        self.skip_button.pack()

        self.recorder_frame.pack()

        self.speaker_frame.pack(side='left')

        self.microphone_frame.pack(side='right')

        self.record_speaker_button.pack()

        self.record_microphone_button.pack()

        self.volume_scale.pack()

        self.now_playing_label.pack(pady=10 * self.scale)

        self.progress_bar.pack()

        self.progress_label.pack()

        self.youtube_input.bind('<Return>', func=lambda _: self.youtube_download(self.youtube_input.get()))
        self.youtube_input.pack(pady=20 * self.scale)

        self.playlist_frame.pack(side='bottom')

        self.playlist_frame_display.pack(side='left')

        self.playlist_frame_controls.pack(side='right')

        self.playlist_tree.heading('#0', text='Track', anchor='center')
        self.playlist_tree.column('#0', width=425 * self.scale, minwidth=300 * self.scale)
        self.playlist_tree.heading(column='Length', text='Length', anchor='center')
        self.playlist_tree.column(column='Length', width=50 * self.scale, minwidth=50 * self.scale)
        self.playlist_tree.configure(yscrollcommand=self.playlist_scrollbar.set)
        self.playlist_tree.pack(side='left')

        self.playlist_scrollbar.pack(side='right', fill='y')

        self.move_tracks_up_button.pack(padx=10 * self.scale)

        self.move_tracks_down_button.pack(padx=10 * self.scale)

        self.remove_track_button.pack(padx=10 * self.scale)

    @thread
    def choose_upload(self):
        filenames = filedialog.askopenfilenames(initialdir=f'{environ["HOME"]}/Downloads',
                                                title='Select File',
                                                filetypes=[('Audio', FILEDIALOG_TYPES)])
        [self.playlist.add_track(filename) for filename in filenames]

    def toggle_pause(self):
        paused_bool = self.playlist.get_paused()
        if paused_bool:
            self.pause_button['text'] = 'Pause'
        else:
            self.pause_button['text'] = 'Play'
        self.playlist.set_paused(not paused_bool)

    def skip(self):
        self.playlist.skip_track()

    def record_speaker(self):
        self.playlist.toggle_recording_speaker()

        if self.playlist.is_recording_speaker():
            status = self.recording_symbol
            self.playlist.record_speaker(self.recorder)
        else:
            status = self.disconnected_symbol

        self.record_speaker_button['text'] = f'Speaker {status}'

        self.recorder.set_recording_speaker(self.playlist.is_recording_speaker())

    def record_microphone(self):
        self.playlist.toggle_recording_microphone()

        if self.playlist.is_recording_microphone():
            status = self.recording_symbol
            self.playlist.record_microphone(self.recorder)
        else:
            status = self.disconnected_symbol

        self.record_microphone_button['text'] = f'Microphone {status}'

        self.recorder.set_recording_microphone(self.playlist.is_recording_microphone())

    def set_volume(self, volume):
        self.recorder.set_amplification(float(volume))

    def youtube_download(self, url):
        if not url:
            return
        if '&list' in url:  # don't download playlist
            url = url[:url.index('&list')]
        self.playlist.add_youtube_track(url)

    def update_player(self):
        def seconds_to_time(seconds):
            minutes, seconds = divmod(int(seconds), 60)
            hours, minutes = divmod(minutes, 60)

            if hours:
                return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
            else:
                return '{:02d}:{:02d}'.format(minutes, seconds)

        connection_status = self.connected_symbol if self.shouter.get_connected() else self.disconnected_symbol

        self.title(f'{connection_status} {self.name}@{self.host}{self.mount}')

        now_playing = self.playlist.get_current_track()  # Track object

        if self.playlist.is_recording():
            progress = self.recorder.get_volume()
            now_playing_name = 'LIVE'

            now_playing_time = 0
            now_playing_length = 0

        elif not self.playlist.get_paused() and now_playing:
            now_playing_name = repr(now_playing)
            now_playing_length = now_playing.get_length()

            progress = self.playlist.progress / now_playing.get_num_chunks()
            now_playing_time = progress * now_playing_length

        else:  # idle
            progress = 0
            now_playing_name = 'Idle'

            now_playing_time = 0
            now_playing_length = 0

        # update progress bar and label
        if not self.playlist.get_paused() or self.playlist.is_recording():
            self.progress_bar['value'] = progress * 1000
            self.progress_label.config(
                text=f'{seconds_to_time(now_playing_time)}/{seconds_to_time(now_playing_length)}')

        # update now playing name
        self.now_playing_label_text.set(now_playing_name)

        if not self.playlist.get_updated():
            # update playlist tree
            self.playlist_tree.delete(*self.playlist_tree.get_children())
            for index, track in enumerate(self.playlist.get_tracks()):
                self.playlist_tree.insert('', 'end', iid=index, text=repr(track),
                                          values=seconds_to_time(track.get_length()))
            if self.focused_items:
                for index in self.focused_items:
                    self.playlist_tree.selection_add(index)
                self.focused_items = ()

            self.playlist.update()

        self.after(self.update_time, self.update_player)

    def remove_tracks(self):
        selected = self.playlist_tree.selection()

        if selected:
            self.playlist.remove_tracks((int(index) for index in reversed(selected)))

    def move_tracks_up(self):
        selected = self.playlist_tree.selection()
        tree_length = len(self.playlist_tree.get_children())

        if '0' in selected:  # can't move up
            return
        elif selected:
            selected = [int(index) for index in selected]
            self.playlist.move_tracks_up(selected)
            self.focused_items = (str(index - 1) for index in selected)
            self.playlist_tree.yview_moveto((selected[0] - 1) / tree_length)

    def move_tracks_down(self):
        selected = self.playlist_tree.selection()
        tree_length = len(self.playlist_tree.get_children())

        if str(tree_length - 1) in selected:  # can't move down
            return
        elif selected:
            selected = [int(index) for index in selected]
            self.playlist.move_tracks_down(reversed(selected))
            self.focused_items = (str(index + 1) for index in selected)
            self.playlist_tree.yview_moveto((selected[-1] + 1) / tree_length)

    def disconnect(self):
        self.withdraw()
        if messagebox.askyesno('Disconnect', 'Disconnect and close?'):
            self.recorder.join()
            self.destroy()
        else:
            self.deiconify()


def run_player():
    # Config window
    outputs = ConfigWindow()
    outputs.mainloop()

    # Main player
    root = Player()
    root.mainloop()
