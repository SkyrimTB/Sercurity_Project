'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, static_file, response

import model
import secrets

# -----------------------------------------------------------------------------
# Setup a secret key for cookies
global_secret = secrets.token_hex(16)


# -----------------------------------------------------------------------------
# Static file paths
# -----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')


# -----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')


# -----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    username = request.get_cookie("account", secret=global_secret)
    return model.index(username)


# -----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    username = request.get_cookie("account", secret=global_secret)
    return model.login_form(username)


# -----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')

    # Call the appropriate method
    return model.login_check(username, password, global_secret)


# -----------------------------------------------------------------------------

# Display the logout page
@get('/logout')
def get_logout_controller():
    '''
        get_llogout
        
        Serves the logout page
    '''

    # Get cookies
    username = request.get_cookie("account", secret=global_secret)

    return model.logout_form(username)


# -----------------------------------------------------------------------------

# Attempt the register
@post('/logout')
def post_logout():
    '''
        post_logout
        
        Handles logout
        Expects a form containing 'logout' fields
    '''

    # Get cookies
    username = request.get_cookie("account", secret=global_secret)

    # Call the appropriate method
    return model.logout_account(username, global_secret)


# -----------------------------------------------------------------------------

# Display the register page
@get('/register')
def get_register_controller():
    '''
        get_register
        
        Serves the register page
    '''
    return model.register_form()


# -----------------------------------------------------------------------------

# Attempt the register
@post('/register')
def post_register():
    '''
        post_register
        
        Handles register account
        Expects a form containing 'username', 'password', 'confirm_password' and '' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    confirem_password = request.forms.get('confirm_password')
    public_key = request.forms.get('user_public_key')

    # Call the appropriate method
    return model.register_account(username, password, confirem_password, public_key)


# -----------------------------------------------------------------------------

# Add a friend
@post('/friendlist')
def post_friendlist():
    '''
        post_friendlist
        
        Handles add friend to user's friendlist
        Expects a form containing 'add_friend', 'messages' fields
    '''

    # Get cookies
    username = request.get_cookie("account", secret=global_secret)

    # Handle the form processing
    friend_username = request.forms.get('add_friend')
    messages = request.forms.get('msg_encrypted')
    receiver = request.forms.get('receiver')

    # Call the appropriate method
    return model.friendlist_form(username, friend_username, messages, receiver)


# -----------------------------------------------------------------------------

# Display the Chat with friends page
@get('/friendlist')
def get_friendlist():
    '''
        get_friendlist
        
        Serves the friendlist page
    '''

    # Get cookies
    username = request.get_cookie("account", secret=global_secret)

    return model.friendlist_form(username, None, None, None)


# -----------------------------------------------------------------------------

# Display the forum page
@get('/forum')
def get_forum_controller():
    username = request.get_cookie("account", secret=global_secret)
    return model.forum_form(username)


@post('/forum')
def get_forum_controller():
    '''
        get_forum

        Serves the forum page
    '''

    username = request.get_cookie("account", secret=global_secret)
    title = request.forms.get('title')
    content = request.forms.get('content')
    section = request.forms.get('section')
    return model.add_post(username, title, content, section)


# -----------------------------------------------------------------------------

# Add a friend
@post('/forum')
def post_forum():
    '''
        post_forum
        
        Handles post forum
    '''

    # Get cookies
    username = request.get_cookie("account", secret=global_secret)

    # Handle the form processing
    post_message = request.forms.get('add_friend')

    # Call the appropriate method
    return model.forum_form(username)


# -----------------------------------------------------------------------------
# Display the post page
@get('/post')
def get_post_controller():
    '''
        get_forum

        Serves the forum page
    '''
    section = request.query.get('section')
    username = request.get_cookie("account", secret=global_secret)
    return model.post_page(username, section)


@get('/delete_post')
def delete_post():
    '''
        get_forum

        Serves the forum page
    '''
    username = request.get_cookie("account", secret=global_secret)
    post_id = request.query.get('post_id')

    return model.delete_post(username, post_id)


@get('/delete_comment')
def delete_delete_comment():
    '''
        get_forum

        Serves the forum page
    '''
    username = request.get_cookie("account", secret=global_secret)
    c_id = request.query.get('c_id')
    return model.delete_comment(username, c_id)


# -----------------------------------------------------------------------------
@post('/comments')
def add_comment_controller():
    '''
        add_comment
    '''
    username = request.get_cookie("account", secret=global_secret)
    post_id = request.forms.get('post_id')
    detail = request.forms.get('detail')
    return model.add_comment(username, detail, post_id)


# -----------------------------------------------------------------------------
@post('/update_profile')
def update_profile():
    '''
        add_comment
    '''
    username = request.get_cookie("account", secret=global_secret)
    password = request.forms.get('password',None)
    avatar = request.forms.get('avatar',None)
    return model.update_user(username, password, avatar)


# -----------------------------------------------------------------------------

@get('/profile')
def profile_page():
    username = request.get_cookie("account", secret=global_secret)
    return model.profile_page(username)


@get('/block')
def block_page():
    username = request.get_cookie("account", secret=global_secret)
    return model.block_page(username)


@get('/block_user')
def block_user():
    username = request.get_cookie("account", secret=global_secret)
    block_username = request.query.get('username')
    return model.block_user(username, block_username)


@get('/unblock_user')
def block_user():
    username = request.get_cookie("account", secret=global_secret)
    block_username = request.query.get('username')
    return model.unblock_user(username, block_username)


# -----------------------------------------------------------------------------
# Display the rescources page
@get('/rescources')
def get_rescources_controller():
    '''
        get_rescources
        
        Serves the rescources page
    '''

    # Get cookies
    username = request.get_cookie("account", secret=global_secret)

    return model.rescources_form(username)


# -----------------------------------------------------------------------------

@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()


# -----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)


# -----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error):
    return model.handle_errors(error)
