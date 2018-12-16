import os
from math import floor
from tkinter import Tk, filedialog, StringVar
from tkinter.ttk import Button, Entry, Label, Progressbar, Treeview, Scrollbar, Frame, Style
import platform

from thread_decorator import thread

filetypes = ['.mp3', '.flac', '.ogg', '.m4a', '.webm', '.mp4']
FILEDIALOG_TYPES = ' '.join(f'*{filetype}' for filetype in filetypes)


class Player:
    def __init__(self, master, user_params, playlist):
        # Window initialization

        self.master = master
        # self.master.resizable(width=False, height=False)

        self.scale = 1

        if platform.system() == 'Linux':
            self.scale = 2

        self.width = 600 * self.scale
        self.height = 400 * self.scale

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        self.x_center = screen_width / 2 - self.width / 2
        self.y_center = screen_height / 2 - self.height / 2

        self.master.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x_center, self.y_center))
        self.master.title(f'Pystation@{user_params.get("ICECAST", "Host")}{user_params.get("ICECAST", "Mount")}')

        self.playlist = playlist

        self.chunk_size = user_params.getint('ICECAST', 'ChunkSize')

        self.update_time = 100  # in milleseconds

        self.focused_items = []

        self.style = Style()

        self.upload_button = Button(self.master, text='Upload', command=self.choose_upload)

        self.pause_button = Button(self.master, text='Pause', command=self.toggle_pause)

        self.skip_button = Button(self.master, text='Skip', command=self.skip)

        self.now_playing_label_text = StringVar()

        self.now_playing_label = Label(self.master, background='gray92', textvariable=self.now_playing_label_text)

        self.progress_bar = Progressbar(self.master, orient='horizontal', length=300 * self.scale,
                                        mode='determinate', maximum=1000)

        self.progress_label = Label(self.master, font='Menlo', background='gray92')

        self.youtube_input = Entry(self.master, width=40, font='Menlo')

        self.playlist_frame = Frame(self.master)

        self.playlist_frame_display = Frame(self.playlist_frame)

        self.playlist_frame_controls = Frame(self.playlist_frame)

        self.playlist_tree = Treeview(self.playlist_frame_display, height=12, columns='Length', selectmode='extended')

        self.playlist_scrollbar = Scrollbar(self.playlist_frame_display, command=self.playlist_tree.yview)

        self.remove_track_button = Button(self.playlist_frame_controls, text='Remove', command=self.remove_tracks)

        self.move_tracks_up_button = Button(self.playlist_frame_controls, text='Up', command=self.move_tracks_up)

        self.move_tracks_down_button = Button(self.playlist_frame_controls, text='Down', command=self.move_tracks_down)

        self.init_ui()

        self.update_player()

    def init_ui(self):
        self.style.configure('Treeview.Heading', font=(None, 10))
        self.style.configure('TFrame', background='gray92')

        self.upload_button.pack()

        self.pause_button.pack()

        self.skip_button.pack()

        self.now_playing_label.pack(pady=10)

        self.progress_bar.pack()

        self.progress_label.pack()

        self.youtube_input.bind('<Return>', func=lambda _: self.youtube_download(self.youtube_input.get()))
        self.youtube_input.pack(pady=10)

        self.playlist_frame.pack(side='bottom')

        self.playlist_frame_display.pack(side='left')

        self.playlist_frame_controls.pack(side='right')

        self.playlist_tree.heading('#0', text='Track', anchor='center')
        self.playlist_tree.column('#0', width=400 * self.scale, minwidth=300 * self.scale)
        self.playlist_tree.heading(column='Length', text='Length', anchor='center')
        self.playlist_tree.column(column='Length', width=50 * self.scale, minwidth=50 * self.scale)
        self.playlist_tree.configure(yscrollcommand=self.playlist_scrollbar.set)
        self.playlist_tree.pack(side='left')

        self.playlist_scrollbar.pack(side='right', fill='y')

        self.remove_track_button.pack(padx=10)

        self.move_tracks_up_button.pack(padx=10)

        self.move_tracks_down_button.pack(padx=10)

    @thread
    def choose_upload(self):
        filenames = filedialog.askopenfilenames(initialdir=f'{os.environ["HOME"]}/Downloads',
                                                title='Select File',
                                                filetypes=([('Audio', FILEDIALOG_TYPES)]))
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

    def youtube_download(self, url):
        if '&list' in url:  # don't download playlist
            # consider downloading all in list
            url = url[:url.index('&list')]
        self.playlist.add_youtube_track(url)

    def update_player(self):
        def seconds_to_time(seconds):
            seconds = int(seconds)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)

            if hours:
                return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, floor(seconds))
            else:
                return '{:02d}:{:02d}'.format(minutes, floor(seconds))

        now_playing = self.playlist.get_current_track()  # Track object

        if not self.playlist.get_paused() and now_playing:
            now_playing_name = repr(now_playing)
            now_playing_time = self.playlist.get_play_time()
            now_playing_length = now_playing.get_length()

            progress = now_playing_time / now_playing_length * 1000

            self.playlist.increment_play_time(self.update_time * 1.01)  # account for slight lag

        else:  # idle
            now_playing_name = 'Idle'
            now_playing_time = 0
            now_playing_length = 0
            progress = 0

        # update progress bar and label
        if not self.playlist.get_paused():
            self.progress_bar['value'] = progress
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
                self.focused_items = []

            self.playlist.update()

        self.master.after(self.update_time, self.update_player)

    def remove_tracks(self):
        selected = self.playlist_tree.selection()
        if selected:
            self.playlist.remove_tracks((int(index) for index in reversed(selected)))

    def move_tracks_up(self):
        selected = self.playlist_tree.selection()

        if '0' in selected:  # can't move up
            return
        elif selected:
            self.playlist.move_tracks_up((int(index) for index in reversed(selected)))
            self.focused_items = [str(int(index) - 1) for index in selected]

    def move_tracks_down(self):
        selected = self.playlist_tree.selection()

        if str(len(self.playlist_tree.get_children()) - 1) in selected:  # can't move down
            return
        elif selected:
            self.playlist.move_tracks_down((int(index) for index in reversed(selected)))
            self.focused_items = [str(int(index) + 1) for index in selected]


def run_player(user_params, playlist):
    root = Tk()
    root.configure(background='gray92')
    _ = Player(root, user_params, playlist)

    root.mainloop()
