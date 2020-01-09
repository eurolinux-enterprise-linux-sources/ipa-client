#!/bin/sh

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

for file in `find $HOME/.mozilla -name prefs.js`
do
    rm -f $file.new

    # If the configuration already exists, remove it
    if grep network.negotiate- $file > /dev/null 2>&1; then
        grep -v network.negotiate- $file > $file.new
        mv $file.new $file
    fi

    # We have the configuration unobscured
    if grep network.auth.use-sspi $file > /dev/null 2>&1; then
        grep -v network.auth.use-sspi $file > $file.new
        mv $file.new $file
    fi

    # Now we can add the new stuff to the file
    echo "user_pref('network.auth.use-sspi', false);" >> $file
    echo "user_pref('network.cookie.prefsMigrated', true);" >> $file
    echo "user_pref('network.negotiate-auth.allow-proxies', true);" >> $file
    echo "user_pref('network.negotiate-auth.delegation-uris', '.freeipa.org');" >> $file
    echo "user_pref('network.negotiate-auth.gsslib', '');" >> $file
    echo "user_pref('network.negotiate-auth.trusted-uris', '.freeipa.org');" >> $file
    echo "user_pref('network.negotiate-auth.using-native-gsslib', true);" >> $file
done
