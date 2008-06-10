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
from lxml         import objectify
from pan_app      import _
from pos          import PartOfSpeech
from root         import Root
from source       import Source
from surface_form import SurfaceForm
from user         import User

class LanguageDB(object):
    """
    This class represents and manages a XML language database.
    """

    # CONSTRUCTOR #
    def __init__(self, lang=None):
        """Constructor.
            @type  lang: str
            @param lang: ISO 639 language code.
            """
        self.lang = lang
        self.parts_of_speech, self.roots, self.sources, self.surface_forms, self.users = [], [], [], [], []
        self.__createRoot()

    # METHODS #
    def add_part_of_speech(self, pos):
        """Add a part of speech to the database.
            @type  pos: PartOfSpeech
            @param pos: The part-of-speech model to add to the database.
            """
        assert isinstance(pos, PartOfSpeech)
        if pos in self.parts_of_speech:
            raise 'PartOfSpeach already in database!'

        self.parts_of_speech.append(pos)
        self.xmlroot.parts_of_speech.append(pos.to_xml())

    def add_root(self, root):
        """Add a word root to the database.
            @type  root: Root
            @param root: The word root model to add to the database.
            """
        assert isinstance(root, Root)
        if root in self.roots:
            raise 'Root already in database!'

        self.roots.append(root)
        self.xmlroot.roots.append(root.to_xml())

    def add_source(self, src):
        """Add a source to the database.
            @type  src: Source
            @param src: The source model to add to the database.
            """
        assert isinstance(src, Source)
        if src in self.sources:
            raise 'Source already in database!'

        self.sources.append(src)
        self.xmlroot.sources.append(src.to_xml())

    def add_surface_form(self, sf):
        """Add a surface form model to the database.
            @type  sf: SurfaceForm
            @param sf: The surface form model to add to the database.
            """
        assert isinstance(sf, SurfaceForm)
        if sf in self.surface_forms:
            raise 'SurfaceForm already in database!'

        self.surface_forms.append(sf)
        self.xmlroot.surface_forms.append(sf.to_xml())

    def add_user(self, user):
        """Add a user to the database.
            @type  user: User
            @param user: The user model to add to the database.
            """
        assert isinstance(user, User)
        if user in self.users:
            raise 'User already in database!'

        self.users.append(user)
        self.xmlroot.users.append(user.to_xml())

    def __create_root(self):
        self.xmlroot                 = objectify.Element('language_database', lang=self.lang)
        self.xmlroot.parts_of_speech = objectify.Element('parts_of_speech')
        self.xmlroot.roots           = objectify.Element('roots')
        self.xmlroot.sources         = objectify.Element('sources')
        self.xmlroot.surface_forms   = objectify.Element('surface_forms')
        self.xmlroot.users           = objectify.Element('users')

    def load(self, filename='lang.xldb'):
        """Load a language database from the specified file.
            @type  filename: basestring
            @param filename: The full path to the file to load the language database from.
            """
        # TODO: Check that file exists
        self.xmlroot = objectify.parse(open(filename, 'r')).getroot()
        self.filename = filename

    def save(self, filename=None):
        """Save the represented language database to the specified file.
            @type  filename: basestring
            @param filename: The path and name of the file to store the language database in.
            """
        if filename is None and not self.filename is None:
            filename = self.filename

        if filename is None:
            raise 'Invalid filename!'

        f = open(filename, 'w')
        print >> f, etree.tostring(pretty_print=True)
        f.close()
