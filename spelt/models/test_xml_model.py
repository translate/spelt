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

from lxml     import etree, objectify
from StringIO import StringIO

from spelt.models.xml_model import XMLModel

class TestXMLModel:
    """Unit test for XMLModel class."""

    xml = StringIO("""
        <person sex="male" race="chinese">
            <height>182</height>
            <weight>70.5</weight>
            <notes></notes>
        </person>
        """)

    def __init__(self):
        self.model = XMLModel('person', values=['height', 'weight', 'notes'], attribs=['sex', 'race'])
        self.model.from_xml(objectify.parse(TestXMLModel.xml).getroot())

    def test_from_xml(self):
        """
        Test that XMLModel.from_xml() works by checking that members are assigned
        according to the hard-coded values represented in xml.
        """
        assert self.model.sex == 'male'
        assert self.model.race == 'chinese'
        assert self.model.height == 182
        assert self.model.weight == 70.5
        assert self.model.notes == ''

    def test_to_xml(self):
        """
        Test that XMLModel.to_xml() works by comparing the source
        lxml.objectify.ObjectifiedElement used to create a XMLModel and the element
        returned by to_xml().
        """
        fromroot = objectify.parse(TestXMLModel.xml).getroot()
        self.model.from_xml(fromroot)
        toroot = self.model.to_xml()

        assert fromroot.get('sex') == toroot.get('sex')
        assert fromroot.get('race') == toroot.get('race')
        assert fromroot.height == toroot.height
        assert fromroot.weight == toroot.weight
        assert fromroot.notes == toroot.notes

if __name__ == '__main__':
    test = TestXMLModel()
    test.test_from_xml()
    test.test_to_xml()
