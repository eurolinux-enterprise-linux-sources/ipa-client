/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; version 2 only
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 *
 */
 
try
{
    /* Kerberos SSO configuration */
    lockPref("network.negotiate-auth.trusted-uris", ".freeipa.org");
    lockPref("network.negotiate-auth.delegation-uris", ".freeipa.org");

    /* These are the defaults */
    lockPref("network.negotiate-auth.gsslib", "");
    lockPref("network.negotiate-auth.using-native-gsslib", true);
    lockPref("network.negotiate-auth.allow-proxies", true);

    /* For Windows */
    lockPref("network.auth.use-sspi", false);	
}
catch(e)
{
    displayError("Error in Autoconfig", e);
}
