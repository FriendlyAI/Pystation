import os
from tkinter import Tk, filedialog
from tkinter.ttk import Button, Entry


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
        self.master.title('Pystation Player')

        self.playlist = playlist

        # self.chunk_size = int(user_params['ICECAST']['Chunk Size'])
        self.chunk_size = user_params.getint('ICECAST', 'Chunk Size')

        self.paused = False

        self.upload_button = Button(self.master, text='Upload', command=self.choose_upload)

        self.pause_button = Button(self.master, text='Pause', command=self.toggle_pause)

        self.skip_button = Button(self.master, text='Skip', command=self.skip)

        self.youtube_input = Entry(self.master, width=20)

        self.init_ui()

    def init_ui(self):

        self.upload_button.pack()

        self.pause_button.pack()

        self.skip_button.pack()

        self.youtube_input.bind('<Return>', func=lambda _: self.youtube_download(self.youtube_input.get()))
        self.youtube_input.configure(font='Menlo')
        self.youtube_input.pack()

    def choose_upload(self):
        print('upload')
        filenames = filedialog.askopenfilenames(initialdir=f'{os.environ["HOME"]}/Downloads',
                                                title='Select File',
                                                filetypes=([('Audio', '*.mp3 *.flac')]))
        [self.playlist.add_track(filename) for filename in filenames]

    def toggle_pause(self):
        paused_bool = self.playlist.get_paused()
        if paused_bool:
            self.pause_button['text'] = 'Pause'
        else:
            self.pause_button['text'] = 'Play'
        self.playlist.set_paused(not paused_bool)
        print('pause toggled')

    def skip(self):
        print('skip')
        self.playlist.skip_track()

    def youtube_download(self, url):
        print(f'yt download: {url}')
        self.playlist.add_track(url=url)


def run_player(user_params, playlist):
    root = Tk()
    _ = Player(root, user_params, playlist)

    # tab_control = ttk.Notebook(root)  # Create Tab Control
    # player = ttk.Frame(tab_control)  # Create a tab
    # tab_control.add(player, text='Tab 1')  # Add the tab
    # player.pack(expand=1, fill='both')  # Pack to make visible

    root.mainloop()
