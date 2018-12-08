import os
from math import floor
from tkinter import Tk, filedialog, StringVar
from tkinter.ttk import Button, Entry, Label, Progressbar, Treeview, Scrollbar, Frame

from thread_decorator import thread

filetypes = ['.mp3', '.flac', '.ogg', '.m4a', '.webm', '.mp4']
FILEDIALOG_TYPES = ' '.join(f'*{filetype}' for filetype in filetypes)


class Player:
    def __init__(self, master, user_params, playlist):
        # Window initialization

        self.master = master
        self.master.resizable(width=False, height=False)

        self.width = 600
        self.height = 400

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        self.x_center = screen_width / 2 - self.width / 2
        self.y_center = screen_height / 2 - self.height / 2

        self.master.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x_center, self.y_center))
        self.master.title(f'Pystation@{user_params.get("ICECAST", "Host")}{user_params.get("ICECAST", "Mount")}')

        self.playlist = playlist

        self.chunk_size = user_params.getint('ICECAST', 'Chunk Size')

        self.update_time = 100  # in milleseconds

        self.upload_button = Button(self.master, text='Upload', command=self.choose_upload)

        self.pause_button = Button(self.master, text='Pause', command=self.toggle_pause)

        self.skip_button = Button(self.master, text='Skip', command=self.skip)

        self.youtube_input = Entry(self.master, width=40)

        self.now_playing_label_text = StringVar()

        self.now_playing_label = Label(self.master, textvariable=self.now_playing_label_text)

        self.progress_bar = Progressbar(self.master, orient='horizontal', length=300, mode='determinate', maximum=1000)

        self.progress_label = Label(self.master, font='Menlo')

        self.playlist_frame = Frame(self.master)

        self.playlist_tree = Treeview(self.playlist_frame, height=12, columns='Length', selectmode='extended')

        self.playlist_scrollbar = Scrollbar(self.playlist_frame, command=self.playlist_tree.yview)

        self.init_ui()

        self.update_player()

    def init_ui(self):

        self.upload_button.pack()

        self.pause_button.pack()

        self.skip_button.pack()

        self.youtube_input.bind('<Return>', func=lambda _: self.youtube_download(self.youtube_input.get()))
        self.youtube_input.configure(font='Menlo')
        self.youtube_input.pack()

        self.now_playing_label.pack()

        self.progress_bar.pack()

        self.progress_label.pack()

        self.playlist_frame.configure()
        self.playlist_frame.pack(side='bottom')

        self.playlist_tree.heading('#0', text='Track', anchor='center')
        self.playlist_tree.column('#0', width=400, minwidth=100)
        self.playlist_tree.heading(column='Length', text='Length', anchor='center')
        self.playlist_tree.column(column='Length', width=50, minwidth=50)
        self.playlist_tree.configure(yscrollcommand=self.playlist_scrollbar.set)
        self.playlist_tree.pack(side='left')

        # self.playlist_scrollbar.place(x=590, y=0, height=400)
        # self.playlist_scrollbar.place(bordermode='outside', anchor='e', height=200)
        self.playlist_scrollbar.pack(side='right', fill='y')

    @thread
    def choose_upload(self):
        print('upload')
        filenames = filedialog.askopenfilenames(initialdir=f'{os.environ["HOME"]}/Downloads',
                                                title='Select File',
                                                filetypes=([('Audio', FILEDIALOG_TYPES)]))
        [self.playlist.add_track(filename) for filename in filenames]

    def toggle_pause(self):
        paused_bool = self.playlist.get_paused()
        if paused_bool:
            self.pause_button['text'] = 'Pause'
            print('play')
        else:
            self.pause_button['text'] = 'Play'
            print('pause')
        self.playlist.set_paused(not paused_bool)

    def skip(self):
        print('skip')
        self.playlist.skip_track()

    def youtube_download(self, url):
        if '&list' in url:  # don't download playlist
            # consider downloading all in list
            url = url[:url.index('&list')]
        print(f'yt download: {url}')
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

        # update playlist tree
        if not self.playlist.get_updated():
            self.playlist_tree.delete(*self.playlist_tree.get_children())
            for track in self.playlist.get_tracks():
                self.playlist_tree.insert('', 'end', text=repr(track), values=seconds_to_time(track.get_length()))
            self.playlist.update()

        self.master.after(self.update_time, self.update_player)


def run_player(user_params, playlist):
    root = Tk()
    root.configure(background='gray92')
    _ = Player(root, user_params, playlist)

    root.mainloop()
