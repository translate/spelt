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

import time
from datetime  import datetime
from lxml      import objectify
from xml_model import XMLModel

class Root(XMLModel):
    """
    This class represents a word root as represented in the XML language database.
    """

    # ACCESSORS #
    def _get_date(self):
        return str(int( time.mktime(self._date.timetuple()) ))
    def _set_date(self, v):
        if isinstance(v, datetime):
            self._date = v
        elif isinstance(v, basestring):
            self._date = datetime.fromtimestamp(float(v))
    date = property(_get_date, _set_date)


    # CONSTRUCTORS #
    def __init__(self, value=u'', remarks=None, id=0, pos_id=0, user_id=0, date=None):
        """
        Constructor.

        @type  value:   basestring
        @param value:   The actual word root text
        @type  remarks: basestring
        @param remarks: Arbitrary user remarks
        @type  id:      int
        @param id:      Unique identifier of the word root
        @type  pos_id:  int
        @param pos_id:  The word root's part-of-speech's ID
        @type  user_id: int
        @param user_id: The ID of the user that added/changed the root
        @type  date:    datetime.datetime
        @param date:    The last modification date of the word root
        """
        assert isinstance(value, basestring)
        assert remarks is None or isinstance(remarks, basestring)
        assert isinstance(id, int)
        assert isinstance(pos_id, int)
        assert isinstance(user_id, int)
        assert date is None or isinstance(date, datetime)

        if date is None:
            date = datetime.now()

        super(Root, self).__init__(
            tag='root',
            values=['value', 'remarks'],
            attribs=['id', 'pos_id', 'user_id', 'date']
        )

        self.value   = value
        self.remarks = remarks
        self.id      = id
        self.pos_id  = pos_id
        self.user_id = user_id
        self.date    = date

    # METHODS #
    def from_xml(self, elem):
        """
        Calls XMLModel.from_xml(elem) and then converts the 'id', 'pos_id'
        and 'user_id' members to int.
        """
        try: super(Root, self).from_xml(elem)
        except AssertionError:
            pass

        self.pos_id = int(self.pos_id)
        self.user_id = int(self.user_id)

        self.validateData()

    def validateData(self):
        """See XMLModel.validateData()."""
        assert len(self.value) > 0
        assert self.remarks is None or isinstance(self.remarks, basestring)
        assert isinstance(self.id, int)
        assert isinstance(self.pos_id, int)
        assert isinstance(self.user_id, int)
        assert isinstance(self._date, datetime)

    # CLASS/STATIC METHODS #
    @staticmethod
    def create_from_elem(elem):
        """Factory method to create a Root object from a lxml.objectify.ObjectifiedElement.
            @type  elem: lxml.objectify.ObjectifiedElement
            @param elem: The element to read XML information from.
            @rtype:      Root
            @return:     An instance containing the data loaded from elem.
            """
        assert isinstance(elem, objectify.ObjectifiedElement)
        r = Root()
        r.from_xml(elem)
        return r

    # SPECIAL METHODS #
    def __eq__(self, rhs):
        return self.id == rhs.id

    def __hash__(self):
        return self.id
