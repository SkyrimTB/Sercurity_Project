import sqlite3
import uuid
import hashlib
import bcrypt
from datetime import datetime
import time


# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self):
        self.conn = sqlite3.connect("database.db", uri=True)
        self.cur = self.conn.cursor()

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    # -----------------------------------------------------------------------------

    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin'):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.execute("DROP TABLE IF EXISTS Friends")
        self.execute("DROP TABLE IF EXISTS Messages")
        self.execute("DROP TABLE IF EXISTS Posts")
        self.execute("DROP TABLE IF EXISTS Comments")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            username TEXT UNIQUE,
            password TEXT,
            salt TEXT,
            admin TEXT DEFAULT 'NO',
            attempts INTEGER DEFAULT 0,
            block_time DATETIME DEFAULT NULL,
            public_key TEXT DEFAULT NULL,
            mute TEXT DEFAULT 'NO',
              avatar TEXT,
            block TEXT
            
        )""")

        # Create the Firends table
        self.execute("""CREATE TABLE Friends(
            Id INTEGER PRIMARY KEY,
            username TEXT,
            friend TEXT
        )""")

        # Create the Messages table to store encrypted messages
        self.execute("""CREATE TABLE Messages(
            Id INTEGER PRIMARY KEY,
            sender_username TEXT,
            receiver_username TEXT,
            encrypted_messagge TEXT
        )""")
        # Create the post table
        self.execute("""CREATE TABLE Posts(
                 Id INTEGER PRIMARY KEY,
                 title TEXT,
                 content TEXT,
                 section TEXT,
                 sender_username TEXT,
                 add_time datetime
             )""")

        # Create the comment table
        self.execute("""CREATE TABLE Comments(
                 Id INTEGER PRIMARY KEY,
                 post_id INTEGER,
                 detail TEXT,
                 sender_username TEXT,
                 add_time datetime
             )""")

        self.commit()

        # Add our admin user
        self.add_user('admin', admin_password, admin='YES')
        self.add_user('root', '321.qwer', admin='NO')
        self.add_post("what's your name? ",
                      'Welcome to USPS.com. Find information on our most convenient and affordable shipping and mailing services. Use our quick tools to find locations, ...',
                      'root', 'general')

    # -----------------------------------------------------------------------------
    # User handling
    # -----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, password, admin):
        sql_cmd = """
                INSERT INTO Users(username, password, salt, admin,block,avatar)
                VALUES('{username}', '{password}', '{salt}', '{admin}','NO','/img/avatar.png')
           """

        # Generate a random number as salt.
        salt = uuid.uuid4().hex

        password_salt = salt + password
        password_hash = hashlib.sha256(password_salt.encode()).hexdigest()

        # Hash the password
        password_double_encrypted = bcrypt.hashpw(password_hash.encode('ascii'), bcrypt.gensalt()).hex()

        sql_cmd = sql_cmd.format(username=username, password=password_double_encrypted, salt=salt, admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    # Add a public key to a user
    def add_pk(self, username, public_key):

        # Update the public key
        sql_query = """
            UPDATE Users
            SET public_key = '{public_key}'
            WHERE username = '{username}'
        """

        sql_cmd = sql_query.format(public_key=public_key, username=username)

        self.execute(sql_cmd)
        self.commit()
        return True

    # Get a public key for a user
    def get_pk(self, username):

        # Update the public key
        sql_query = """
                SELECT public_key
                FROM Users
                WHERE username = '{username}'
            """

        sql_cmd = sql_query.format(username=username)

        self.execute(sql_cmd)
        return self.cur.fetchall()

    # -----------------------------------------------------------------------------

    def get_user(self, username):
        sql_query = """
                SELECT * 
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        self.commit()

        return self.cur.fetchall()

    def debug(self):
        sql_query = """
                SELECT * 
                FROM Users
            """

        self.execute(sql_query)
        self.commit()

        return self.cur.fetchall()

    def debug_friend(self):
        sql_query = """
                SELECT * 
                FROM Friends
            """

        self.execute(sql_query)
        self.commit()

        return self.cur.fetchall()

    def debug_message(self):
        sql_query = """
                SELECT * 
                FROM Messages
            """

        self.execute(sql_query)
        self.commit()

        return self.cur.fetchall()

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT *
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.execute(sql_query)

        # Get the return result
        result = self.cur.fetchone()

        # Check if the hash is same
        if bcrypt.checkpw(password.encode('ascii'), bytes.fromhex(result[1])):

            # Update the attempts to zero
            sql_query = """
                UPDATE Users
                SET attempts = 0, block_time = NULL
                WHERE username = '{username}'
            """

            sql_query = sql_query.format(username=username)
            self.execute(sql_query)
            self.commit()

            return True
        else:

            attempts = int(result[4]) + 1

            # Update Attempts
            # Update the attempts to zero
            sql_query = """
                UPDATE Users
                SET attempts = '{attempts}'
                WHERE username = '{username}'
            """

            sql_query = sql_query.format(username=username, attempts=attempts)
            self.execute(sql_query)
            self.commit()

            # Do a attempts_check
            self.attempts_check(username)

            return False

    # -----------------------------------------------------------------------------

    # Check if the username is exist
    def check_username(self, username):
        sql_query = """
                SELECT *
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)

        self.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        else:
            return False

    # -----------------------------------------------------------------------------

    # Check user attempts to defense Brute Force Attack
    def attempts_check(self, username):
        sql_query = """
                SELECT *
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.execute(sql_query)

        # Get the return result
        result = self.cur.fetchone()

        attempts = result[4]
        block_time = result[5]

        # Form the data that the account is block
        format_data = "%Y-%m-%d %H:%M:%S"

        # If the account is block, cooldown for 5 minutes
        if block_time != None:

            block_time = datetime.strptime(block_time, format_data)

            # Check if pass the 5 minutes cooldown
            different = datetime.utcnow() - block_time
            different = different.total_seconds() / 60

            if different >= 5:
                return True
            else:
                return False

        # IF the password gets wrong three times, block the account
        if attempts == 3:
            current_time = datetime.utcnow().strftime(format_data)

            # Update the block time
            sql_query = """
                UPDATE Users
                SET attempts = 0, block_time = '{block_time}'
                WHERE username = '{username}'
            """

            sql_query = sql_query.format(block_time=current_time, username=username)
            self.execute(sql_query)
            self.commit()

            return False

        return True

    # -----------------------------------------------------------------------------

    # Add a friend to a user
    def add_friend(self, username, friend):

        # Check if the friend usernmae is exist
        if len(self.get_user(friend)) == 0:
            return False

        sql_cmd = """
                INSERT INTO Friends(username, friend)
                VALUES('{username}', '{friend}')
           """

        sql_cmd = sql_cmd.format(username=username, friend=friend)

        self.execute(sql_cmd)
        self.commit()

        return True

    # -----------------------------------------------------------------------------

    # Get a user friends list
    def get_friendlist(self, username):

        sql_query = """
                SELECT * 
                FROM Friends
                WHERE username='{username}' or friend='{username}'
            """

        sql_cmd = sql_query.format(username=username)
        self.execute(sql_cmd)

        return self.cur.fetchall()

    # -----------------------------------------------------------------------------

    # Check if two user is friends
    def check_friendlist(self, username, friend_username):

        sql_query = """
                SELECT *
                FROM Friends
                WHERE (username = '{username}' and friend = '{friend_username}') or (username = '{friend_username}' and friend = '{username}')
            """

        sql_cmd = sql_query.format(username=username, friend_username=friend_username)
        self.execute(sql_cmd)

        return self.cur.fetchone()

    # -----------------------------------------------------------------------------

    # Add encrypted message to the database
    def add_messages(self, sender_username, receiver_username, encrypted_messagge):

        sql_query = """
                INSERT INTO Messages(sender_username, receiver_username, encrypted_messagge)
                VALUES('{sender_username}', '{receiver_username}', '{encrypted_messagge}')
           """

        sql_cmd = sql_query.format(sender_username=sender_username, receiver_username=receiver_username,
                                   encrypted_messagge=encrypted_messagge)
        self.execute(sql_cmd)
        self.commit()

        return True

    # -----------------------------------------------------------------------------

    # Get encrypted message to the database between two user
    def get_messages(self, username, friend_username):

        sql_query = """
                SELECT *
                FROM Messages
                WHERE (sender_username = '{username}' and receiver_username = '{friend_username}') or (sender_username = '{friend_username}' and receiver_username = '{username}')
            """

        sql_cmd = sql_query.format(username=username, friend_username=friend_username)
        self.execute(sql_cmd)

        return self.cur.fetchall()

    # -----------------------------------------------------------------------------
    def add_post(self, title, content, sender_username, section):
        add_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql_query = f'insert into Posts(title,content,sender_username,section,add_time) values' \
                    f'("{title}","{content}","{sender_username}","{section}","{add_time}") '
        self.execute(sql_query)
        self.commit()
        return self.cur.lastrowid

    def delete_post(self, Id):
        sql_cmd = f"delete from Posts where Id={Id}"
        self.execute(sql_cmd)
        self.commit()
        return True

    def get_post_list(self):
        sql_cmd = "select * from Posts"
        self.execute(sql_cmd)
        return self.cur.fetchall()

    def get_post_by_section(self, section):
        sql_cmd = f"select * from Posts where section='{section}'"
        self.execute(sql_cmd)
        return self.cur.fetchall()

    def add_comment(self, sender_username, post_id, detail):
        add_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql_query = f'insert into Comments(post_id,sender_username,detail,add_time) values' \
                    f'("{post_id}","{sender_username}","{detail}","{add_time}") '
        self.execute(sql_query)
        self.commit()
        return self.cur.lastrowid

    def delete_comment(self, comment_id):
        sql_cmd = f"delete from Comments where Id={comment_id}"
        self.execute(sql_cmd)
        self.commit()
        return True

    def get_comments(self, post_id):
        sql_cmd = f"select * from Comments where post_id={post_id}"
        self.execute(sql_cmd)
        return self.cur.fetchall()

    def get_user_list(self):
        sql_cmd = f"select username,avatar,block from Users"
        self.execute(sql_cmd)
        return self.cur.fetchall()

    def block_user(self, username, block='YES'):
        sql_cmd = f"update Users set block='{block}' where username='{username}'"
        self.execute(sql_cmd)
        self.commit()
        return True

    def update_password(self, username, password):
        salt = uuid.uuid4().hex
        password_salt = salt + password
        password_hash = hashlib.sha256(password_salt.encode()).hexdigest()
        password_double_encrypted = bcrypt.hashpw(password_hash.encode('ascii'), bcrypt.gensalt()).hex()
        sql_cmd = f"update Users set password='{password_double_encrypted}',salt='{salt}' where username='{username}'"
        self.execute(sql_cmd)
        self.commit()
        return True

    def update_avatar(self, username, avatar):
        sql_cmd = f"update Users set avatar='{avatar}' where username='{username}'"
        self.cur.execute(sql_cmd)
        self.commit()
        return True

    def is_block(self, username):
        sql_cmd = f"select block from Users where username='{username}'"
        self.execute(sql_cmd)
        data = self.cur.fetchall()
        if not data:
            return True
        else:
            return data[0][-1] == "YES"

# sql = SQLDatabase()
# sql.database_setup()
# sql.add_post('1', '1', '1', '1')
# row_id = sql.add_post('1', '1', '1', '1')
# sql.delete_post(row_id)
# print(sql.get_post_list())
