from configparser import ConfigParser
from os import environ, path
from platform import system
from tkinter import Tk, filedialog, StringVar, Message
from tkinter.messagebox import askyesno
from tkinter.simpledialog import askstring
from tkinter.ttk import Button, Entry, Label, Progressbar, Treeview, Scrollbar, Frame, Style, Scale

from auto_tag import get_mpv_tags, get_progress
from config import ConfigWindow
from playlist import Playlist
from recorder import Recorder
from shouter import Shouter
from thread_decorator import thread

filetypes = ('*.mp3', '*.flac', '*.ogg', '*.aac', '*.webm', '*.mp4')
FILEDIALOG_TYPES = ' '.join(filetypes)


class Player(Tk):
    def __init__(self):
        super(Player, self).__init__()

        # Get user preferences

        user_params = ConfigParser()
        user_params.read(path.join('config', 'conf.ini'))

        # Window initialization

        self.toplevel = int(user_params.get('SYSTEM', 'toplevel'))
        if self.toplevel:
            self.attributes("-topmost", True)  # keep window on top

        self.scale = 1
        if system() == 'Linux':
            self.scale = 2

        self.width = 600 * self.scale
        self.height = 550 * self.scale

        self.x_center = self.winfo_screenwidth() / 2 - self.width / 2
        self.y_center = self.winfo_screenheight() / 2 - self.height / 2

        self.configure(background='gray92')
        self.protocol('WM_DELETE_WINDOW', self.disconnect)

        self.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x_center, self.y_center))

        # Speaker and microphone

        speaker_id = user_params.get('SYSTEM', 'speakerid')
        microphone_id = user_params.get('SYSTEM', 'microphoneid')

        self.recorder = Recorder(speaker_id, microphone_id)
        self.recorder.start()

        # User parameters

        self.chunk_size = user_params.getint('ICECAST', 'chunksize')
        self.host = user_params.get('ICECAST', 'host')
        self.mount = user_params.get('ICECAST', 'mount')
        self.name = user_params.get('ICECAST', 'name')
        self.mpv_tags = int(user_params.get('SYSTEM', 'mpvtags'))

        # Playlist

        self.playlist = Playlist(self.chunk_size)
        self.playlist.set_live_track(self.recorder.get_track())

        # Shouter

        self.shouter = Shouter(user_params, self.playlist)
        self.shouter.start()

        # Player objects

        self.update_time = 100  # milleseconds

        self.focused_items = ()

        self.style = Style()

        # Buttons

        self.upload_button = Button(self, text='Upload', takefocus=False, command=self.choose_upload)

        self.pause_button = Button(self, text='Pause', takefocus=False, command=self.toggle_pause)

        self.skip_button = Button(self, text='Skip', takefocus=False, command=self.skip)

        # Recorder buttons

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

        # Volume scale

        self.volume_scale = Scale(self, length=200 * self.scale, from_=0, to=2, value=1, command=self.set_volume)

        # Microphone scale

        self.microphone_scale = Scale(self, length=200 * self.scale, from_=0, to=10, value=5,
                                      command=self.set_microphone_volume)

        # Now playing

        self.now_playing_label_text = StringVar()

        self.now_playing_label = Message(self, width=500 * self.scale, justify='center', background='gray92',
                                         textvariable=self.now_playing_label_text)
        self.now_playing_label.bind('<Button-1>', lambda _: self.override_trackname())

        # Progress bar

        self.progress_bar = Progressbar(self, orient='horizontal', length=300 * self.scale, mode='determinate',
                                        maximum=1000)

        self.progress_label = Label(self, font='Menlo', background='gray92')

        # Youtube input

        self.youtube_input = Entry(self, width=40, font='Menlo')

        # Playlist treeview

        self.playlist_frame = Frame(self)

        self.playlist_frame_display = Frame(self.playlist_frame)

        self.playlist_frame_controls = Frame(self.playlist_frame)

        self.playlist_tree = Treeview(self.playlist_frame_display, height=12, columns=('Track', 'Length'),
                                      selectmode='extended')

        self.playlist_scrollbar = Scrollbar(self.playlist_frame_display, command=self.playlist_tree.yview)

        # Playlist controls

        self.move_tracks_up_button = Button(self.playlist_frame_controls, text='Up', takefocus=False,
                                            command=self.move_tracks_up)

        self.move_tracks_down_button = Button(self.playlist_frame_controls, text='Down', takefocus=False,
                                              command=self.move_tracks_down)

        self.remove_track_button = Button(self.playlist_frame_controls, text='Remove', takefocus=False,
                                          command=self.remove_tracks)

        # Pack UI

        self.init_ui()

        # Begin refreshing player

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

        self.microphone_scale.pack()

        self.now_playing_label.pack(pady=10 * self.scale)

        self.progress_bar.pack()

        self.progress_label.pack()

        self.youtube_input.bind('<Return>', func=lambda _: self.youtube_download(self.youtube_input.get()))
        self.youtube_input.pack(pady=20 * self.scale)

        self.playlist_frame.pack(side='bottom')

        self.playlist_frame_display.pack(side='left')

        self.playlist_frame_controls.pack(side='right')

        self.playlist_tree.heading('#0', text='#')
        self.playlist_tree.column('#0', width=30 * self.scale, minwidth=30 * self.scale)
        self.playlist_tree.heading(column='Track', text='Track', anchor='center')
        self.playlist_tree.column(column='Track', width=395 * self.scale, minwidth=300 * self.scale)
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
        self.attributes("-topmost", False)
        filenames = filedialog.askopenfilenames(initialdir=f'{path.join(environ["HOME"], "Downloads")}',
                                                title='Select File',
                                                filetypes=[('Audio', FILEDIALOG_TYPES)])
        if self.toplevel:
            self.attributes("-topmost", True)
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
        else:
            status = self.disconnected_symbol

        self.record_speaker_button['text'] = f'Speaker {status}'

        self.recorder.set_recording_speaker(self.playlist.is_recording_speaker())

    def record_microphone(self):
        self.playlist.toggle_recording_microphone()

        if self.playlist.is_recording_microphone():
            status = self.recording_symbol
        else:
            status = self.disconnected_symbol

        self.record_microphone_button['text'] = f'Microphone {status}'

        self.recorder.set_recording_microphone(self.playlist.is_recording_microphone())

    def set_volume(self, volume):
        self.recorder.set_amplification(float(volume))

    def set_microphone_volume(self, volume):
        self.recorder.set_microphone_volume(float(volume))

    def override_trackname(self):
        self.attributes("-topmost", False)
        new_trackname = askstring('Override Trackname', 'Enter new trackname',
                                  initialvalue=self.now_playing_label_text.get(), parent=self)
        if self.toplevel:
            self.attributes("-topmost", True)

        current_track = self.playlist.get_current_track()
        if new_trackname and current_track:
            new_trackname = new_trackname.strip()
            current_track.set_trackname(new_trackname)
            self.update_trackname()

    def update_trackname(self):
        track = self.playlist.get_current_track()
        trackname = track.get_trackname() if track else 'IDLE'
        self.now_playing_label_text.set(trackname)
        self.shouter.update_metadata(trackname)

    def update_mpv_trackname(self):
        if self.playlist.is_recording_speaker():
            trackname = get_mpv_tags()
            if trackname:
                self.now_playing_label_text.set(trackname)
                self.shouter.update_metadata(trackname)
            else:
                self.update_trackname()

        progress, current_track_time, current_track_length = get_progress()

        if progress + current_track_time + current_track_length == 0:
            self.set_progress(self.recorder.get_volume(), 0, 0)
        else:
            self.set_progress(progress, current_track_time, current_track_length)

    def set_progress(self, progress, current_track_time, current_track_length):
        self.progress_bar['value'] = progress * 1000
        self.progress_label.config(
            text=f'{seconds_to_time(current_track_time)}/{seconds_to_time(current_track_length)}')

    def youtube_download(self, url):
        if not url:
            return
        if '&list' in url:  # don't download playlist
            url = url[:url.index('&list')]
        self.playlist.add_youtube_track(url)

    def update_player(self):

        connection_status = self.connected_symbol if self.shouter.get_connected() else self.disconnected_symbol

        self.title(f'{connection_status} {self.name}@{self.host}{self.mount}')

        current_track = self.playlist.get_current_track()  # Track object

        # if self.playlist.is_recording():
        #     progress = self.recorder.get_volume()
        #     current_track_time = 0
        #     current_track_length = 0

        if not self.playlist.is_recording() and not self.playlist.get_paused() and current_track:
            current_track_length = current_track.get_length()

            try:
                progress = self.playlist.progress / current_track.get_num_chunks()
            except ZeroDivisionError:
                progress = 0

            current_track_time = progress * current_track_length

        else:  # idle
            progress = 0
            current_track_time = 0
            current_track_length = 0

        # force update mpv trackname and progress
        if self.mpv_tags and self.playlist.is_recording_speaker():
            self.update_mpv_trackname()

        else:
            if not self.playlist.get_paused() or self.playlist.is_recording():
                self.set_progress(progress, current_track_time, current_track_length)

            # update now playing name
            if self.playlist.get_trackname_updated():
                self.update_trackname()
                self.playlist.update_trackname()

        # update playlist tree
        if self.playlist.get_playlist_updated():
            self.playlist_tree.delete(*self.playlist_tree.get_children())
            for index, track in enumerate(self.playlist.get_tracks()):
                self.playlist_tree.insert('', 'end', iid=index, text=int(index) + 1,
                                          values=(track.get_trackname(), seconds_to_time(track.get_length())))
            if self.focused_items:
                for index in self.focused_items:
                    self.playlist_tree.selection_add(index)
                self.focused_items = ()

            self.playlist.update_playlist()

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
        self.attributes("-topmost", False)
        if askyesno('Disconnect', 'Disconnect and close?'):
            self.recorder.join()
            self.destroy()
        elif self.toplevel:
            self.attributes("-topmost", True)


def seconds_to_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    else:
        return '{:02d}:{:02d}'.format(minutes, seconds)


def run_player():
    # Config window
    config_window = ConfigWindow()
    config_window.mainloop()

    # Main player
    root = Player()
    root.mainloop()
