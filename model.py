'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import view
import random
import sql
import uuid
import hashlib

from bottle import response, redirect

# Initialise our views, all arguments are defaults for the template
page_view = view.View()


def is_admin(username):
    if not username:
        return False
    sql_db = sql.SQLDatabase()
    user_record = sql_db.get_user(username)
    return user_record[0][3] == 'YES'


# -----------------------------------------------------------------------------
# Index
# -----------------------------------------------------------------------------

def index(username):
    '''
        index
        Returns the view for the index
    '''
    return page_view("index", username=username)


# -----------------------------------------------------------------------------
# Register
# -----------------------------------------------------------------------------

def register_form():
    return page_view("register")


# -----------------------------------------------------------------------------

# Register a user account
def register_account(username, password, confirem_password, public_key):
    '''
        register_account
        Register a user account

        :: username :: The username
        :: password :: The password
        :: confirm password :: The confirm password that need to match

        Returns either a view for valid register, or a view for invalid register
    '''

    # Check if password is matches with confirem_password
    if password != confirem_password:
        return page_view("invalid", reason="Password and confirem_password is not Match")

    # Connect to the database
    sql_db = sql.SQLDatabase()
    # sql_db.database_setup()
    check_duplice = sql_db.check_username(username)

    if check_duplice:
        return page_view("invalid", reason="This Username is exist")
    else:
        # Store the password hashed by bcrypt with salt
        sql_db.add_user(username, password, 'NO')
        sql_db.add_pk(username, public_key)
        return page_view("valid", name="Register successed ! " + username)


# -----------------------------------------------------------------------------

def login_form(username):
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login", username=username)


# -----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password, global_secret):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    # By default assume good creds

    sql_db = sql.SQLDatabase()
    user_record = sql_db.get_user(username)

    if len(user_record) == 0:
        return page_view("invalid", reason='username does not exist.')

    # Do a attempts_check
    check_attempts = sql_db.attempts_check(username)

    if check_attempts == False:
        return page_view("invalid", reason="You try too many times, Please try again after 5 minutes")

    db_username, db_password = user_record[0][0], user_record[0][1]
    salt = user_record[0][2]

    password_salt = salt + password
    password_hash = hashlib.sha256(password_salt.encode()).hexdigest()

    if username != db_username:  # Wrong Username
        return page_view("invalid", reason="Incorrect Username")

    login = sql_db.check_credentials(username, password_hash)

    if login == False:  # Wrong password or too many attempts
        return page_view("invalid", reason="Incorrect Password")

    # Setup a cookies when login in
    response.set_cookie("account", username, secret=global_secret)

    return friendlist_form(username, None, None, None)


# -----------------------------------------------------------------------------

def logout_form(username):
    '''
        login_form
        Returns the view for the login_form
    '''
    # Check if the user is not login
    if username == None:
        return page_view("invalid", reason="Please Login first")

    return page_view("logout")


def logout_account(username, global_secret):
    # Expires the cookies
    response.set_cookie("account", username, expires=0, secret=global_secret)

    return page_view("login")


# -----------------------------------------------------------------------------
# Friends list page with chat functions
# -----------------------------------------------------------------------------

def friendlist_form(username, friend_username, message, receiver):
    '''
        about
        Returns the view for the about page
    '''
    # Check if the user is not login
    if username == None:
        return page_view("invalid", reason="Please Login first")

    # Connect to the database
    sql_db = sql.SQLDatabase()

    error_msg = ""

    # Add friend_username
    if friend_username != None and message != None:
        error_msg = "Please given a input once at time ! You can't adding the friend and also sending a message"
    else:

        if friend_username != None:

            if username == friend_username:
                error_msg = "You can't input your username!"
            else:

                # Check if the user is already be the friend of the giving username
                if sql_db.check_friendlist(username, friend_username) != None:
                    error_msg = "You are already friends with the giving username!"
                else:
                    add_state = sql_db.add_friend(username, friend_username)

                    if add_state:
                        error_msg = "Successed add friend!"
                    else:
                        error_msg = "The friend is not found!"
        elif message != None:

            # Add message to the database
            sql_db.add_messages(username, receiver, message)
            error_msg = "Message sent!"

    # Get friend list
    friendlists = []
    lists = sql_db.get_friendlist(username)

    # Get public key for current user
    public_key_current_user = sql_db.get_pk(username)

    # Add friends to the list
    if lists != None:
        for data in lists:

            if data[1] == username:
                public_key = sql_db.get_pk(data[2])
                public_key_current_user = sql_db.get_pk(data[1])

                # check receiver
                if data[2] == receiver:
                    friendlists.append([data[2], public_key[0][0], 1, public_key_current_user[0][0]])
                else:
                    friendlists.append([data[2], public_key[0][0], 0, public_key_current_user[0][0]])
            elif data[2] == username:
                public_key = sql_db.get_pk(data[1])

                # check receiver
                if data[1] == receiver:
                    friendlists.append([data[1], public_key[0][0], 1, public_key_current_user[0][0]])
                else:
                    friendlists.append([data[1], public_key[0][0], 0, public_key_current_user[0][0]])

    # Setup friend number msg
    firends_num = ""

    if len(friendlists) < 2:
        firends_num += str(len(friendlists)) + " friend!"
    else:
        firends_num += str(len(friendlists)) + " friends!"

    # Get messagelist
    messagelists = []

    temp_msg = sql_db.get_messages(username, receiver)

    if temp_msg != None:
        for msg in temp_msg:
            messagelists.append([msg[3], msg[1]])

    return page_view("friendlist", name=username, friend_num=firends_num, friendlists=friendlists,
                     messages=messagelists, error_msg=error_msg)


