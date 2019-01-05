from configparser import ConfigParser
from os import environ
from platform import system
from tkinter import Tk, filedialog, StringVar, Message
from tkinter.ttk import Button, Entry, Label, Progressbar, Treeview, Scrollbar, Frame, Style

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

        # Opened config window already

        # TODO add sections for organization

        user_params = ConfigParser()
        user_params.read('config/conf.ini')

        # Window initialization

        # root.deiconify()
        # self.root = root
        # self.root.deiconify()

        self.scale = 1

        if system() == 'Linux':
            self.scale = 2

        self.width = 600 * self.scale
        self.height = 475 * self.scale

        self.x_center = self.winfo_screenwidth() / 2 - self.width / 2
        self.y_center = self.winfo_screenheight() / 2 - self.height / 2

        self.recorder = Recorder()  # TODO put init speaker, mic in config
        self.recorder.start()

        # self.config()

        self.configure(background='gray92')
        self.protocol('WM_DELETE_WINDOW', self.disconnect)

        self.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x_center, self.y_center))

        self.playlist = Playlist(user_params.getint('ICECAST', 'ChunkSize'))

        self.shouter = Shouter(user_params, self.playlist)
        self.shouter.start()

        self.recording_speaker = False
        self.recording_microphone = False

        self.chunk_size = user_params.getint('ICECAST', 'ChunkSize')
        self.host = user_params.get('ICECAST', 'Host')
        self.mount = user_params.get('ICECAST', 'Mount')

        self.update_time = 100  # milleseconds

        self.focused_items = ()

        self.style = Style()

        self.upload_button = Button(self, text='Upload', takefocus=False, command=self.choose_upload)

        self.pause_button = Button(self, text='Pause', takefocus=False, command=self.toggle_pause)

        self.skip_button = Button(self, text='Skip', takefocus=False, command=self.skip)

        self.recorder_frame = Frame(self)

        self.speaker_frame = Frame(self.recorder_frame)

        self.microphone_frame = Frame(self.recorder_frame)

        # self.speaker_label = Label(self.speaker_frame, text='Speaker')

        self.record_speaker_button = Button(self.speaker_frame, width=10, text=f'Speaker {chr(10005)}',
                                            takefocus=False, command=self.record_speaker)

        # self.microphone_label = Label(self.microphone_frame, text='Microphone')

        self.record_microphone_button = Button(self.microphone_frame, width=10, text=f'Microphone {chr(10005)}',
                                               takefocus=False, command=self.record_microphone)

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

    def config(self):
        def destroy():
            config_window.destroy()
            # window.destroy()
            # self.deiconify()

        config_window = Tk()
        config_window.configure(background='gray92')
        config_window.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x_center, self.y_center))
        config_window.title('Setup Pystation')
        config_window.protocol('WM_DELETE_WINDOW', destroy)

        finish_button = Button(config_window, text='Finish', command=destroy)

        finish_button.place(x=self.width - 100 * self.scale, y=self.height - 75 * self.scale)

        config_window.wait_window()
        return None  # ? need?

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

        self.now_playing_label.pack(pady=10 * self.scale)

        self.progress_bar.pack()

        self.progress_label.pack()

        self.youtube_input.bind('<Return>', func=lambda _: self.youtube_download(self.youtube_input.get()))
        self.youtube_input.pack(pady=10 * self.scale)

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
        self.recording_speaker = not self.recording_speaker

        if self.recording_speaker:
            status = chr(10003)
            # TODO disable other buttons
        else:
            status = chr(10005)
            # enable buttons

        self.record_speaker_button['text'] = f'Speaker {status}'

        self.playlist.record_speaker(self.recording_speaker, self.recorder)
        self.recorder.set_recording_speaker(self.recording_speaker)

    def record_microphone(self):
        self.recording_microphone = not self.recording_microphone

        if self.recording_microphone:
            status = chr(10003)
            # TODO disable other buttons? maybe not? test first
        else:
            status = chr(10005)
            # enable buttons

        self.record_microphone_button['text'] = f'Microphone {status}'

        self.playlist.record_microphone(self.recording_microphone, self.recorder)
        self.recorder.set_recording_microphone(self.recording_microphone)

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

        connection_status = chr(10003) if self.shouter.get_connected() else chr(10005)

        self.title(f'{connection_status} Pystation@{self.host}{self.mount}')

        now_playing = self.playlist.get_current_track()  # Track object

        if not self.playlist.get_paused() and now_playing:
            now_playing_name = repr(now_playing)
            now_playing_length = now_playing.get_length()

            progress = self.playlist.progress / now_playing.get_num_chunks()
            now_playing_time = progress * now_playing_length

        else:  # idle or recording
            if self.recording_speaker or self.recording_microphone:
                progress = 1
                now_playing_name = 'LIVE'
            else:  # idle
                progress = 0
                now_playing_name = 'Idle'

            now_playing_time = 0
            now_playing_length = 0

        # update progress bar and label
        if not self.playlist.get_paused():
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
        self.recorder.join()
        self.destroy()


def run_player():
    # Config window
    outputs = ConfigWindow()
    outputs.mainloop()
    print('done with config')

    # Main player
    root = Player()
    root.mainloop()
