# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    if request.args(0) == 'profile':
        # response.view = 'default/logedIn.html'
        # redirect(URL('logedIn'))
        redirect(URL('workbench'))
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def idea():
    return dict()


# ///////////////////////////////////////////////////////////////////////////
@auth.requires_login()
def logedIn():
    return dict()


# /////////////////////////////////////////////////////////////////////////

def showIdea():

    # Add the custom css file
    response.files.append(URL('static', 'css/showIdea.css'))

    # Get the idea from the db
    thePost = db.idea[request.args[0]]

    # Grab comments associated with the idea
    comments = db(db.post.idea_id == thePost.id).select()  # the comments that are associated with that idea

    upvotes = db((db.vote.idea_id == request.args[0]) & (db.vote.vote == 'T')).count()
    downvotes = db((db.vote.idea_id == request.args[0]) & (db.vote.vote == 'F')).count()

    return dict(thePost=thePost, comments=comments, upvotes=upvotes, downvotes=downvotes)

# ///////////////////////////////////////////////////////////////////////////

@auth.requires_login()
def createComment():
    post = db.idea[request.args(0)]
    print post
    db.post.idea_id.default = post.id
    form = SQLFORM(db.post,
                   showid=False,
                   deletable=True,
                   submit_button = 'Post your comment')
    if form.process().accepted:  # if the comment is valid
        redirect(URL('showIdea', args=post.id))
    elif form.errors:
       response.flash = 'please complete your post'
    else:
       response.flash = 'please edit your comment'
    return dict(form=form)

# ///////////////////////////////////////////////////////////////////////////
def ideasList():
    query = """SELECT DISTINCT q.idea_id AS ID, i.title AS Title, i.startdate AS Posted, i.active_idea AS Active,
            (SELECT COUNT(v.vote) FROM vote AS v WHERE v.vote = "T" AND v.idea_id = q.idea_id) as UpVote,
            (SELECT COUNT(v.vote) FROM vote AS v WHERE v.vote = "F" AND v.idea_id = q.idea_id) as DownVote
            FROM vote AS q
            INNER JOIN idea AS i
            ON q.idea_id=i.id;"""

    ideas = db.executesql(query, as_dict=True)

    return dict(ideas=ideas)

	


# ///////////////////////////////////////////////////////////////////////////
@auth.requires_login()
def create_idea():
    form = SQLFORM(db.idea)
    form.add_button('Cancel', URL('workbench'))
    form.process()
    if form.accepted:

        idea_id = form.vars.id
        db.idea_group.insert(g_privileges='O', idea_id=idea_id)
        db.vote.insert(user_id=auth.user_id, idea_id=idea_id, vote='True')

        response.view = 'default/index.html'
        response.flash = 'Idea Processed'
    elif form.errors:
        response.flash = 'Woops! Something is wrong.'
    else:
        response.flash = 'Start here to spread your idea world round.'
    return dict(form=form)


def about():
    return dict()


def test():
    ideas = db().select(db.idea.category).as_list()
    return dict(ideas=ideas)


def get_data():
    custdata = db.executesql(qry, as_dict=True)
    return response.json(custdata)



def showGroupMembers():
    post = db.post[request.args(0)]
    print 'post '
    print 'id '
    print id
    rows = db((db.idea_group.user_id == db.auth_user.id) &
              (db.idea_group.idea_id == post)).select(
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.email,
        db.idea_group.g_privileges,
        db.idea_group.idea_id
    )
    for row in rows:
        print rows

    return dict(rows=rows, id=id, post=post)


def exportIdeas():
    rows = db(db.idea).select()
    arr = []
    for row in rows:
        arr.append(int(row.category))
    return (arr)

@auth.requires_login()
def workbench():

    bg_url = 'background-image:url(' + str(URL('static', 'images/shark_bg.jpg')) + ')'

    response.files.append(URL('static', 'js/workbench.js'))
    response.files.append(URL('static', 'css/workbench.css'))

    my_tank_rows = db((db.idea_group.idea_id==db.idea.id) &
                (db.idea_group.user_id==auth.user_id) &
                (db.idea_group.g_privileges == 'O')).select(db.idea.title)
    my_contrib_rows = db((db.idea_group.idea_id == db.idea.id) &
                      (db.idea_group.user_id == auth.user_id) &
                      (db.idea_group.g_privileges == 'C')).select(db.idea.title)
    my_follow_rows = db((db.idea_group.idea_id == db.idea.id) &
                      (db.idea_group.user_id == auth.user_id) &
                      (db.idea_group.g_privileges == 'F')).select(db.idea.title)
    my_messages = db(db.user_message.to_user==auth.user_id).select()
    myIdeas = ''
    myFollows = ''
    myContribs = ''
    myMessages = ''

    for row in my_tank_rows:
        myIdeas += str(LI(row.title))
    for row in my_contrib_rows:
        myContribs += str(LI(row.title))
    for row in my_follow_rows:
        myFollows += str(LI(row.title))
    for row in my_messages:
        myMessages += str(LI(row.the_message)) + \
                      """<button class ="btn" id="allowContrib" onclick=" \
                          jQuery('#msgId').val('""" + str(row.id) + "'); \
                                jQuery('#from_user').val('" + str(row.about_idea_id) + "'); \
                                jQuery('#about_idea_id').val('" + str(row.from_user) + "'); " \
                                                                                       "ajax('" + URL('default',
                                                                                                      'allowContrib') + """', ['msgId', 'from_user', 'about_idea_id'], ':eval');" > Allow </button >"""

    return dict(myIdeas=myIdeas, myFollows=myFollows, myContribs=myContribs, myMessages=myMessages, bg_url=bg_url)

