# Authors:
#   Jason Gerard DeRose <jderose@redhat.com>
#
# Copyright (C) 2008  Red Hat
# see file 'COPYING' for use and warranty inmsgion
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
Custom exception classes (some which are RPC transparent).

`PrivateError` and its subclasses are custom IPA excetions that will *never* be
forwarded in a Remote Procedure Call (RPC) response.

On the other hand, `PublicError` and its subclasses can be forwarded in an RPC
response.  These public errors each carry a unique integer error code as well as
a gettext translated error message (translated at the time the exception is
raised).  The purpose of the public errors is to relay information about
*expected* user errors, service availability errors, and so on.  They should
*never* be used for *unexpected* programmatic or run-time errors.

For security reasons it is *extremely* important that arbitrary exceptions *not*
be forwarded in an RPC response.  Unexpected exceptions can easily contain
compromising information in their error messages.  Any time the server catches
any exception that isn't a `PublicError` subclass, it should raise an
`InternalError`, which itself always has the same, static error message (and
therefore cannot be populated with information about the true exception).

The public errors are arranging into five main blocks of error code ranges:

    =============  ========================================
     Error codes                 Exceptions
    =============  ========================================
    1000 - 1999    `AuthenticationError` and its subclasses
    2000 - 2999    `AuthorizationError` and its subclasses
    3000 - 3999    `InvocationError` and its subclasses
    4000 - 4999    `ExecutionError` and its subclasses
    5000 - 5999    `GenericError` and its subclasses
    =============  ========================================

Within these five blocks some sub-ranges are already allocated for certain types
of error messages, while others are reserved for future use.  Here are the
current block assignments:

    - **900-5999** `PublicError` and its subclasses

        - **901 - 907**  Assigned to special top-level public errors

        - **908 - 999**  *Reserved for future use*

        - **1000 - 1999**  `AuthenticationError` and its subclasses

            - **1001 - 1099**  Open for general authentication errors

            - **1100 - 1199**  `KerberosError` and its subclasses

            - **1200 - 1999**  *Reserved for future use*

        - **2000 - 2999**  `AuthorizationError` and its subclasses

            - **2001 - 2099**  Open for general authorization errors

            - **2100 - 2199**  `ACIError` and its subclasses

            - **2200 - 2999**  *Reserved for future use*

        - **3000 - 3999**  `InvocationError` and its subclasses

            - **3001 - 3099**  Open for general invocation errors

            - **3100 - 3199**  *Reserved for future use*

        - **4000 - 4999**  `ExecutionError` and its subclasses

            - **4001 - 4099**  Open for general execution errors

            - **4100 - 4199**  `BuiltinError` and its subclasses

            - **4200 - 4299**  `LDAPError` and its subclasses

            - **4300 - 4399**  `CertificateError` and its subclasses

            - **4400 - 4999**  *Reserved for future use*

        - **5000 - 5999**  `GenericError` and its subclasses

            - **5001 - 5099**  Open for generic errors

            - **5100 - 5999**  *Reserved for future use*
