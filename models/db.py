# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.login_next=URL('workbench')

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
# -------------------------------------------------------------------------
from datetime import datetime

db.define_table('category',
                Field('categories', 'string', requires=IS_NOT_EMPTY()))

# This table hold the data for each idea
db.define_table('idea',
                Field('title', 'string',
                      requires=IS_NOT_EMPTY()),

                Field('description', 'text',
                      requires=IS_NOT_EMPTY()),

                Field('documents', 'upload'),

                Field('active_idea', 'boolean',
                      default=True),

                Field('startdate', 'datetime',
                      default=lambda:datetime.now()),

                Field('enddate', 'datetime'),

                Field('category', 'reference category',
                      requires=IS_IN_DB(db, 'category.id', '%(categories)s')))

# This table holds the group information
db.define_table('idea_group',
                Field('user_id', 'reference auth_user',
                      default=auth.user_id,
                      writable=False,
                      readable=False,
                      requires=IS_NOT_EMPTY()),

                Field('idea_id', 'reference idea',
                      requires=IS_NOT_EMPTY()),

                Field('g_privileges', 'string',
                      length=1,
                      writable=False,
                      readable=False,
                      requires=IS_NOT_EMPTY()))

# This table holds the voting information
db.define_table('vote',
                Field('user_id', 'reference auth_user',
                      writable=False,
                      readable=False,
                      default=auth.user_id,
                      requires=IS_NOT_EMPTY()),

                Field('idea_id', 'reference idea',
                      requires=IS_NOT_EMPTY()),

                # A value of True represents a vote 'for'
                # A value of False represents a vote 'against'
                Field('vote', 'boolean',
                      writable=False,
                      readable=False,
                      requires=IS_NOT_EMPTY()))

# This table holds the post data for an idea
db.define_table('post',
                Field('user_id', 'reference auth_user',
                      default=auth.user_id,
                      requires=IS_NOT_EMPTY()),

                Field('idea_id', 'reference idea',
                      requires=IS_NOT_EMPTY()),

                Field('p_content', 'text'),

                Field('author'),

                Field('p_date', 'datetime',
                      default=lambda:datetime.now(),
                      requires=IS_NOT_EMPTY()))

# This table holds the user messages
db.define_table('user_message',
                Field('from_user', 'reference auth_user',
                      requires=IS_NOT_EMPTY(), default=auth.user_id),
                Field('to_user', 'reference auth_user',
                      requires=IS_NOT_EMPTY()),
                Field('the_message', 'text',
                      requires=IS_NOT_EMPTY()))

def get_author():
    author = 'none'
    if auth.user:
        author = auth.user.first_name  # set the name to who ever is loged in
    return author

db.post.idea_id.writable = db.post.idea_id.readable = False
db.post.user_id.writable = db.post.user_id.readable = False
db.post.p_date.writable = db.post.p_date.readable = False
db.post.author.default = get_author()
db.post.author.writable = False   # can't change the id
db.post.author.readable = False

# O = Owner, C=Contributor, F=Follower
db.idea_group.g_privileges.requires = IS_IN_SET(('O', 'C', 'F'))

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
