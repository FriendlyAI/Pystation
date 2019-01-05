from configparser import ConfigParser
from os import environ
from platform import system
from tkinter import Tk, filedialog, StringVar, Message, Text
from tkinter.ttk import Button, Entry, Label, Progressbar, Treeview, Scrollbar, Frame, Style, Combobox
from soundcard import all_microphones


class ConfigWindow(Tk):
    def __init__(self):
        super(ConfigWindow, self).__init__()

        self.user_params = ConfigParser()
        self.user_params.read('config/conf.ini')

        self.scale = 1
        if system() == 'Linux':
            self.scale = 2

        self.user_params['SYSTEM']['Scale'] = str(self.scale)

        self.width = 600 * self.scale
        self.height = 500 * self.scale

        x_center = int(self.winfo_screenwidth() / 2 - self.width / 2)
        y_center = int(self.winfo_screenheight() / 2 - self.height / 2)

        self.user_params['SYSTEM']['XCenter'] = str(x_center)
        self.user_params['SYSTEM']['YCenter'] = str(y_center)

        self.geometry('%dx%d+%d+%d' % (self.width, self.height, x_center, y_center))
        self.title('Setup Pystation')
        self.protocol('WM_DELETE_WINDOW', self.finish)
        self.configure(background='gray92')

        '''
        id for speaker
        id for mic
        idle track
        Host
        Port
        Username
        Password
        Mount
        Chunksize
        Name
        Description
        Genre
        '''
        '''
        self.label_frame = Frame(self, width=200)
        self.input_frame = Frame(self, width=200)
        self.info_frame = Frame(self, width=200)

        self.host_label = Label(self.label_frame, text='Host')
        self.host_input = Entry(self.input_frame, width=20, font='Menlo')

        self.port_label = Label(self.label_frame, text='Port')
        self.port_input = Entry(self.input_frame, width=5, font='Menlo')

        self.username_label = Label(self.label_frame, text='Username')
        self.username_input = Entry(self.input_frame, width=20, font='Menlo')

        self.password_label = Label(self.label_frame, text='Password')
        self.password_input = Entry(self.input_frame, width=20, font='Menlo', show='*')

        self.mount_label = Label(self.label_frame, text='Mount')
        self.mount_input = Entry(self.input_frame, width=20, font='Menlo')

        self.chunksize_label = Label(self.label_frame, text='Chunk size')
        self.chunksize_input = Entry(self.input_frame, width=5, font='Menlo')

        self.name_label = Label(self.label_frame, text='Stream name')
        self.name_input = Entry(self.input_frame, width=20, font='Menlo')

        self.description_label = Label(self.label_frame, text='Description')
        self.description_input = Entry(self.input_frame, width=20, font='Menlo')

        self.genre_label = Label(self.label_frame, text='Genre')
        self.genre_input = Entry(self.input_frame, width=20, font='Menlo')

        self.idle_label = Label(self.label_frame, text='Idle track')
        self.idle_input = Button(self.input_frame, width=20)
        self.idle_selected = Label(self.info_frame, text=self.user_params.get('GENERAL', 'Idle'))
        '''

        self.upper_frame = Frame(self)

        self.host_label = Label(self.upper_frame, text='Host')
        self.host_input = Entry(self.upper_frame, width=20, font='Menlo')

        self.port_label = Label(self.upper_frame, text='Port')
        self.port_input = Entry(self.upper_frame, width=5, font='Menlo')

        self.username_label = Label(self.upper_frame, text='Username')
        self.username_input = Entry(self.upper_frame, width=20, font='Menlo')

        self.password_label = Label(self.upper_frame, text='Password')
        self.password_input = Entry(self.upper_frame, width=20, font='Menlo', show='*')

        self.mount_label = Label(self.upper_frame, text='Mount')
        self.mount_input = Entry(self.upper_frame, width=20, font='Menlo')

        self.chunksize_label = Label(self.upper_frame, text='Chunk size')
        self.chunksize_input = Entry(self.upper_frame, width=5, font='Menlo')

        self.name_label = Label(self.upper_frame, text='Stream name')
        self.name_input = Entry(self.upper_frame, width=20, font='Menlo')

        self.description_label = Label(self.upper_frame, text='Description')
        self.description_input = Entry(self.upper_frame, width=20, font='Menlo')

        self.genre_label = Label(self.upper_frame, text='Genre')
        self.genre_input = Entry(self.upper_frame, width=20, font='Menlo')

        self.idle_label = Label(self.upper_frame, text='Idle track')
        self.idle_input = Button(self.upper_frame, text='Choose idle track', command=self.select_idle_file)
        self.idle_selected_text = StringVar()
        self.idle_selected_text.set(self.user_params.get('GENERAL', 'Idle'))
        self.idle_selected = Message(self.upper_frame, width=300 * self.scale, background='gray92',
                                     textvariable=self.idle_selected_text, takefocus=False)

        speakers = [f'{repr(speaker)} ID: {speaker.id}' for speaker in all_microphones(include_loopback=True)]

        default_speaker = self.user_params.get('SYSTEM', 'speakername')
        self.speaker_text = StringVar()
        self.speaker_text.set(default_speaker)
        self.speaker_choice = Combobox(self, width=40, values=speakers, textvariable=self.speaker_text,
                                       state='readonly', takefocus=False)
        self.speaker_choice.bind('<<ComboboxSelected>>', lambda _: self.select_speaker())

        microphones = all_microphones(include_loopback=False)

        default_microphone = self.user_params.get('SYSTEM', 'microphonename')
        self.microphone_text = StringVar()
        self.microphone_text.set(default_microphone)
        self.microphone_choice = Combobox(self, width=40, values=microphones, textvariable=self.microphone_text,
                                          state='readonly', takefocus=False)
        self.microphone_choice.bind('<<ComboboxSelected>>', lambda _: self.select_microphone())

        self.finish_button = Button(self, text='Finish', takefocus=False, command=self.finish)

        self.init_ui()

    def init_ui(self):
        # self.label_frame.pack(side='left')
        # self.input_frame.pack(side='left')
        # self.info_frame.pack(side='left')
        self.upper_frame.pack()

        self.host_label.grid(row=0, column=0, sticky='w', padx=10)
        self.host_input.grid(row=0, column=1, sticky='w')

        self.port_label.grid(row=1, column=0, sticky='w', padx=10)
        self.port_input.grid(row=1, column=1, sticky='w')

        self.username_label.grid(row=2, column=0, sticky='w', padx=10)
        self.username_input.grid(row=2, column=1, sticky='w')

        self.password_label.grid(row=3, column=0, sticky='w', padx=10)
        self.password_input.grid(row=3, column=1, sticky='w')

        self.mount_label.grid(row=4, column=0, sticky='w', padx=10)
        self.mount_input.grid(row=4, column=1, sticky='w')

        self.chunksize_label.grid(row=5, column=0, sticky='w', padx=10)
        self.chunksize_input.grid(row=5, column=1, sticky='w')

        self.name_label.grid(row=6, column=0, sticky='w', padx=10)
        self.name_input.grid(row=6, column=1, sticky='w')

        self.description_label.grid(row=7, column=0, sticky='w', padx=10)
        self.description_input.grid(row=7, column=1, sticky='w')

        self.genre_label.grid(row=8, column=0, sticky='w', padx=10)
        self.genre_input.grid(row=8, column=1, sticky='w')

        self.idle_label.grid(row=9, column=0, sticky='w', padx=10)
        self.idle_input.grid(row=9, column=1)
        self.idle_selected.grid(row=9, column=2, sticky='w')

        self.speaker_choice.pack()

        self.microphone_choice.pack()

        self.finish_button.place(x=self.width - 100 * self.scale, y=self.height - 50 * self.scale)

    def select_idle_file(self):
        filename = filedialog.askopenfilename(initialdir=f'{environ["HOME"]}/Downloads', title='Select File',
                                              filetypes=[('Audio', '*.mp3')])
        self.user_params['GENERAL']['idle'] = filename
        self.idle_selected_text.set(filename)

    def select_speaker(self):
        choice = self.speaker_choice.get()
        speaker_id_index = choice.rindex(' ID: ')
        speaker_id = choice[speaker_id_index + 5:]
        self.user_params['SYSTEM']['speakername'] = choice[:speaker_id_index]
        self.user_params['SYSTEM']['speakerid'] = speaker_id
        self.speaker_choice.selection_clear()

    def select_microphone(self):
        choice = self.microphone_choice.get()
        microphone_id_index = choice.rindex(' ID: ')
        microphone_id = choice[microphone_id_index + 5:]
        self.user_params['SYSTEM']['microphonename'] = choice[:microphone_id_index]
        self.user_params['SYSTEM']['microphoneid'] = microphone_id
        self.microphone_choice.selection_clear()

    def finish(self):
        with open('config/conf.ini', 'w+') as config_file:
            self.user_params.write(config_file)
        self.destroy()
