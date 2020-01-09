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

ipacfg="ipa.cfg"

for file in /usr/lib/firefox-* /usr/lib64/firefox*
do
    # Find the configuration file we want to change
    cfg=`find $file -name all.js`

    # determine the directory by removing all.js
    dir=`echo $cfg | sed 's/greprefs\/all.js//'`

    # It is possible that there will be empty Firefox directories, so skip
    # those.
    if test "X"$cfg != "X"; then

        rm -f $cfg.new

        # If the configuration already exists, remove it
        if grep general.config.filename $cfg > /dev/null 2>&1; then
            grep -v general.config.filename $cfg > $cfg.new
            mv $cfg.new $cfg
        fi

        # We have the configuration unobscured
        if grep general.config.filename $cfg > /dev/null 2>&1; then
            grep -v general.config.obscure_value $cfg > $cfg.new
            mv $cfg.new $cfg
        fi

        # Now we can add the new stuff to the file
        echo "pref('general.config.obscure_value', 0);" >> "$cfg"
        echo "pref('general.config.filename', '$ipacfg');" >> "$cfg"

        # Create a link to our configuration file
        rm -f $dir/$ipacfg
        ln -s /usr/share/ipa/ipa.cfg $dir/$ipacfg
    fi
done
