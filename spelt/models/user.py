#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Spelt.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from common    import *
from lxml      import objectify
from xml_model import XMLModel

class User(XMLModel):
    """
    This class represents user from the language database.
    """

    # CONSTRUCTORS #
    def __init__(self, id=None, name=None):
        """Constructor.
            @type  id: int
            @param id: The user's unique identifier (default None)
            @type  name: basestring
            @param name: User's name (default None)
            """
        assert id is None   or isinstance(id, int)
        assert name is None or isinstance(name, basestring)

        super(User, self).__init__(tag='user', values=['name'], attribs=['id'])
        self.id, self.name = id, name

        if not self.id:
            self.id = 0 # FIXME: Should this find an appropriate ID?

        if not self.name:
            self.name = '<unknown>'

    # METHODS #
    def from_xml(self, elem):
        """
        Calls XMLModel.from_xml(elem) and then converts the 'id' members to int.
        """
        try: super(User, self).from_xml(elem)
        except AssertionError:
            pass

        self.id = int(self.id)
        self.validateData()

    def validateData(self):
        """See XMLModel.validateData()."""
        assert isinstance(self.id, int)
        assert isinstance(unicode(self.name), basestring) and len(unicode(self.name)) > 0

    # CLASS/STATIC METHODS #
    @staticmethod
    def create_from_elem(elem):
        """Factory method to create a User object from a obj.ObjectifiedElement.
            @type  elem: objectify.ObjectifiedElement
            @param elem: The element to read XML information from.
            @rtype:      User
            @return:     An instance containing the data loaded from elem.
            """
        assert isinstance(elem, objectify.ObjectifiedElement)
        u = User()
        u.from_xml(elem)
        return u