# -----------------------------------------------------------------------------

def forum_form(username):
    '''
        forum_form
        Returns the view for the forum_form
    '''
    # Check if the user is not login
    if not username:
        return page_view("invalid", reason="Please Login first")
    sql_db = sql.SQLDatabase()
    block = sql_db.is_block(username)
    return page_view("forum", is_admin=is_admin(username), block=block, username=username)


def add_post(username, title, content, section):
    sql_db = sql.SQLDatabase()
    sql_db.add_post(title, content, username, section)
    return page_view("postlist")


# -----------------------------------------------------------------------------
def post_page(username, section=None):
    sql_db = sql.SQLDatabase()
    if section:
        posts = sql_db.get_post_by_section(section)
    else:
        posts = sql_db.get_post_list()
    admin = is_admin(username)
    block = sql_db.is_block(username)
    posts = [list(p) for p in posts]
    for p in posts:
        sender = sql_db.get_user(p[4])[0]
        p[4] = sender
        p.append(admin or sender[0] == username)
        comments = sql_db.get_comments(p[0])
        comments = [list(c) for c in comments]
        for c in comments:
            c.append(p.append(admin or c[3] == username))
        p.append(comments)
    return page_view("postlist", is_admin=is_admin(username), posts=posts, username=username, block=block)


def delete_post(username, post_id):
    sql_db = sql.SQLDatabase()
    sql_db.delete_post(post_id)
    print(post_id)
    return redirect('/post')


def delete_comment(username, c_id):
    sql_db = sql.SQLDatabase()
    sql_db.delete_comment(c_id)
    return redirect('/post')


# -----------------------------------------------------------------------------
def add_comment(username, detail, post_id):
    sql_db = sql.SQLDatabase()
    sql_db.add_comment(username, post_id, detail)
    return redirect('/post')


# -----------------------------------------------------------------------------
def profile_page(username):
    sql_db = sql.SQLDatabase()
    if not username:
        return page_view("invalid", reason="Please Login first")
    admin = is_admin(username)
    user = sql_db.get_user(username)[0]
    return page_view("profile", admin=admin, user=user)


# -----------------------------------------------------------------------------
def block_page(username):
    # if not username:
    #     return page_view("invalid", reason="Please Login first")
    admin = is_admin(username)
    sql_db = sql.SQLDatabase()
    user_list = sql_db.get_user_list()
    return page_view("block", user_list=user_list, admin=admin)


# -----------------------------------------------------------------------------
def block_user(username, block_username):
    # if not username:
    #     return page_view("invalid", reason="Please Login first")
    admin = is_admin(username)
    sql_db = sql.SQLDatabase()
    user_list = sql_db.block_user(block_username, 'YES')
    return redirect('/block')


# -----------------------------------------------------------------------------
def unblock_user(username, block_username):
    # if not username:
    #     return page_view("invalid", reason="Please Login first")
    admin = is_admin(username)
    sql_db = sql.SQLDatabase()
    user_list = sql_db.block_user(block_username, 'NO')
    return redirect('/block')


# -----------------------------------------------------------------------------
def update_user(username, password, avatar):
    sql_db = sql.SQLDatabase()
    if password:
        print("update password")
        sql_db.update_password(username, password)
    if avatar:
        print("update avatar")
        sql_db.update_avatar(username, avatar)
    return redirect('/profile')


# -----------------------------------------------------------------------------

def rescources_form(username):
    '''
        rescources_form
        Returns the view for the rescources_form
    '''

    # Check if the user is not login
    if username == None:
        return page_view("invalid", reason="Please Login first")

    return page_view("rescources")


# -----------------------------------------------------------------------------
# About
# -----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())


# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.",
              "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
              "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
              "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
              "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
              "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


# -----------------------------------------------------------------------------
# Debug
# -----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


# -----------------------------------------------------------------------------
# 404
# Custom 404 error page
# -----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)
