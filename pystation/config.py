from configparser import ConfigParser
from os import environ
from platform import system
from tkinter import Tk, filedialog, StringVar, Message, IntVar
from tkinter.ttk import Button, Entry, Label, Frame, Combobox, Checkbutton

from soundcard import all_microphones


class ConfigWindow(Tk):
    def __init__(self):
        super(ConfigWindow, self).__init__()

        self.scale = 1
        if system() == 'Linux':
            self.scale = 2

        self.width = 600 * self.scale
        self.height = 500 * self.scale

        self.x_center = int(self.winfo_screenwidth() / 2 - self.width / 2)
        self.y_center = int(self.winfo_screenheight() / 2 - self.height / 2)

        self.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x_center, self.y_center))
        self.title('Setup Pystation')
        self.protocol('WM_DELETE_WINDOW', self.finish)
        self.configure(background='gray92')

        self.user_params = ConfigParser()
        self.user_params.read('config/conf.ini')

        default_host = self.user_params.get('ICECAST', 'host', fallback='')
        default_port = self.user_params.get('ICECAST', 'port', fallback='')
        default_username = self.user_params.get('ICECAST', 'username', fallback='')
        default_password = self.user_params.get('ICECAST', 'password', fallback='')
        default_mount = self.user_params.get('ICECAST', 'mount', fallback='')
        default_chunksize = self.user_params.get('ICECAST', 'chunksize', fallback='')
        default_name = self.user_params.get('ICECAST', 'name', fallback='')
        default_description = self.user_params.get('ICECAST', 'description', fallback='')
        default_genre = self.user_params.get('ICECAST', 'genre', fallback='')
        default_idle = self.user_params.get('GENERAL', 'Idle', fallback='')
        default_speaker = self.user_params.get('SYSTEM', 'speakername', fallback='')
        default_microphone = self.user_params.get('SYSTEM', 'microphonename', fallback='')
        default_top = self.user_params.get('SYSTEM', 'toplevel', fallback='0')

        for section in ('ICECAST', 'GENERAL', 'SYSTEM'):  # if conf.ini doens't exist or is corrupt
            try:
                self.user_params[section]
            except KeyError:
                self.user_params.add_section(section)

        self.upper_frame = Frame(self)

        self.host_label = Label(self.upper_frame, text='Host')
        self.host_input = Entry(self.upper_frame, width=40, font='Menlo')
        self.host_input.insert(0, default_host)

        self.port_label = Label(self.upper_frame, text='Port')
        self.port_input = Entry(self.upper_frame, width=5, font='Menlo')
        self.port_input.insert(0, default_port)

        self.username_label = Label(self.upper_frame, text='Username')
        self.username_input = Entry(self.upper_frame, width=40, font='Menlo')
        self.username_input.insert(0, default_username)

        self.password_label = Label(self.upper_frame, text='Password')
        self.password_input = Entry(self.upper_frame, width=40, font='Menlo', show='*')
        self.password_input.insert(0, default_password)

        self.mount_label = Label(self.upper_frame, text='Mount')
        self.mount_input = Entry(self.upper_frame, width=40, font='Menlo')
        self.mount_input.insert(0, default_mount)

        self.chunksize_label = Label(self.upper_frame, text='Chunk size')
        self.chunksize_input = Entry(self.upper_frame, width=5, font='Menlo')
        self.chunksize_input.insert(0, default_chunksize)

        self.name_label = Label(self.upper_frame, text='Stream name')
        self.name_input = Entry(self.upper_frame, width=40, font='Menlo')
        self.name_input.insert(0, default_name)

        self.description_label = Label(self.upper_frame, text='Description')
        self.description_input = Entry(self.upper_frame, width=40, font='Menlo')
        self.description_input.insert(0, default_description)

        self.genre_label = Label(self.upper_frame, text='Genre')
        self.genre_input = Entry(self.upper_frame, width=40, font='Menlo')
        self.genre_input.insert(0, default_genre)

        self.mid_frame = Frame(self)

        self.idle_label = Label(self.mid_frame, text='Idle track')
        self.idle_input = Button(self.mid_frame, text='Choose idle track', takefocus=False,
                                 command=self.select_idle_file)
        self.idle_selected_text = StringVar()
        self.idle_selected_text.set(default_idle)
        self.idle_selected = Message(self.mid_frame, width=300 * self.scale, background='gray92',
                                     textvariable=self.idle_selected_text)

        self.lower_frame = Frame(self)

        self.speaker_label = Label(self.lower_frame, text='Speaker')

        speakers = [f'{repr(speaker)} ID: {speaker.id}'
                    for speaker in all_microphones(include_loopback=True)]

        self.speaker_text = StringVar()
        self.speaker_text.set(default_speaker)
        self.speaker_choice = Combobox(self.lower_frame, width=40, values=speakers,
                                       textvariable=self.speaker_text, state='readonly', takefocus=False)
        self.speaker_choice.bind('<<ComboboxSelected>>', lambda _: self.select_speaker())

        self.microphone_label = Label(self.lower_frame, text='Microphone')

        microphones = [f'{repr(microphone)} ID: {microphone.id}'
                       for microphone in all_microphones(include_loopback=False)]

        self.microphone_text = StringVar()
        self.microphone_text.set(default_microphone)
        self.microphone_choice = Combobox(self.lower_frame, width=40, values=microphones,
                                          textvariable=self.microphone_text, state='readonly', takefocus=False)
        self.microphone_choice.bind('<<ComboboxSelected>>', lambda _: self.select_microphone())

        self.top_window_status = IntVar()
        self.top_window_checkbutton = Checkbutton(self, text='Keep player on top', variable=self.top_window_status,
                                                  takefocus=False)
        if int(default_top):
            self.top_window_checkbutton.invoke()

        self.finish_button = Button(self, text='Finish', takefocus=False, command=self.finish)

        self.init_ui()

    def init_ui(self):
        self.upper_frame.pack(pady=20 * self.scale)

        self.host_label.grid(row=0, column=0, sticky='w', padx=10 * self.scale)
        self.host_input.grid(row=0, column=1, sticky='w')

        self.port_label.grid(row=1, column=0, sticky='w', padx=10 * self.scale)
        self.port_input.grid(row=1, column=1, sticky='w')

        self.username_label.grid(row=2, column=0, sticky='w', padx=10 * self.scale)
        self.username_input.grid(row=2, column=1, sticky='w')

        self.password_label.grid(row=3, column=0, sticky='w', padx=10 * self.scale)
        self.password_input.grid(row=3, column=1, sticky='w')

        self.mount_label.grid(row=4, column=0, sticky='w', padx=10 * self.scale)
        self.mount_input.grid(row=4, column=1, sticky='w')

        self.chunksize_label.grid(row=5, column=0, sticky='w', padx=10 * self.scale)
        self.chunksize_input.grid(row=5, column=1, sticky='w')

        self.name_label.grid(row=6, column=0, sticky='w', padx=10 * self.scale)
        self.name_input.grid(row=6, column=1, sticky='w')

        self.description_label.grid(row=7, column=0, sticky='w', padx=10 * self.scale)
        self.description_input.grid(row=7, column=1, sticky='w')

        self.genre_label.grid(row=8, column=0, sticky='w', padx=10 * self.scale)
        self.genre_input.grid(row=8, column=1, sticky='w')

        self.mid_frame.pack()

        self.idle_label.grid(row=0, column=0, sticky='w', padx=10 * self.scale)
        self.idle_input.grid(row=0, column=1)
        self.idle_selected.grid(row=0, column=2, sticky='w')

        self.lower_frame.pack(pady=20 * self.scale)

        self.speaker_label.grid(row=0, column=0, sticky='w')
        self.speaker_choice.grid(row=0, column=1)

        self.microphone_label.grid(row=1, column=0, sticky='w')
        self.microphone_choice.grid(row=1, column=1)

        self.top_window_checkbutton.pack(pady=10 * self.scale)

        self.finish_button.pack()

    def select_idle_file(self):
        filename = filedialog.askopenfilename(initialdir=f'{environ["HOME"]}/Downloads', title='Select File',
                                              filetypes=[('Audio', '*.mp3')])
        if filename:
            self.user_params['GENERAL']['idle'] = filename
            self.idle_selected_text.set(filename)

    def select_speaker(self):
        choice = self.speaker_choice.get()
        speaker_id_index = choice.rindex('ID: ') + 4
        speaker_id = choice[speaker_id_index:]
        self.user_params['SYSTEM']['speakername'] = choice
        self.user_params['SYSTEM']['speakerid'] = speaker_id
        self.speaker_choice.selection_clear()

    def select_microphone(self):
        choice = self.microphone_choice.get()
        microphone_id_index = choice.rindex('ID: ')
        microphone_id = choice[microphone_id_index + 4:]
        self.user_params['SYSTEM']['microphonename'] = choice
        self.user_params['SYSTEM']['microphoneid'] = microphone_id
        self.microphone_choice.selection_clear()

    def finish(self):
        # TODO check if user has completed every item or enable/disable features if not filled ex mic and speaker
        self.user_params['ICECAST']['host'] = self.host_input.get()
        self.user_params['ICECAST']['port'] = self.port_input.get()
        self.user_params['ICECAST']['username'] = self.username_input.get()
        self.user_params['ICECAST']['password'] = self.password_input.get()
        self.user_params['ICECAST']['mount'] = self.mount_input.get()
        self.user_params['ICECAST']['chunksize'] = self.chunksize_input.get()
        self.user_params['ICECAST']['name'] = self.name_input.get()
        self.user_params['ICECAST']['description'] = self.description_input.get()
        self.user_params['ICECAST']['genre'] = self.genre_input.get()
        self.user_params['SYSTEM']['scale'] = str(self.scale)
        self.user_params['SYSTEM']['xcenter'] = str(self.x_center)
        self.user_params['SYSTEM']['ycenter'] = str(self.y_center)
        self.user_params['SYSTEM']['toplevel'] = str(self.top_window_status.get())

        with open('config/conf.ini', 'w+') as config_file:
            self.user_params.write(config_file)
        self.destroy()
