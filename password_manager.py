import sqlite3
import tkinter as tk
from tkinter import ttk
import configparser
from tables import create_db
import os

'''
TODO:
- separate db management and ui codes
- insert, update and delete records
- create generic connector
- review ui
'''


class User(object):
    def __init__(self, user_name, password):
        self.username = user_name
        self.password = password


class LoginFrame(tk.Frame):
    record_keys = ['media', 'login_name', 'password1', 'password2', 'remarks',]
    fake_record1 = ['facebook', 'test123', 'pw123', 'pw234', 'remarks']
    fake_record2 = ['twitter', 'test1234', 'pw123', 'pw234', 'remarks on twitter']
    root_user = User('root', 'root')

    def __init__(self, parent, db_name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.conn = connect_db(db_name)
        create_tables(self.conn)
        self._add_dummy()
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

        input1.bind("<KeyPress-Return>", lambda event: self.get_user_login(user_name, pw))
        input2.bind("<KeyPress-Return>", lambda event: self.get_user_login(user_name, pw))

        # btms
        btm_frame = tk.Frame(self)
        btm1 = tk.Button(btm_frame, text='Login', command=lambda: self.get_user_login(user_name, pw))
        btm1.grid(row=0, column=0)
        btm2 = tk.Button(btm_frame, text='QUIT', command=self.parent.quit)
        btm2.grid(row=0, column=1)
        btm_frame.grid(row=2, columnspan=2)
        self.place(relx=0.5, rely=0.5, anchor="center")

    def get_user_login(self, user_name, pw):
        user = User(user_name.get(), pw.get())
        check_user = get_user(user, self.conn)
        if check_user and check_user[0][1] == user.password:
            self.place_forget()
            main = MainApplication(self.parent, user=user, conn=self.conn)
        else:
            error_label = tk.Label(self, text="Invalid user name and password, please input again...")
            error_label.grid(row=4, columnspan=2)

    def _add_dummy(self):
        # add fake reocrds for testing
        user = User('shit', 'shit')
        add_user(user, self.conn)
        for _ in range(10):
            add_record(user, {k:v for k, v in zip(self.record_keys, self.fake_record1)}, self.conn)

        user = User('wow', 'wow')
        add_user(user, self.conn)
        for _ in range(5):
            add_record(user, {k:v for k, v in zip(self.record_keys, self.fake_record2)}, self.conn)


class MainApplication(tk.Frame):
    def __init__(self, parent, user, conn, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.user = user
        self.conn = conn
        self.parent = parent
        self.parent.geometry('800x400')
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
        records = get_record(self.user, self.conn)

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
        add_record(self.parent.user, record, self.parent.conn)
        self.cancel()

    def cancel(self):
        self.destroy()
        self.parent.display_records()
        self.parent.main_btm.grid(row=2)


def connect_db(db_name):
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except Exception as e:
        print(e)


def create_tables(conn):
    with conn:
        cur = conn.cursor()
        # user table
        cur.execute("""CREATE TABLE IF NOT EXISTS user (username text, password text)""")
        # create root user if not exist
        first_user = User('root', 'root')
        if not get_user(first_user, conn):
            add_user(first_user, conn)
        # data table
        cur.execute("""CREATE TABLE IF NOT EXISTS main
            (
            username text,
            media text,
            login_name text,
            password1 text,
            password2 text,
            remarks text
            )""")


def get_record(user, conn):
    with conn:
        cur = conn.cursor()
        cur.execute('''SELECT * FROM main WHERE username=:username''',
            {'username': user.username}
        )
        return cur.fetchall()


def add_record(user, record, conn):
    with conn:
        cur = conn.cursor()
        cur.execute("""INSERT INTO main VALUES
            (:username, :media, :login_name, :password1, :password2, :remarks)""",
            {
                'username': user.username,
                'media': record.get('media'),
                'login_name': record.get('login_name'),
                'password1': record.get('password1'),
                'password2': record.get('password2'),
                'remarks': record.get('remarks'),
            }
        )


def add_user(user, conn):
    with conn:
        cur = conn.cursor()
        cur.execute("""INSERT INTO user VALUES (:username, :password)""",
            {'username': user.username, 'password': user.password}
        )


def get_user(user, conn):
    with conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM user WHERE username=:username""",
            {'username': user.username}
        )
        return cur.fetchall()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    if config['sqlite']['db_name'] not in os.listdir():
        create_db('sqlite:///' + config['sqlite']['db_name'])

    root = tk.Tk()
    root.title('password manager')
    root.geometry(config['geometry']['screen_size'])
    # root['background'] = '#3E4149'
    t = LoginFrame(root)
    root.mainloop()
