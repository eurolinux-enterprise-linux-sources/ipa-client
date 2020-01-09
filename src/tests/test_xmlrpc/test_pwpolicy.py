# Authors:
#   Rob Crittenden <rcritten@redhat.com>
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
Test the `ipalib/plugins/pwpolicy.py` module.
"""

import sys
from xmlrpc_test import XMLRPC_test, assert_attr_equal
from ipalib import api
from ipalib import errors


class test_pwpolicy(XMLRPC_test):
    """
    Test the `pwpolicy` plugin.
    """
    group = u'testgroup1'
    group2 = u'testgroup2'
    user = u'testuser1'
    kw = {'group': group, 'cospriority': 1, 'krbminpwdlife': 30, 'krbmaxpwdlife': 40, 'krbpwdhistorylength': 5, 'krbpwdminlength': 6 }
    kw2 = {'group': group2, 'cospriority': 2, 'krbminpwdlife': 40, 'krbmaxpwdlife': 60, 'krbpwdhistorylength': 8, 'krbpwdminlength': 9 }

    def test_1_pwpolicy_add(self):
        """
        Test adding a per-group policy using the `xmlrpc.pwpolicy_add` method.
        """
        # First set up a group and user that will use this policy
        self.failsafe_add(
            api.Object.group, self.group, description=u'pwpolicy test group',
        )
        self.failsafe_add(
            api.Object.user, self.user, givenname=u'Test', sn=u'User'
        )
        api.Command.group_add_member(self.group, users=self.user)

        entry = api.Command['pwpolicy_add'](**self.kw)['result']
        assert_attr_equal(entry, 'krbminpwdlife', '30')
        assert_attr_equal(entry, 'krbmaxpwdlife', '40')
        assert_attr_equal(entry, 'krbpwdhistorylength', '5')
        assert_attr_equal(entry, 'krbpwdminlength', '6')

    def test_2_pwpolicy_add(self):
        """
        Add a policy with a duplicate priority

        The priority validation is done first so it's ok that the group
        is the same here.
        """
        try:
            api.Command['pwpolicy_add'](**self.kw)
        except errors.ValidationError:
            pass
        else:
            assert False

    def test_3_pwpolicy_add(self):
        """
        Add a policy that already exists
        """
        try:
            # cospriority needs to be unique
            self.kw['cospriority'] = 3
            api.Command['pwpolicy_add'](**self.kw)
        except errors.DuplicateEntry:
            pass
        else:
            assert False

    def test_4_pwpolicy_add(self):
        """
        Test adding another per-group policy using the `xmlrpc.pwpolicy_add` method.
        """
        self.failsafe_add(
            api.Object.group, self.group2, description=u'pwpolicy test group 2'
        )
        entry = api.Command['pwpolicy_add'](**self.kw2)['result']
        assert_attr_equal(entry, 'krbminpwdlife', '40')
        assert_attr_equal(entry, 'krbmaxpwdlife', '60')
        assert_attr_equal(entry, 'krbpwdhistorylength', '8')
        assert_attr_equal(entry, 'krbpwdminlength', '9')

    def test_5_pwpolicy_add(self):
        """
        Add a pwpolicy for a non-existent group
        """
        try:
            api.Command['pwpolicy_add'](group=u'nopwpolicy',cospriority=4,krbminpwdlife=1)
        except errors.NotFound:
            pass
        else:
            assert False

    def test_6_pwpolicy_show(self):
        """
        Test the `xmlrpc.pwpolicy_show` method with global policy.
        """
        entry = api.Command['pwpolicy_show']()['result']
        # Note that this assumes an unchanged global policy
        assert_attr_equal(entry, 'krbminpwdlife', '1')
        assert_attr_equal(entry, 'krbmaxpwdlife', '90')
        assert_attr_equal(entry, 'krbpwdhistorylength', '0')
        assert_attr_equal(entry, 'krbpwdminlength', '8')

    def test_7_pwpolicy_show(self):
        """
        Test the `xmlrpc.pwpolicy_show` method.
        """
        entry = api.Command['pwpolicy_show'](group=self.group)['result']
        assert_attr_equal(entry, 'krbminpwdlife', '30')
        assert_attr_equal(entry, 'krbmaxpwdlife', '40')
        assert_attr_equal(entry, 'krbpwdhistorylength', '5')
        assert_attr_equal(entry, 'krbpwdminlength', '6')

    def test_8_pwpolicy_mod(self):
        """
        Test the `xmlrpc.pwpolicy_mod` method for global policy.
        """
        entry = api.Command['pwpolicy_mod'](krbminpwdlife=50)['result']
        assert_attr_equal(entry, 'krbminpwdlife', '50')

        # Great, now change it back
        entry = api.Command['pwpolicy_mod'](krbminpwdlife=1)['result']
        assert_attr_equal(entry, 'krbminpwdlife', '1')

    def test_9_pwpolicy_mod(self):
        """
        Test the `xmlrpc.pwpolicy_mod` method.
        """
        entry = api.Command['pwpolicy_mod'](group=self.group, krbminpwdlife=50)['result']
        assert_attr_equal(entry, 'krbminpwdlife', '50')

    def test_a_pwpolicy_mod(self):
        """
        Test `xmlrpc.pwpolicy_mod` with a duplicate priority
        """
        try:
            api.Command['pwpolicy_mod'](group=self.group, cospriority=1)
        except errors.ValidationError:
            pass
        else:
            assert False

    def test_b_pwpolicy_del(self):
        """
        Test the `xmlrpc.pwpolicy_del` method.
        """
        assert api.Command['pwpolicy_del'](group=self.group)['result'] is True
        # Verify that it is gone
        try:
            api.Command['pwpolicy_show'](group=self.group)
        except errors.NotFound:
            pass
        else:
            assert False

        # Remove the groups we created
        api.Command['group_del'](self.group)
        api.Command['group_del'](self.group2)

        # Remove the user we created
        api.Command['user_del'](self.user)
