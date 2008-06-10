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

from id_manager import IDManager
from lxml       import objectify
from pan_app    import _

class XMLModel(IDManager):
    """
    This base-class of that provides common XML reading and writing methods.

    This class is only meant to be inherited from, but can conceivably be used
    on its own (see test_xml_model).
    """

    # CONSTRUCTORS #
    def __init__(self, tag, values, attribs):
        """Constructor.

            @type  tag:       str
            @param tag:       The XML-tag to use to represent an instance of this model.
            @type  values:    list
            @param values:    A list of names of accepted the child values.
            @type  attribs:   list
            @param attribs:   A list of accepted attributes
            """
        assert isinstance(tag, str) and len(tag) > 0

        super(XMLModel, self).__init__()

        self.tag       = tag
        self.values    = values
        self.attribs   = attribs

    # METHODS #
    def from_xml(self, elem):
        """Read data from the given objectify.ObjectifiedElement element.
            NOTE: Using this method will _not_ preserve any undeclared information.
            NOTE: Attributes are always saved as strings

            @type  elem: objectify.ObjectifiedElement
            @param elem: The element to read data from.
            """
        assert elem and isinstance(elem, objectify.ObjectifiedElement)

        if elem.tag != self.tag:
            raise InvalidElementException(_("The parameter element's tag is not valid for this model."))

        for at in self.attribs:
            if at == 'id':
                if self.id > 0:
                    self.del_id(self.id)
                self.id = int( elem.get('id') )
            else:
                setattr(self, at, elem.get(at))

        for v in self.values:
            try: elem_v = getattr(elem, v)
            except AttributeError:
                elem_v = None

            if isinstance(elem_v, objectify.StringElement):
                setattr(self, v, unicode(elem_v))
            else:
                setattr(self, v, elem_v)

        self.validateData()

    def to_xml(self):
        """Create an objectify.ObjectifiedElement from the model.
            @rtype:  objectify.Element
            @return: The constructed XML element."""
        self.validateData()

        root = objectify.Element(self.tag)

        for at in self.attribs:
            if at == 'id':
                root.set('id', str(self.id))
            else:
                root.set(at, str(getattr(self, at)))

        for v in self.values:
            setattr(root, v, getattr(self, v))

        return root

    def validateData(self):
        """
        Checks whether all data-constraints are met.

        A successful validation should mean that:
            * All required data is present
            * All required data members are of the correct type

        Notes to this function's relevance in XML-related operations:
            - Optional values (not attributes) may be None.
            - Attributes declared in XMLModel.__init__ must have a non-None
              value.

        This method is empty and should be overridden in inheriting classes.
        It should throw an exception if validation fails.
        """
        pass
