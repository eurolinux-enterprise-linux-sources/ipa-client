# Authors:
#   Rob Crittenden <rcritten@redhat.com>
#   Pavel Zuna <pzuna@redhat.com>
#
# Copyright (C) 2008, 2009  Red Hat
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
Test the `ipalib.plugins.hostgroup` module.
"""

from ipalib import api, errors
from tests.test_xmlrpc.xmlrpc_test import Declarative, fuzzy_uuid
from tests.test_xmlrpc import objectclasses

hostgroup1 = u'testhostgroup1'
dn1 = u'cn=%s,cn=hostgroups,cn=accounts,%s' % (hostgroup1, api.env.basedn)

fqdn1 = u'testhost1.%s' % api.env.domain
host_dn1 = u'fqdn=%s,cn=computers,cn=accounts,%s' % (fqdn1, api.env.basedn)


class test_hostgroup(Declarative):

    cleanup_commands = [
        ('hostgroup_del', [hostgroup1], {}),
        ('host_del', [fqdn1], {}),
    ]

    tests=[

        dict(
            desc='Try to retrieve non-existent %r' % hostgroup1,
            command=('hostgroup_show', [hostgroup1], {}),
            expected=errors.NotFound(reason='no such entry'),
        ),


        dict(
            desc='Try to update non-existent %r' % hostgroup1,
            command=('hostgroup_mod', [hostgroup1],
                dict(description=u'Updated hostgroup 1')
            ),
            expected=errors.NotFound(reason='no such entry'),
        ),


        dict(
            desc='Try to delete non-existent %r' % hostgroup1,
            command=('hostgroup_del', [hostgroup1], {}),
            expected=errors.NotFound(reason='no such entry'),
        ),


        dict(
            desc='Create %r' % hostgroup1,
            command=('hostgroup_add', [hostgroup1],
                dict(description=u'Test hostgroup 1')
            ),
            expected=dict(
                value=hostgroup1,
                summary=u'Added hostgroup "testhostgroup1"',
                result=dict(
                    dn=dn1,
                    cn=[hostgroup1],
                    objectclass=objectclasses.hostgroup,
                    description=[u'Test hostgroup 1'],
                    ipauniqueid=[fuzzy_uuid],
                ),
            ),
        ),


        dict(
            desc='Try to create duplicate %r' % hostgroup1,
            command=('hostgroup_add', [hostgroup1],
                dict(description=u'Test hostgroup 1')
            ),
            expected=errors.DuplicateEntry(),
        ),


        dict(
            desc='Create host %r' % fqdn1,
            command=('host_add', [fqdn1],
                dict(
                    description=u'Test host 1',
                    l=u'Undisclosed location 1',
                ),
            ),
            expected=dict(
                value=fqdn1,
                summary=u'Added host "%s"' % fqdn1,
                result=dict(
                    dn=host_dn1,
                    fqdn=[fqdn1],
                    description=[u'Test host 1'],
                    l=[u'Undisclosed location 1'],
                    krbprincipalname=[u'host/%s@%s' % (fqdn1, api.env.realm)],
                    objectclass=objectclasses.host,
                    ipauniqueid=[fuzzy_uuid],
                ),
            ),
        ),


        dict(
            desc=u'Add host %r to %r' % (fqdn1, hostgroup1),
            command=(
                'hostgroup_add_member', [hostgroup1], dict(host=fqdn1)
            ),
            expected=dict(
                completed=1,
                failed=dict(
                    member=dict(
                        host=tuple(),
                        hostgroup=tuple(),
                    ),
                ),
                result={
                    'dn': dn1,
                    'cn': [hostgroup1],
                    'description': [u'Test hostgroup 1'],
                    'member_host': [fqdn1],
                },
            ),
        ),


        dict(
            desc='Retrieve %r' % hostgroup1,
            command=('hostgroup_show', [hostgroup1], {}),
            expected=dict(
                value=hostgroup1,
                summary=None,
                result={
                    'dn': dn1,
                    'member_host': [u'testhost1.%s' % api.env.domain],
                    'cn': [hostgroup1],
                    'description': [u'Test hostgroup 1'],
                },
            ),
        ),


        dict(
            desc='Search for %r' % hostgroup1,
            command=('hostgroup_find', [], dict(cn=hostgroup1)),
            expected=dict(
                count=1,
                truncated=False,
                summary=u'1 hostgroup matched',
                result=[
                    {
                        'dn': dn1,
                        'member_host': [u'testhost1.%s' % api.env.domain],
                        'cn': [hostgroup1],
                        'description': [u'Test hostgroup 1'],
                    },
                ],
            ),
        ),


        dict(
            desc='Update %r' % hostgroup1,
            command=('hostgroup_mod', [hostgroup1],
                dict(description=u'Updated hostgroup 1')
            ),
            expected=dict(
                value=hostgroup1,
                summary=u'Modified hostgroup "testhostgroup1"',
                result=dict(
                    cn=[hostgroup1],
                    description=[u'Updated hostgroup 1'],
                    member_host=[u'testhost1.%s' % api.env.domain],
                ),
            ),
        ),


        dict(
            desc='Retrieve %r to verify update' % hostgroup1,
            command=('hostgroup_show', [hostgroup1], {}),
            expected=dict(
                value=hostgroup1,
                summary=None,
                result={
                    'dn': dn1,
                    'member_host': [u'testhost1.%s' % api.env.domain],
                    'cn': [hostgroup1],
                    'description': [u'Updated hostgroup 1'],
                },
            ),
        ),


        dict(
            desc='Remove host %r from %r' % (fqdn1, hostgroup1),
            command=('hostgroup_remove_member', [hostgroup1],
                dict(host=fqdn1)
            ),
            expected=dict(
                failed=dict(
                    member=dict(
                        host=tuple(),
                        hostgroup=tuple(),
                    ),
                ),
                completed=1,
                result={
                    'dn': dn1,
                    'cn': [hostgroup1],
                    'description': [u'Updated hostgroup 1'],
                },
            ),
        ),


        dict(
            desc='Delete %r' % hostgroup1,
            command=('hostgroup_del', [hostgroup1], {}),
            expected=dict(
                value=hostgroup1,
                summary=u'Deleted hostgroup "testhostgroup1"',
                result=True,
            ),
        ),


        dict(
            desc='Delete host %r' % fqdn1,
            command=('host_del', [fqdn1], {}),
            expected=dict(
                value=fqdn1,
                summary=u'Deleted host "%s"' % fqdn1,
                result=True,
            ),
        )

    ]
