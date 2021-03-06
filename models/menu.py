# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------

response.logo = A(IMG(_src=URL('static', 'images/white_shark.png'),
                  _href=URL('default', 'index')))
response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

if auth.user_id:
    response.menu = [
        (T('Intro'), False, URL('default', 'index'), []),
        (T('Workbench'), False, URL('default', 'workbench'), []),
        (T('Pitch Idea'), False, URL('default', 'create_idea'), []),
        (T('Idea Tank'), False, URL('default', 'ideasList'), []),
        (T('Edit Profile'), False, URL('default', 'myprofile'), [])
    ]
else:
    response.menu = [
        (T('Intro'), False, URL('default', 'index'), []),
        (T('Idea Tank'), False, URL('default', 'ideasList'), [])
    ]

DEVELOPMENT_MENU = True


# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. remove in production
# ----------------------------------------------------------------------------------------------------------------------

def _():
    # ------------------------------------------------------------------------------------------------------------------
    # shortcuts
    # ------------------------------------------------------------------------------------------------------------------
    app = request.application
    ctr = request.controller
    # ------------------------------------------------------------------------------------------------------------------
    # useful links to internal and external resources
    # ------------------------------------------------------------------------------------------------------------------
    # response.menu += [
    #     (T('My Sites'), False, URL('admin', 'default', 'site')),
    #     (T('This App'), False, '#', [
    #         (T('Design'), False, URL('admin', 'default', 'design/%s' % app)),
    #         LI(_class="divider"),
    #         (T('Controller'), False,
    #          URL(
    #              'admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
    #         (T('View'), False,
    #          URL(
    #              'admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
    #         (T('DB Model'), False,
    #          URL(
    #              'admin', 'default', 'edit/%s/models/db.py' % app)),
    #         (T('Menu Model'), False,
    #          URL(
    #              'admin', 'default', 'edit/%s/models/menu.py' % app)),
    #         (T('Config.ini'), False,
    #          URL(
    #              'admin', 'default', 'edit/%s/private/appconfig.ini' % app)),
    #         (T('Layout'), False,
    #          URL(
    #              'admin', 'default', 'edit/%s/views/layout.html' % app)),
    #         (T('Stylesheet'), False,
    #          URL(
    #              'admin', 'default', 'edit/%s/static/css/web2py-bootstrap3.css' % app)),
    #         (T('Database'), False, URL(app, 'appadmin', 'index')),
    #         (T('Errors'), False, URL(
    #             'admin', 'default', 'errors/' + app)),
    #         (T('About'), False, URL(
    #             'admin', 'default', 'about/' + app)),
    #     ]),
    #     ('web2py.com', False, '#', [
    #         (T('Download'), False,
    #          'http://www.web2py.com/examples/default/download'),
    #     ]),
    #     (T('Documentation'), False, '#', [
    #         (T('Online book'), False, 'http://www.web2py.com/book'),
    #     ]),
    #     (T('Community'), False, None, [
    #         (T('Groups'), False,
    #          'http://www.web2py.com/examples/default/usergroups'),
    #     ]),
    #]


if DEVELOPMENT_MENU:
    _()

if "auth" in locals():
    auth.wikimenu()