"""

from inspect import isclass
from request import ugettext, ungettext
from constants import TYPE_ERROR


class PrivateError(StandardError):
    """
    Base class for exceptions that are *never* forwarded in an RPC response.
    """

    format = ''

    def __init__(self, **kw):
        self.msg = self.format % kw
        self.kw = kw
        for (key, value) in kw.iteritems():
            assert not hasattr(self, key), 'conflicting kwarg %s.%s = %r' % (
                self.__class__.__name__, key, value,
            )
            setattr(self, key, value)
        StandardError.__init__(self, self.msg)


class SubprocessError(PrivateError):
    """
    Raised when ``subprocess.call()`` returns a non-zero exit status.

    This custom exception is needed because Python 2.4 doesn't have the
    ``subprocess.CalledProcessError`` exception (which was added in Python 2.5).

    For example:

    >>> raise SubprocessError(returncode=2, argv=('ls', '-lh', '/no-foo/'))
    Traceback (most recent call last):
      ...
    SubprocessError: return code 2 from ('ls', '-lh', '/no-foo/')

    The exit code of the sub-process is available via the ``returncode``
    instance attribute.  For example:

    >>> e = SubprocessError(returncode=1, argv=('/bin/false',))
    >>> e.returncode
    1
    >>> e.argv  # argv is also available
    ('/bin/false',)
    """

    format = 'return code %(returncode)d from %(argv)r'


class PluginSubclassError(PrivateError):
    """
    Raised when a plugin doesn't subclass from an allowed base.

    For example:

    >>> raise PluginSubclassError(plugin='bad', bases=('base1', 'base2'))
    Traceback (most recent call last):
      ...
    PluginSubclassError: 'bad' not subclass of any base in ('base1', 'base2')

    """

    format  = '%(plugin)r not subclass of any base in %(bases)r'


class PluginDuplicateError(PrivateError):
    """
    Raised when the same plugin class is registered more than once.

    For example:

    >>> raise PluginDuplicateError(plugin='my_plugin')
    Traceback (most recent call last):
      ...
    PluginDuplicateError: 'my_plugin' was already registered
    """

    format = '%(plugin)r was already registered'


class PluginOverrideError(PrivateError):
    """
    Raised when a plugin overrides another without using ``override=True``.

    For example:

    >>> raise PluginOverrideError(base='Command', name='env', plugin='my_env')
    Traceback (most recent call last):
      ...
    PluginOverrideError: unexpected override of Command.env with 'my_env'
    """

    format = 'unexpected override of %(base)s.%(name)s with %(plugin)r'


class PluginMissingOverrideError(PrivateError):
    """
    Raised when a plugin overrides another that has not been registered.

    For example:

    >>> raise PluginMissingOverrideError(base='Command', name='env', plugin='my_env')
    Traceback (most recent call last):
      ...
    PluginMissingOverrideError: Command.env not registered, cannot override with 'my_env'
    """

    format = '%(base)s.%(name)s not registered, cannot override with %(plugin)r'


class SkipPluginModule(PrivateError):
    """
    Raised to abort the loading of a plugin module.
    """

    format = '%(reason)s'


class PluginsPackageError(PrivateError):
    """
    Raised when ``package.plugins`` is a module instead of a sub-package.
    """

    format = '%(name)s must be sub-package, not module: %(file)r'


##############################################################################
# Public errors:

__messages = []

def _(message):
    __messages.append(message)
    return message


class PublicError(StandardError):
    """
    **900** Base class for exceptions that can be forwarded in an RPC response.
    """

    errno = 900
    rval = 1
    format = None

    def __init__(self, format=None, message=None, **kw):
        self.kw = kw
        name = self.__class__.__name__
        if self.format is not None and format is not None:
            raise ValueError(
                'non-generic %r needs format=None; got format=%r' % (
                    name, format)
            )
        if message is None:
            if self.format is None:
                if format is None:
                    raise ValueError(
                        '%s.format is None yet format=None, message=None' % name
                    )
                self.format = format
            self.forwarded = False
            self.msg = self.format % kw
            self.strerror = ugettext(self.format) % kw
        else:
            if type(message) is not unicode:
                raise TypeError(
                    TYPE_ERROR % ('message', unicode, message, type(message))
                )
            self.forwarded = True
            self.msg = message
            self.strerror = message
        for (key, value) in kw.iteritems():
            assert not hasattr(self, key), 'conflicting kwarg %s.%s = %r' % (
                name, key, value,
            )
            setattr(self, key, value)
        StandardError.__init__(self, self.msg)


class VersionError(PublicError):
    """
    **901** Raised when client and server versions are incompatible.

    For example:

    >>> raise VersionError(cver='2.0', sver='2.1', server='https://localhost')
    Traceback (most recent call last):
      ...
    VersionError: 2.0 client incompatible with 2.1 server at 'https://localhost'

    """

    errno = 901
    format = _('%(cver)s client incompatible with %(sver)s server at %(server)r')


class UnknownError(PublicError):
    """
    **902** Raised when client does not know error it caught from server.

    For example:

    >>> raise UnknownError(code=57, server='localhost', error=u'a new error')
    ...
    Traceback (most recent call last):
      ...
    UnknownError: unknown error 57 from localhost: a new error

    """

    errno = 902
    format = _('unknown error %(code)d from %(server)s: %(error)s')


class InternalError(PublicError):
    """
    **903** Raised to conceal a non-public exception.

    For example:

    >>> raise InternalError()
    Traceback (most recent call last):
      ...
    InternalError: an internal error has occurred
    """

    errno = 903
    format = _('an internal error has occurred')

    def __init__(self, message=None):
        """
        Security issue: ignore any information given to constructor.
        """
        PublicError.__init__(self)


class ServerInternalError(PublicError):
    """
    **904** Raised when client catches an `InternalError` from server.

    For example:

    >>> raise ServerInternalError(server='https://localhost')
    Traceback (most recent call last):
      ...
    ServerInternalError: an internal error has occurred on server at 'https://localhost'
    """

    errno = 904
    format = _('an internal error has occurred on server at %(server)r')


class CommandError(PublicError):
    """
    **905** Raised when an unknown command is called.

    For example:

    >>> raise CommandError(name='foobar')
    Traceback (most recent call last):
      ...
    CommandError: unknown command 'foobar'
    """

    errno = 905
    format = _('unknown command %(name)r')


class ServerCommandError(PublicError):
    """
    **906** Raised when client catches a `CommandError` from server.

    For example:

    >>> e = CommandError(name='foobar')
    >>> raise ServerCommandError(error=e.message, server='https://localhost')
    Traceback (most recent call last):
      ...
    ServerCommandError: error on server 'https://localhost': unknown command 'foobar'
    """

    errno = 906
    format = _('error on server %(server)r: %(error)s')


class NetworkError(PublicError):
    """
    **907** Raised when a network connection cannot be created.

    For example:

    >>> raise NetworkError(uri='ldap://localhost:389', error=u'Connection refused')
    Traceback (most recent call last):
      ...
    NetworkError: cannot connect to 'ldap://localhost:389': Connection refused
    """

    errno = 907
    format = _('cannot connect to %(uri)r: %(error)s')


class ServerNetworkError(PublicError):
    """
    **908** Raised when client catches a `NetworkError` from server.
    """

    errno = 908
    format = _('error on server %(server)r: %(error)s')


class JSONError(PublicError):
    """
    **909** Raised when server recieved a malformed JSON-RPC request.
    """

    errno = 909
    format = _('Invalid JSON-RPC request: %(error)s')



##############################################################################
# 1000 - 1999: Authentication errors
class AuthenticationError(PublicError):
    """
    **1000** Base class for authentication errors (*1000 - 1999*).
    """

    errno = 1000


class KerberosError(AuthenticationError):
    """
    **1100** Base class for Kerberos authentication errors (*1100 - 1199*).

    For example:

    >>> raise KerberosError(major='Unspecified GSS failure.  Minor code may provide more information', minor='No credentials cache found')
    Traceback (most recent call last):
      ...
    KerberosError: Kerberos error: Unspecified GSS failure.  Minor code may provide more information/No credentials cache found

    """

    errno = 1100
    format= _('Kerberos error: %(major)s/%(minor)s')


class CCacheError(KerberosError):
    """
    **1101** Raised when sever does not recieve Kerberose credentials.

    For example:

    >>> raise CCacheError()
    Traceback (most recent call last):
      ...
    CCacheError: did not receive Kerberos credentials

    """

    errno = 1101
    format = _('did not receive Kerberos credentials')


class ServiceError(KerberosError):
    """
    **1102** Raised when service is not found in Kerberos DB.

    For example:

    >>> raise ServiceError(service='HTTP@localhost')
    Traceback (most recent call last):
      ...
    ServiceError: Service 'HTTP@localhost' not found in Kerberos database
    """

    errno = 1102
    format = _('Service %(service)r not found in Kerberos database')


class NoCCacheError(KerberosError):
    """
    **1103** Raised when a client attempts to use Kerberos without a ccache.

    For example:

    >>> raise NoCCacheError()
    Traceback (most recent call last):
      ...
    NoCCacheError: No credentials cache found
    """

    errno = 1103
    format = _('No credentials cache found')


class TicketExpired(KerberosError):
    """
    **1104** Raised when a client attempts to use an expired ticket

    For example:

    >>> raise TicketExpired()
    Traceback (most recent call last):
      ...
    TicketExpired: Ticket expired
    """

    errno = 1104
    format = _('Ticket expired')


class BadCCachePerms(KerberosError):
    """
    **1105** Raised when a client has bad permissions on their ccache

    For example:

    >>> raise BadCCachePerms()
    Traceback (most recent call last):
      ...
    BadCCachePerms: Credentials cache permissions incorrect
    """

    errno = 1105
    format = _('Credentials cache permissions incorrect')


class BadCCacheFormat(KerberosError):
    """
    **1106** Raised when a client has a misformated ccache

    For example:

    >>> raise BadCCacheFormat()
    Traceback (most recent call last):
      ...
    BadCCacheFormat: Bad format in credentials cache
    """

    errno = 1106
    format = _('Bad format in credentials cache')


class CannotResolveKDC(KerberosError):
    """
    **1107** Raised when the KDC can't be resolved

    For example:

    >>> raise CannotResolveKDC()
    Traceback (most recent call last):
      ...
    CannotResolveKDC: Cannot resolve KDC for requested realm
    """

    errno = 1107
    format = _('Cannot resolve KDC for requested realm')


##############################################################################
# 2000 - 2999: Authorization errors
class AuthorizationError(PublicError):
    """
    **2000** Base class for authorization errors (*2000 - 2999*).
    """

    errno = 2000


class ACIError(AuthorizationError):
    """
    **2100** Base class for ACI authorization errors (*2100 - 2199*).
    """

    errno = 2100
    format = _('Insufficient access: %(info)s')



##############################################################################
# 3000 - 3999: Invocation errors

class InvocationError(PublicError):
    """
    **3000** Base class for command invocation errors (*3000 - 3999*).
    """

    errno = 3000


class EncodingError(InvocationError):
    """
    **3001** Raised when received text is incorrectly encoded.
    """

    errno = 3001


class BinaryEncodingError(InvocationError):
    """
    **3002** Raised when received binary data is incorrectly encoded.
    """

    errno = 3002


class ZeroArgumentError(InvocationError):
    """
    **3003** Raised when a command is called with arguments but takes none.

    For example:

    >>> raise ZeroArgumentError(name='ping')
    Traceback (most recent call last):
      ...
    ZeroArgumentError: command 'ping' takes no arguments
    """

    errno = 3003
    format = _('command %(name)r takes no arguments')


class MaxArgumentError(InvocationError):
    """
    **3004** Raised when a command is called with too many arguments.

    For example:

    >>> raise MaxArgumentError(name='user_add', count=2)
    Traceback (most recent call last):
      ...
    MaxArgumentError: command 'user_add' takes at most 2 arguments
    """

    errno = 3004

    def __init__(self, message=None, **kw):
        if message is None:
            format = ungettext(
                'command %(name)r takes at most %(count)d argument',
                'command %(name)r takes at most %(count)d arguments',
                kw['count']
            )
        else:
            format = None
        InvocationError.__init__(self, format, message, **kw)


class OptionError(InvocationError):
    """
    **3005** Raised when a command is called with unknown options.
    """

    errno = 3005


class OverlapError(InvocationError):
    """
    **3006** Raised when arguments and options overlap.

    For example:

    >>> raise OverlapError(names=['givenname', 'login'])
    Traceback (most recent call last):
      ...
    OverlapError: overlapping arguments and options: ['givenname', 'login']
    """

    errno = 3006
    format = _('overlapping arguments and options: %(names)r')


class RequirementError(InvocationError):
    """
    **3007** Raised when a required parameter is not provided.

    For example:

    >>> raise RequirementError(name='givenname')
    Traceback (most recent call last):
      ...
    RequirementError: 'givenname' is required
    """

    errno = 3007
    format = _('%(name)r is required')


class ConversionError(InvocationError):
    """
    **3008** Raised when parameter value can't be converted to correct type.

    For example:

    >>> raise ConversionError(name='age', error=u'must be an integer')
    Traceback (most recent call last):
      ...
    ConversionError: invalid 'age': must be an integer
    """

    errno = 3008
    format = _('invalid %(name)r: %(error)s')


class ValidationError(InvocationError):
    """
    **3009** Raised when a parameter value fails a validation rule.

    For example:

    >>> raise ValidationError(name='sn', error=u'can be at most 128 characters')
    Traceback (most recent call last):
      ...
    ValidationError: invalid 'sn': can be at most 128 characters
    """

    errno = 3009
    format = _('invalid %(name)r: %(error)s')


class NoSuchNamespaceError(InvocationError):
    """
    **3010** Raised when an unknown namespace is requested.

    For example:

    >>> raise NoSuchNamespaceError(name='Plugins')
    Traceback (most recent call last):
      ...
    NoSuchNamespaceError: api has no such namespace: 'Plugins'
    """

    errno = 3010
    format = _('api has no such namespace: %(name)r')


class PasswordMismatch(InvocationError):
    """
    **3011** Raise when password and password confirmation don't match.
    """

    errno = 3011
    format = _('Passwords do not match')

class NotImplementedError(InvocationError):
    """
    **3012** Raise when a function hasn't been implemented.
    """

    errno = 3012
    format = _('Command not implemented')


##############################################################################
# 4000 - 4999: Execution errors

class ExecutionError(PublicError):
    """
    **4000** Base class for execution errors (*4000 - 4999*).
    """

    errno = 4000

class NotFound(ExecutionError):
    """
    **4001** Raised when an entry is not found.

    For example:

    >>> raise NotFound(reason='no such user')
    Traceback (most recent call last):
      ...
    NotFound: no such user

    """

    errno = 4001
    rval = 2
    format = _('%(reason)s')

class DuplicateEntry(ExecutionError):
    """
    **4002** Raised when an entry already exists.

    For example:

    >>> raise DuplicateEntry
    Traceback (most recent call last):
      ...
    DuplicateEntry: This entry already exists

    """

    errno = 4002
    format = _('This entry already exists')

class HostService(ExecutionError):
    """
    **4003** Raised when a host service principal is requested

    For example:

    >>> raise HostService
    Traceback (most recent call last):
      ...
    HostService: You must enroll a host in order to create a host service

    """

    errno = 4003
    format = _('You must enroll a host in order to create a host service')

class MalformedServicePrincipal(ExecutionError):
    """
    **4004** Raised when a service principal is not of the form: service/fully-qualified host name

    For example:

    >>> raise MalformedServicePrincipal(reason='missing service')
    Traceback (most recent call last):
      ...
    MalformedServicePrincipal: Service principal is not of the form: service/fully-qualified host name: missing service

    """

    errno = 4004
    format = _('Service principal is not of the form: service/fully-qualified host name: %(reason)s')

class RealmMismatch(ExecutionError):
    """
    **4005** Raised when the requested realm does not match the IPA realm

    For example:

    >>> raise RealmMismatch
    Traceback (most recent call last):
      ...
    RealmMismatch: The realm for the principal does not match the realm for this IPA server

    """

    errno = 4005
    format = _('The realm for the principal does not match the realm for this IPA server')

class RequiresRoot(ExecutionError):
    """
    **4006** Raised when a command requires the unix super-user to run

    For example:

    >>> raise RequiresRoot
    Traceback (most recent call last):
      ...
    RequiresRoot: This command requires root access

    """

    errno = 4006
    format = _('This command requires root access')

class AlreadyPosixGroup(ExecutionError):
    """
    **4007** Raised when a group is already a posix group

    For example:

    >>> raise AlreadyPosixGroup
    Traceback (most recent call last):
      ...
    AlreadyPosixGroup: This is already a posix group

    """

    errno = 4007
    format = _('This is already a posix group')

class MalformedUserPrincipal(ExecutionError):
    """
    **4008** Raised when a user principal is not of the form: user@REALM

    For example:

    >>> raise MalformedUserPrincipal(principal='jsmith@@EXAMPLE.COM')
    Traceback (most recent call last):
      ...
    MalformedUserPrincipal: Principal is not of the form user@REALM: 'jsmith@@EXAMPLE.COM'

    """

    errno = 4008
    format = _('Principal is not of the form user@REALM: %(principal)r')

class AlreadyActive(ExecutionError):
    """
    **4009** Raised when an entry is made active that is already active

    For example:

    >>> raise AlreadyActive()
    Traceback (most recent call last):
      ...
    AlreadyActive: This entry is already unlocked

    """

    errno = 4009
    format = _('This entry is already unlocked')

class AlreadyInactive(ExecutionError):
    """
    **4010** Raised when an entry is made inactive that is already inactive

    For example:

    >>> raise AlreadyInactive()
    Traceback (most recent call last):
      ...
    AlreadyInactive: This entry is already locked

    """

    errno = 4010
    format = _('This entry is already locked')

class HasNSAccountLock(ExecutionError):
    """
    **4011** Raised when an entry has the nsAccountLock attribute set

    For example:

    >>> raise HasNSAccountLock()
    Traceback (most recent call last):
      ...
    HasNSAccountLock: This entry has nsAccountLock set, it cannot be locked or unlocked

    """

    errno = 4011
    format = _('This entry has nsAccountLock set, it cannot be locked or unlocked')

class NotGroupMember(ExecutionError):
    """
    **4012** Raised when a non-member is attempted to be removed from a group

    For example:

    >>> raise NotGroupMember()
    Traceback (most recent call last):
      ...
    NotGroupMember: This entry is not a member of the group

    """

    errno = 4012
    format = _('This entry is not a member of the group')

class RecursiveGroup(ExecutionError):
    """
    **4013** Raised when a group is added as a member of itself

    For example:

    >>> raise RecursiveGroup()
    Traceback (most recent call last):
      ...
    RecursiveGroup: A group may not be a member of itself

    """

    errno = 4013
    format = _('A group may not be a member of itself')

class AlreadyGroupMember(ExecutionError):
    """
    **4014** Raised when a member is attempted to be re-added to a group

    For example:

    >>> raise AlreadyGroupMember()
    Traceback (most recent call last):
      ...
    AlreadyGroupMember: This entry is already a member of the group

    """

    errno = 4014
    format = _('This entry is already a member of the group')

class Base64DecodeError(ExecutionError):
    """
    **4015** Raised when a base64-encoded blob cannot decoded

    For example:

    >>> raise Base64DecodeError(reason='Incorrect padding')
    Traceback (most recent call last):
      ...
    Base64DecodeError: Base64 decoding failed: Incorrect padding

    """

    errno = 4015
    format = _('Base64 decoding failed: %(reason)s')

class RemoteRetrieveError(ExecutionError):
    """
    **4016** Raised when retrieving data from a remote server fails

    For example:

    >>> raise RemoteRetrieveError(reason="Error: Failed to get certificate chain.")
    Traceback (most recent call last):
      ...
    RemoteRetrieveError: Error: Failed to get certificate chain.

    """

    errno = 4016
    format = _('%(reason)s')

class SameGroupError(ExecutionError):
    """
    **4017** Raised when adding a group as a member of itself

    For example:

    >>> raise SameGroupError()
    Traceback (most recent call last):
      ...
    SameGroupError: A group may not be added as a member of itself

    """

    errno = 4017
    format = _('A group may not be added as a member of itself')

class DefaultGroupError(ExecutionError):
    """
    **4018** Raised when removing the default user group

    For example:

    >>> raise DefaultGroupError()
    Traceback (most recent call last):
      ...
    DefaultGroupError: The default users group cannot be removed

    """

    errno = 4018
    format = _('The default users group cannot be removed')

class BuiltinError(ExecutionError):
    """
    **4100** Base class for builtin execution errors (*4100 - 4199*).
    """

    errno = 4100


class HelpError(BuiltinError):
    """
    **4101** Raised when requesting help for an unknown topic.

    For example:

    >>> raise HelpError(topic='newfeature')
    Traceback (most recent call last):
      ...
    HelpError: no command nor help topic 'newfeature'
    """

    errno = 4101
    format = _('no command nor help topic %(topic)r')


class LDAPError(ExecutionError):
    """
    **4200** Base class for LDAP execution errors (*4200 - 4299*).
    """

    errno = 4200


class MidairCollision(ExecutionError):
    """
    **4201** Raised when a change collides with another change

    For example:

    >>> raise MidairCollision()
    Traceback (most recent call last):
      ...
    MidairCollision: change collided with another change
    """

    errno = 4201
    format = _('change collided with another change')


class EmptyModlist(ExecutionError):
    """
    **4202** Raised when an LDAP update makes no changes

    For example:

    >>> raise EmptyModlist()
    Traceback (most recent call last):
      ...
    EmptyModlist: no modifications to be performed
    """

    errno = 4202
    format = _('no modifications to be performed')


class DatabaseError(ExecutionError):
    """
    **4203** Raised when an LDAP error is not otherwise handled

    For example:

    >>> raise DatabaseError(desc="Can't contact LDAP server", info='')
    Traceback (most recent call last):
      ...
    DatabaseError: Can't contact LDAP server:
    """

    errno = 4203
    format = _('%(desc)s:%(info)s')


class LimitsExceeded(ExecutionError):
    """
    **4204** Raised when search limits are exceeded.

    For example:

    >>> raise LimitsExceeded()
    Traceback (most recent call last):
      ...
    LimitsExceeded: limits exceeded for this query
    """

    errno = 4204
    format = _('limits exceeded for this query')

class ObjectclassViolation(ExecutionError):
    """
    **4205** Raised when an entry is missing a required attribute or objectclass

    For example:

    >>> raise ObjectclassViolation(info='attribute "krbPrincipalName" not allowed')
    Traceback (most recent call last):
      ...
    ObjectclassViolation: attribute "krbPrincipalName" not allowed
    """

    errno = 4205
    format = _('%(info)s')


class CertificateError(ExecutionError):
    """
    **4300** Base class for Certificate execution errors (*4300 - 4399*).
    """

    errno = 4300


class CertificateOperationError(ExecutionError):
    """
    **4301** Raised when a certificate operation cannot be completed

    For example:

    >>> raise CertificateOperationError(error=u'bad serial number')
    Traceback (most recent call last):
      ...
    CertificateOperationError: Certificate operation cannot be completed: bad serial number

    """

    errno = 4301
    format = _('Certificate operation cannot be completed: %(error)s')


##############################################################################
# 5000 - 5999: Generic errors

class GenericError(PublicError):
    """
    **5000** Base class for errors that don't fit elsewhere (*5000 - 5999*).
    """

    errno = 5000



def __errors_iter():
    """
    Iterate through all the `PublicError` subclasses.
    """
    for (key, value) in globals().items():
        if key.startswith('_') or not isclass(value):
            continue
        if issubclass(value, PublicError):
            yield value

public_errors = tuple(
    sorted(__errors_iter(), key=lambda E: E.errno)
)

if __name__ == '__main__':
    for klass in public_errors:
        print '%d\t%s' % (klass.code, klass.__name__)
    print '(%d public errors)' % len(public_errors)