@auth.requires_login()
def editPost():
    post = db.post[request.args(0)]
    if not(post and post.user_id == auth.user_id):
        redirect(URL('showIdea'))
    form = SQLFORM(db.post, post,
                 labels= {'post_content': "Comment"},
                 showid= False,
                 deletable= True,
                 submit_button = 'Update your comment',
                  )
    form.add_button('Cancel', URL('showIdea', args=post.idea_id))

    if form.process(keepvalues=True).accepted:
       response.flash = 'comment updated'
       redirect(URL('showIdea', args=post.idea_id))
    elif form.errors:
       response.flash = 'please complete your post'
    else:
       response.flash = 'please edit your comment'
    return dict(form=form)

@auth.requires_login()
def myprofile():
    form=auth.profile()
    form.add_button('Cancel', URL('workbench'))
    return dict(form=form)


######## Ajax Functions ############
def follow():

    # Add the follow record to the db.
    db.idea_group.insert(user_id=auth.user_id, idea_id=request.vars.id, g_privileges='F')

    ret = """<button class ="btn" id="unfollow" onclick="jQuery('#id').val('""" + \
          request.vars.id + "');ajax('" + URL('default', 'unfollow') + \
          """', ['id'], 'foll');" > Unfollow </button >"""

    # Let the user know what is happening
    response.flash = 'You are now following ' + db.idea[request.vars.id].title + '!'

    return ret

def unfollow():

    # Delete the follow record from the database
    db((db.idea_group.user_id == auth.user_id) &
       (db.idea_group.idea_id == request.vars.id)).delete()

    ret = """<button class ="btn" id="follow" onclick="jQuery('#id').val('""" + \
          request.vars.id + "');ajax('" + URL('default', 'follow') + \
          """', ['id'], 'foll');" > Follow </button >"""

    # Let the user know what just happened
    response.flash = 'You are no longer following ' + db.idea[request.vars.id].title + '.'

    return ret

def contribRequest():

    # Grab the id of the owner of the idea
    idea_owner = db((db.idea_group.idea_id == 1) & (db.idea_group.g_privileges == 'O')).select().first().user_id

    # Create the message that will be sent to the owner
    the_message = auth.user.first_name + ' ' + auth.user.last_name + ' would like to contribute to ' + db.idea[
        request.vars.id].title
    ret = ''

    # Insert the message in to the database
    if db.user_message.insert(from_user=auth.user_id,
                              to_user=idea_owner,
                              about_idea_id=request.vars.id,
                              the_message=the_message):

        # Let the user know that the message was sent
        response.flash = "Message sent to the owner, we will alert you to their choice."

        ret = """<button class ="btn" id="stopcontrib" onclick="jQuery('#id').val('""" + \
              request.vars.id + "');ajax('" + URL('default', 'stop_contrib') + \
              """', ['id'], 'contrib');" >Stop Contributing</button >"""


    else:
        # If the else clause is reached, the database insert failed
        response.flash = "Something went wrong, please try again"

    return ret

def stop_contrib():

    if db((db.idea_group.user_id == auth.user_id) &
                  (db.idea_group.idea_id == request.vars.id) &
                  (db.idea_group.g_privileges == 'C')).delete():

        response.flash = "You are no longer contributing to " + db.idea[request.vars.id].title
    else:
        # If the else clause is reached, then that means that they had sent a request but it has not been responded to
        # delete the message from the system.

        # Grab the id of the owner of the idea
        idea_owner = db((db.idea_group.idea_id == 1) & (db.idea_group.g_privileges == 'O')).select().first().user_id

        # remove the record
        if db((db.user_message.from_user == auth.user_id) &
                      (db.user_message.to_user == idea_owner) &
                      (db.user_message.about_idea_id == request.vars.id)).delete():
            response.flash = "Your request for contribution has been rescinded."
        else:
            response.flash = "Something went wrong."

    return """<button class ="btn" id="contrib" onclick="jQuery('#id').val('""" + \
           request.vars.id + "');ajax('" + URL('default', 'contribRequest') + \
           """', ['id'], 'contrib');" > Request Contribute </button >"""


def upvote():

    if db.vote(user_id=auth.user_id, idea_id=request.vars.id, vote='T'):
        response.flash = "You have already voted for this idea!"
    else:
        if db.vote.insert(user_id=auth.user_id, idea_id=request.vars.id, vote='T'):
            response.flash = "Vote added"

    return ' (' + str(db((db.vote.idea_id == request.vars.id) & (db.vote.vote == 'T')).count()) + ')'

def downvote():

    if db.vote(user_id=auth.user_id, idea_id=request.vars.id, vote='F'):
        response.flash = "You have already voted against this idea!"
    else:
        if db.vote.insert(user_id=auth.user_id, idea_id=request.vars.id, vote='F'):
            response.flash = "Vote added"

    return ' (' + str(db((db.vote.idea_id == request.vars.id) & (db.vote.vote == 'F')).count()) + ')'


def allowContrib():

    ret = "alert('Contribution Allowed')"



    return ret


###### End Ajax Functions ##########
