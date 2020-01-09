# Authors: Jason Gerard DeRose <jderose@redhat.com>
#
# Copyright (C) 2009  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
IPA web UI.
"""

# Special wehjit initialization to prevent it from loading the plugins that
# require pygments, which uses ctypes, which makes the httpd SELinux policy
# crazy:
import wehjit
wehjit.builtins._skip_pygments = True
wehjit.init_builtins()

from ipalib.backend import Executioner
from ipalib.request import destroy_context
from ipaserver.rpcserver import extract_query
from controllers import JSON
from engine import Engine
from widgets import create_widgets

from assetslib import Assets
from wehjit import Application


def join_url(base, url):
    if url.startswith('/'):
        return url
    return base + url


class WebUI(Application):
    def __init__(self, api):
        self.api = api
        baseurl = api.env.mount_ipa
        assets = Assets(
            url=join_url(baseurl, api.env.mount_webui_assets),
            dir=api.env.webui_assets_dir,
            prod=api.env.webui_prod,
        )
        super(WebUI, self).__init__(
            url=join_url(baseurl, api.env.mount_webui),
            assets=assets,
            widgets=create_widgets(),
            prod=api.env.webui_prod,
        )
        self.api.Backend.session.mount(self, api.env.mount_webui)



def create_wsgi_app(api):
    app = WebUI(api)
    engine = Engine(api, app)
    engine.build()

    app.finalize()

    return app
