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
from pan_app   import _
from xml_model import XMLModel

class Source(XMLModel):
    """
    This class represents a source for a word
    """

    # ACCESSORS #
    def _get_date(self):
        if isinstance(self._date, datetime):
            return str(int( time.mktime(self._date.timetuple()) ))
    def _set_date(self, v):
        if isinstance(v, datetime):
            self._date = v
        elif isinstance(v, basestring):
            self._date = datetime.fromtimestamp(float(v))
    date = property( _get_date, _set_date, (lambda self: delattr(self, '_date')) )

    # CONSTRUCTORS #
    def __init__(self, id=None, date=None, import_user_id=None, name=None, filename=None, desc=None):
        """Constructor.
            @type  id:             int
            @param id:             ID from XML file (default None).
            @type  date:           datetime.datetime
            @param date:           A timestamp string representing the date the source was added (default None).
            @type  import_user_id: int
            @param import_user_id: The ID of the user that imported the source (right? (default None).
            @type  name:           basestring
            @param name:           The source's name (default None).
            @type  filename:       basestring
            @param filename:       The filename of the source (default None).
            @type  desc:           basestring
            @param desc:           Description (default None).
            """
        # Check that date is a valid timestamp
        if not date is None:
            assert isinstance(date, datetime)

        super(Source, self).__init__(
            tag='source',
            attribs=['id', 'date', 'import_user_id'],
            values=['name', 'filename', 'description']
        )
        self.id, self._date, self.import_user_id = id, date, import_user_id
        self.name, self.filename, self.description = name, filename, desc

    # METHODS #
    def from_xml(self, elem):
        """
        Calls XMLModel.from_xml(elem) and then converts the 'id' and
        'import_user_id' members to int.
        """
        try: super(Source, self).from_xml(elem)
        except AssertionError:
            pass

        self.id = int(self.id)
        self.import_user_id = int(self.import_user_id)

        self.validateData()

    def validateData(self):
        """See XMLModel.validateData()."""
        assert isinstance(self.id, int)
        assert isinstance(self._date, datetime)
        assert isinstance(self.import_user_id, int)
        assert len(self.name) > 0

    # CLASS/STATIC METHODS #
    @staticmethod
    def create_from_elem(elem):
        """Factory method to create a Source object from an objectify.ObjectifiedElement.
            @type  elem: objectify.ObjectifiedElement
            @param elem: The element to read XML information from.
            @rtype:      Source
            @return:     An instance containing the data loaded from elem.
            """
        assert isinstance(elem, objectify.ObjectifiedElement)
        s = Source()
        s.from_xml(elem)
        return s
