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
    thePost = db.idea(request.args(0, cast=int))  # this is the idea
    db.post.idea_id.default = thePost.id  # set the idea id of the comments to the post id
    #form = SQLFORM(db.post)  # this is the form for filling out a comment
    #if form.process().accepted:  # if the comment is valid
        #response.flash = 'your comment is posted'
    comments = db(db.post.idea_id == thePost.id).select()  # the comments that are associated with that idea

    row = db((db.vote.user_id == auth.user.id) & (db.vote.idea_id == request.args[0])).select(db.vote.vote)

    return dict(thePost=thePost, comments=comments, row=row)

# ///////////////////////////////////////////////////////////////////////////

def createComment():
    post = db.idea[request.args(0)]
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
    query = """SELECT q.idea_id AS ID, i.title AS Title, i.startdate AS Posted, i.active_idea AS Active,
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

        # The following lines MUST be included when processing an idea in to the database.
        # These lines generate the group associated with the idea, adds the creator of the idea
        # as the owner, and dumps it in to the db.

        try_by_user_groups = db(db.idea_group.user_id == auth.user_id).select(
            db.idea_group.idea_id.max())[0][db.idea_group.idea_id.max()]

        failsafe = db().select(db.idea_group.idea_id.max())[0][db.idea_group.idea_id.max()]

        if try_by_user_groups:
            idea_id = int(try_by_user_groups) + 1
        elif failsafe:
            idea_id = int(failsafe) + 1
        else:
            idea_id = 1

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

    #sumUpVote = db().select(db.vote.vote=='True').sum()
    #sumDownVote = db().select(db.vote.vote=='False').sum()

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
    myIdeas = ''
    myFollows = ''
    myContribs = ''
    for row in my_tank_rows:
        myIdeas += str(LI(row.title))
    for row in my_contrib_rows:
        myFollows += str(LI(row.title))
    for row in my_follow_rows:
        myContribs += str(LI(row.title))
    return dict(myIdeas=myIdeas, myFollows=myFollows, myContribs=myContribs,bg_url=bg_url)

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
