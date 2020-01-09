# Authors:
#   Rob Crittenden <rcritten@redhat.com>
#   Pavel Zuna <pzuna@redhat.com>
#   Jason Gerard DeRose <jderose@redhat.com>
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
Test the `ipalib/plugins/user.py` module.
"""

from ipalib import api, errors
from tests.test_xmlrpc import objectclasses
from xmlrpc_test import Declarative, fuzzy_digits, fuzzy_uuid


user_memberof = (u'cn=ipausers,cn=groups,cn=accounts,%s' % api.env.basedn,)
user1=u'tuser1'


class test_user(Declarative):

    cleanup_commands = [
        ('user_del', [user1], {}),
    ]

    tests = [

        dict(
            desc='Try to retrieve non-existent %r' % user1,
            command=('user_show', [user1], {}),
            expected=errors.NotFound(reason='no such entry'),
        ),


        dict(
            desc='Try to update non-existent %r' % user1,
            command=('user_mod', [user1], dict(givenname=u'Foo')),
            expected=errors.NotFound(reason='no such entry'),
        ),


        dict(
            desc='Try to delete non-existent %r' % user1,
            command=('user_del', [user1], {}),
            expected=errors.NotFound(reason='no such entry'),
        ),


        dict(
            desc='Create %r' % user1,
            command=(
                'user_add', [], dict(givenname=u'Test', sn=u'User1')
            ),
            expected=dict(
                value=user1,
                summary=u'Added user "tuser1"',
                result=dict(
                    gecos=[user1],
                    givenname=[u'Test'],
                    homedirectory=[u'/home/tuser1'],
                    krbprincipalname=[u'tuser1@' + api.env.realm],
                    loginshell=[u'/bin/sh'],
                    objectclass=objectclasses.user,
                    sn=[u'User1'],
                    uid=[user1],
                    ipauniqueid=[fuzzy_uuid],
                    dn=u'uid=tuser1,cn=users,cn=accounts,' + api.env.basedn,
                ),
            ),
        ),


        dict(
            desc='Try to create duplicate %r' % user1,
            command=(
                'user_add', [], dict(givenname=u'Test', sn=u'User1')
            ),
            expected=errors.DuplicateEntry(),
        ),


        dict(
            desc='Retrieve %r' % user1,
            command=(
                'user_show', [user1], {}
            ),
            expected=dict(
                result=dict(
                    dn=u'uid=tuser1,cn=users,cn=accounts,%s' % api.env.basedn,
                    givenname=[u'Test'],
                    homedirectory=[u'/home/tuser1'],
                    loginshell=[u'/bin/sh'],
                    sn=[u'User1'],
                    uid=[user1],
                    memberof_group=[u'ipausers'],
                ),
                value=user1,
                summary=None,
            ),
        ),


        dict(
            desc='Search for %r with all=True' % user1,
            command=(
                'user_find', [user1], {'all': True}
            ),
            expected=dict(
                result=[
                    {
                        'dn': u'uid=tuser1,cn=users,cn=accounts,' + api.env.basedn,
                        'cn': [u'Test User1'],
                        'gecos': [user1],
                        'givenname': [u'Test'],
                        'homedirectory': [u'/home/tuser1'],
                        'krbprincipalname': [u'tuser1@' + api.env.realm],
                        'loginshell': [u'/bin/sh'],
                        'memberof_group': [u'ipausers'],
                        'objectclass': objectclasses.user,
                        'sn': [u'User1'],
                        'uid': [user1],
                        'uidnumber': [fuzzy_digits],
                        'gidnumber': [fuzzy_digits],
                        'ipauniqueid': [fuzzy_uuid],
                    },
                ],
                summary=u'1 user matched',
                count=1, truncated=False,
            ),
        ),


        dict(
            desc='Search for %r with minimal attributes' % user1,
            command=(
                'user_find', [user1], {}
            ),
            expected=dict(
                result=[
                    dict(
                        dn=u'uid=tuser1,cn=users,cn=accounts,' + api.env.basedn,
                        givenname=[u'Test'],
                        homedirectory=[u'/home/tuser1'],
                        loginshell=[u'/bin/sh'],
                        sn=[u'User1'],
                        uid=[user1],
                        memberof_group=[u'ipausers'],
                    ),
                ],
                summary=u'1 user matched',
                count=1,
                truncated=False,
            ),
        ),


        dict(
            desc='Search for all users',
            command=(
                'user_find', [], {}
            ),
            expected=dict(
                result=[
                    dict(
                        dn=u'uid=admin,cn=users,cn=accounts,' + api.env.basedn,
                        homedirectory=[u'/home/admin'],
                        loginshell=[u'/bin/bash'],
                        sn=[u'Administrator'],
                        uid=[u'admin'],
                        memberof_group=[u'admins'],
                    ),
                    dict(
                        dn=u'uid=tuser1,cn=users,cn=accounts,' + api.env.basedn,
                        givenname=[u'Test'],
                        homedirectory=[u'/home/tuser1'],
                        loginshell=[u'/bin/sh'],
                        sn=[u'User1'],
                        uid=[user1],
                        memberof_group=[u'ipausers'],
                    ),
                ],
                summary=u'2 users matched',
                count=2,
                truncated=False,
            ),
        ),


        dict(
            desc='Lock %r' % user1,
            command=(
                'user_lock', [user1], {}
            ),
            expected=dict(
                result=True,
                value=user1,
                summary=u'Locked user "tuser1"',
            ),
        ),


        dict(
            desc='Unlock %r'  % user1,
            command=(
                'user_unlock', [user1], {}
            ),
            expected=dict(
                result=True,
                value=user1,
                summary=u'Unlocked user "tuser1"',
            ),
        ),


        dict(
            desc='Update %r' % user1,
            command=(
                'user_mod', [user1], dict(givenname=u'Finkle')
            ),
            expected=dict(
                result=dict(
                    givenname=[u'Finkle'],
                    homedirectory=[u'/home/tuser1'],
                    loginshell=[u'/bin/sh'],
                    sn=[u'User1'],
                    uid=[user1],
                    memberof_group=[u'ipausers'],
                ),
                summary=u'Modified user "tuser1"',
                value=user1,
            ),
        ),


        dict(
            desc='Retrieve %r to verify update' % user1,
            command=('user_show', [user1], {}),
            expected=dict(
                result=dict(
                    dn=u'uid=tuser1,cn=users,cn=accounts,%s' % api.env.basedn,
                    givenname=[u'Finkle'],
                    homedirectory=[u'/home/tuser1'],
                    loginshell=[u'/bin/sh'],
                    sn=[u'User1'],
                    uid=[user1],
                    memberof_group=[u'ipausers'],
                ),
                summary=None,
                value=user1,
            ),

        ),


        dict(
            desc='Delete %r' % user1,
            command=('user_del', [user1], {}),
            expected=dict(
                result=True,
                summary=u'Deleted user "tuser1"',
                value=user1,
            ),
        ),


        dict(
            desc='Try to delete non-existent %r' % user1,
            command=('user_del', [user1], {}),
            expected=errors.NotFound(reason='no such entry'),
        ),


        dict(
            desc='Try to retrieve non-existent %r' % user1,
            command=('user_show', [user1], {}),
            expected=errors.NotFound(reason='no such entry'),
        ),


        dict(
            desc='Try to update non-existent %r' % user1,
            command=('user_mod', [user1], dict(givenname=u'Foo')),
            expected=errors.NotFound(reason='no such entry'),
        ),


    ]
