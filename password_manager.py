import sqlite3
import tkinter as tk
from tkinter import ttk
import configparser
from tables import create_db, login, load_record
import os

'''
TODO:
- separate db management and ui codes
- insert, update and delete records
- create generic connector
- review ui
'''


class LoginFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.login_window()

    # TODO: amend GUI creating func
    def login_window(self):
        # cells
        user_name = tk.StringVar()
        pw = tk.StringVar()

        label1 = tk.Label(self, text='User name: ')
        label1.grid(row=0, column=0, sticky="nsew")
        input1 = tk.Entry(self, width=20, textvariable=user_name)
        input1.grid(row=0, column=1, sticky='nsew')

        label2 = tk.Label(self, text='Password: ')
        label2.grid(row=1, column=0, sticky='nsew')
        input2 = tk.Entry(self, width=20, textvariable=pw)
        input2.grid(row=1, column=1, sticky='nsew')

        user = {'username': user_name.get(), 'password': pw.get()}
        input1.bind("<KeyPress-Return>", lambda event: self.check_login(user))
        input2.bind("<KeyPress-Return>", lambda event: self.check_login(user))

        # btms
        btm_frame = tk.Frame(self)
        btm1 = tk.Button(btm_frame, text='Login', command=lambda: self.check_login(user_name, pw))
        btm1.grid(row=0, column=0)
        btm2 = tk.Button(btm_frame, text='QUIT', command=self.parent.quit)
        btm2.grid(row=0, column=1)
        btm_frame.grid(row=2, columnspan=2)
        self.place(relx=0.5, rely=0.5, anchor="center")

    def check_login(self, user):
        check_user = login(user)
        if check_user is True:
            self.place_forget()
            main = MainApplication(self.parent, user=user)
        else:
            error_label = tk.Label(self, text="Invalid user name and password")
            error_label.grid(row=4, columnspan=2)


class MainApplication(tk.Frame):
    def __init__(self, parent, user, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.user = user
        self.parent = parent
        self.parent.geometry('{}x{}'.format(parent.winfo_width() * 2, parent.winfo_height()))
        self.main_window()

    def main_window(self):
        self.title = tk.Frame(self)
        welcome = tk.Label(self.title, text="Password Manager ver 0.5")
        welcome.pack()
        self.title.grid(row=0, sticky='n')

        self.display_records()

        self.main_btm = tk.Frame(self)
        new_rec = tk.Button(self.main_btm, text='New Record', command=self.to_add_page)
        new_rec.grid(row=0, column=0)
        btm2 = tk.Button(self.main_btm, text='QUIT', command=self.parent.quit)
        btm2.grid(row=0, column=1)
        self.main_btm.grid(row=2)
        self.place(relx=0.5, rely=0.5, anchor="center")

    def to_add_page(self):
        self.records_frame.grid_forget()
        self.main_btm.grid_forget()
        add_record = EditPage(self)

    def display_records(self):
        self.records_frame = tk.Frame(self)
        records = load_record(self.user)

        setting = {'login name': 120, 'password1': 120, 'password2': 120, 'remarks': 300}
        tree = ttk.Treeview(self.records_frame)
        tree['columns'] = list(setting.keys())

        # first column need special treatment
        tree.column('#0', width=100)
        tree.heading('#0', text='media')
        for key in tree['columns']:
            tree.column(key, width=setting[key])
            tree.heading(key, text=key)

        for i, rec in enumerate(records):
            tree.insert('', i, text=rec[1], values=rec[2:])
        tree.pack()
        self.records_frame.grid(row=1, sticky='nsew')


class EditPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.pack_frame()
        self.btm()
        self.grid(row=1, sticky='nsew')

    def pack_frame(self):
        keys = ['media', 'login_name', 'password1', 'password2', 'remarks']
        self.new_records = {k: tk.StringVar() for k in keys}

        for n, k in enumerate(keys):
            label1 = tk.Label(self, text=k.replace('_', ' ').capitalize() + ': ')
            label1.grid(row=n, column=0, sticky="nsew")
            entry = tk.Entry(self, width=20, textvariable=self.new_records[k])
            entry.grid(row=n, column=1, sticky='nsew')

    def btm(self):
        new_rec = tk.Button(self, text='Add', command=self.confirm)
        new_rec.grid(row=5, column=1)
        btm2 = tk.Button(self, text='Cancel', command=self.cancel)
        btm2.grid(row=5, column=0)

    def confirm(self):
        # print([x.get() for x in self.new_records.values()])
        record = {k: v.get() for k, v in self.new_records.items()}
        # add_record(self.parent.user, record, self.parent.conn)
        self.cancel()

    def cancel(self):
        self.destroy()
        self.parent.display_records()
        self.parent.main_btm.grid(row=2)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    if config['sqlite']['db_name'] not in os.listdir():
        create_db('sqlite:///' + config['sqlite']['db_name'])

    root = tk.Tk()
    root.title('password manager')

    geo = config['geometry']

    root.geometry('{}x{}'.format(geo['screen_width'], geo['screen_hight']))
    # root['background'] = '#3E4149'
    t = LoginFrame(root)
    root.mainloop()
