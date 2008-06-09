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

# Contains LanguageDB: the main model representing a language database and provides access to all its parts.

import os.path
from lxml import objectify
from pan_app import _

class LanguageDB(object):
    """
    This class represents and manages the XML language database.
    """

    def __init__(self, from_file=None, lang=None):
        """Constructor.
            @type  from_file: basestring
            @param from_file: Optional filename to load data from.
            """
        if isinstance(from_file, basestring) and os.path.exists(from_file):
            self.load_from_file(from_file)
        elif isinstance(lang, str) or isinstance(lang, unicode):
            self.root = objectify.Element('languageDatabase')
            self.root.set('language', lang)

        raise ArgumentException(_('Need a valid language database filename to open or a language code'))

    def load_from_file(self, filename):
        """Loads the XML language database from the specified filename.
            @type  filename: basestring
            @param filename: The filename of the XML language database.
            """
        assert isinstance(filename, str) and os.path.exists(filename)

        try:
            self.root = objectify.parse(open(filename, 'r'))
        # TODO: Do more specific error-checking here
        except:
            raise Exception('An error has occurred parsing the XML file %s' % filename)

    def __parse_xml(self):
        """
        Parse the XML structure into other models and store them in member lists/variables.
        """
        pass
