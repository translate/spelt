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
from datetime import datetime
from lxml     import objectify

from spelt.models.xml_model import XMLModel

VALID_STATUSES = ('classified', 'ignored', 'rejected', 'todo')

class SurfaceForm(XMLModel):
    """
    This class represents a surface form word (a word with a root).
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
    def __init__(self, value='', status='', id=0, user_id=0, date=None, source_id=0, root_id=0):
        """
        Constructor.
            @type  value:     basestring
            @param value:     The surface form word.
            @type  id:        int
            @param id:        A unique identifier for the instance.
            @type  status:    str
            @param status:    The classification status of the surface form word.
            @type  user_id:   int
            @param user_id:   The user that classified the word.
            @type  date:      datetime.datetime
            @param date:      Date of classification.
            @type  source_id: int
            @param source_id: Source associated with this word.
            @type  root_id:   int
            @param root_id:   ID of the root word for this structure.
            """
        assert isinstance(value, basestring)
        assert isinstance(status, str)
        assert isinstance(id, int)
        assert isinstance(user_id, int)
        assert date is None or isinstance(date, datetime)
        assert isinstance(source_id, int)
        assert isinstance(root_id, int)

        super(SurfaceForm, self).__init__(
            tag='surface_form',
            values=['value', 'status'],
            attribs=['id', 'user_id', 'date', 'source_id', 'root_id']
        )

        if date is None:
            self.date = datetime.now()

        self.value     = value
        self.status    = status
        self.id        = id
        self.user_id   = user_id
        self.date      = date
        self.source_id = source_id
        self.root_id   = root_id

    # METHODS #
    def from_xml(self, elem):
        """
        Calls XMLModel.from_xml(elem) and then converts the 'user_id',
        'source_id' and 'root_id' members to int.
        """
        try: super(SurfaceForm, self).from_xml(elem)
        except AssertionError:
            pass

        self.user_id   = int(self.user_id)
        if self.source_id:
            self.source_id = int(self.source_id)
        if self.root_id:
            self.root_id   = int(self.root_id)

        self.validate_data()

    def validate_data(self):
        """See XMLModel.validate_data()."""
        assert isinstance(unicode(self.value), basestring) and len(unicode(self.value)) > 0
        assert isinstance(str(self.status), str)           and self.status in VALID_STATUSES
        assert isinstance(self.id, int)                    and self.id > 0
        assert isinstance(self.user_id, int)               and self.user_id > 0
        assert isinstance(self._date, datetime)
        assert isinstance(self.source_id, int)

    # CLASS/STATIC METHODS #
    @staticmethod
    def create_from_elem(elem):
        """Factory method to create a Source object from an lxml.objectify.ObjectifiedElement.
            @type  elem: lxml.objectify.ObjectifiedElement
            @param elem: The element to read XML information from.
            @rtype:      SurfaceForm
            @return:     An instance containing the data loaded from elem.
            """
        assert isinstance(elem, objectify.ObjectifiedElement)
        sf = SurfaceForm()
        sf.from_xml(elem)
        return sf

    # SPECIAL METHODS #
    def __eq__(self, rhs):
        return self.value == rhs.value and self.root_id == rhs.root_id

    def __hash__(self):
        return self.id
