# Copyright © 2025
# See file 'LICENSE' for use and warranty information.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Organizational Unit (OU) management plugin
"""

from ipalib import _, ngettext
from ipalib import api, errors, output, Command
from ipalib.output import Output, Entry, ListOfEntries
from ipalib.parameters import *
from ipalib.plugable import Registry
from .baseldap import (
    LDAPObject,
    LDAPCreate,
    LDAPDelete,
    LDAPUpdate,
    LDAPSearch,
    LDAPRetrieve,
    LDAPAddMember,
    LDAPRemoveMember
)
from ipapython.dn import DN


altou_base_dn = '{0}'.format(api.env.basedn)
register = Registry()


@register()
class ou(LDAPObject):
    """
    Organizational Unit object
    """
    container_dn = DN(('cn', 'altou'))
    object_name = _('Organizational Unit')
    object_name_plural = _('Organizational Units')
    object_class = ['altOrganizationalUnit', 'organizationalUnit', 'top']
    default_attributes = [
        'ou', 'description',
        'gPLink', 'objectCategory'
    ]
    uuid_attribute = 'ipauniqueid'
    search_attributes = ['ou', 'description', 'objectCategory', 'gPLink']
    permission_filter_objectclasses = ['altOrganizationalUnit']
    permission_filter_objectclasses_string = '(objectclass=altOrganizationalUnit)'
    label = _('Organizational Units')
    label_singular = _('Organizational Unit')

    managed_permissions = {
        'System: Read Organizational Units': {
            'replaces_global_anonymous_aci': True,
            'ipapermright': {'read', 'search', 'compare'},
            'ipapermbindruletype': 'permission',
            'ipapermdefaultattr': {
                'objectclass', 'ou', 'description',
                'gPLink', 'objectCategory'
            },
        },
        'System: Add Organizational Units': {
            'ipapermright': {'add'},
            'ipapermtargetfilter': ['(objectclass=altOrganizationalUnit)'],
            'default_privileges': {'Policy Administrators'},
        },
        'System: Modify Organizational Units': {
            'ipapermright': {'write'},
            'ipapermtargetfilter': ['(objectclass=altOrganizationalUnit)'],
            'ipapermdefaultattr': {
                'objectclass', 'ou', 'description',
                'gPLink', 'objectCategory'
            },
            'default_privileges': {'Policy Administrators'},
        },
        'System: Remove Organizational Units': {
            'ipapermright': {'delete'},
            'ipapermtargetfilter': ['(objectclass=altOrganizationalUnit)'],
            'default_privileges': {'Policy Administrators'},
        }
    }

    takes_params = (

        Str(
            'description?',
            cli_name='description',
            label=_('Description'),
            doc=_('Organizational Unit description.')
        ),
        Str(
            'ou',
            cli_name='ou',
            label=_('Organizational Unit name'),
            doc=_('Organizational Unit .'),
            primary_key=True
        ),
        Str(
            'gplink?',
            cli_name='gplink',
            label=_('Group Policy Link'),
            doc=_('Group Policy Link.')
        ),
        Str(
            'objectcategory?',
            cli_name='objectcategory',
            label=_('Object Category'),
            doc=_('Object Category.')
        )
    )

@register()
class ou_add(LDAPCreate):
    __doc__ = _('Create a new Organizational Unit.')
    msg_summary = _('Created Organizational Unit "%(value)s"')

    def pre_callback(self, ldap, dn, entry_attrs, attrs_list, *keys, **options):
        assert isinstance(dn, DN)
        container_dn = DN(self.obj.container_dn, api.env.basedn)

        try:
            ldap.get_entry(container_dn, ['objectclass'])
        except errors.NotFound:
            container_entry = ldap.make_entry(
                container_dn,
                objectclass=['nsContainer', 'top'],
                cn=['altou']
            )
            try:
                ldap.add_entry(container_entry)
            except errors.DuplicateEntry:
                pass
            except Exception as e:
                raise errors.NotFound(
                    reason=_('Failed to create container %(container)s: %(error)s') % {
                        'container': str(container_dn),
                        'error': str(e)
                    }
                )

        if 'objectcategory' not in entry_attrs:
            entry_attrs['objectCategory'] = f'CN=altOrganizationalUnit,CN=schema,{api.env.basedn}'

        return dn

@register()
class ou_del(LDAPDelete):
    """
    Delete an Organizational Unit.
    """

@register()
class ou_mod(LDAPUpdate):
    """
    Modify an Organizational Unit.
    """

@register()
class ou_find(LDAPSearch):
    """
    Search for Organizational Units.
    """

@register()
class ou_show(LDAPRetrieve):
    """
    Display an Organizational Unit.
    """

# @register()
# class ou_member_add(LDAPAddMember):
#     """
#     Add a member to an Organizational Unit.
#     """

# @register()
# class ou_member_remove(LDAPRemoveMember):
#     """
#     Remove a member from an Organizational Unit.
#     """
