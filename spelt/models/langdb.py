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

"""Contains LanguageDB: the main model representing a language database and provides access to all its parts."""

import os.path
from lxml          import etree, objectify

from common        import *

from model_factory import ModelFactory
from pos           import PartOfSpeech
from root          import Root
from source        import Source
from surface_form  import SurfaceForm
from user          import User

class LanguageDB(object):
    """
    This class represents and manages a XML language database.
    """

    FILE_EXTENSION = 'xldb' # The normal extension of language database files.

    model_list_map = {
        'part_of_speech' : 'parts_of_speech',
        'root'           : 'roots',
        'source'         : 'sources',
        'surface_form'   : 'surface_forms',
        'user'           : 'users'
    }
    """Maps models' XML tags to the name of the list that contains all instances of a certain model type.
    More simply it can also be seen as a singular-to-plural map of the sections."""

    # ACCESSORS #
    parts_of_speech = property(lambda self: self.sections['parts_of_speech'])
    roots =           property(lambda self: self.sections['roots'])
    sources =         property(lambda self: self.sections['sources'])
    surface_forms =   property(lambda self: self.sections['surface_forms'])
    users =           property(lambda self: self.sections['users'])

    # CONSTRUCTOR #
    # TODO: Use file object instead of forcing opening from filename
    def __init__(self, lang=None, filename=None):
        """Constructor.
            @type  lang: str
            @param lang: ISO 639 language code.
            """
        self.filename = None
        self.lang = lang
        self.sections = dict(zip( self.model_list_map.values(), map(lambda x: [], self.model_list_map.values()) ))

        if not filename is None and os.path.exists(filename):
            self.load(filename)

        if not self.filename:
            self.__create_root()

    # METHODS #
    def add_part_of_speech(self, pos):
        """Add a part of speech to the database.
            @type  pos: PartOfSpeech
            @param pos: The part-of-speech model to add to the database.
            """
        assert isinstance(pos, PartOfSpeech)
        if pos in self.parts_of_speech:
            raise DuplicateModelError(str(pos))

        self.parts_of_speech.append(pos)
        self.xmlroot.parts_of_speech.append(pos.to_xml())

    def add_root(self, root):
        """Add a word root to the database.
            @type  root: Root
            @param root: The word root model to add to the database.
            """
        if root in self.roots:
            raise DuplicateModelError(str(root))

        self.roots.append(root)
        self.xmlroot.roots.append(root.to_xml())

    def add_source(self, src):
        """Add a source to the database.
            @type  src: Source
            @param src: The source model to add to the database.
            """
        assert isinstance(src, Source)
        if src in self.sources:
            raise DuplicateModelError(str(src))

        self.sources.append(src)
        self.xmlroot.sources.append(src.to_xml())

    def add_surface_form(self, sf):
        """Add a surface form model to the database.
            @type  sf: SurfaceForm
            @param sf: The surface form model to add to the database.
            """
        assert isinstance(sf, SurfaceForm)
        if sf in self.surface_forms:
            raise DuplicateModelError(str(sf))

        self.surface_forms.append(sf)
        self.xmlroot.surface_forms.append(sf.to_xml())

    def add_user(self, usr):
        """Add a user to the database.
            @type  usr: User
            @param usr: The user model to add to the database.
            """
        assert isinstance(usr, User)
        if usr in self.users:
            raise DuplicateModelError(str(usr))

        self.users.append(usr)
        self.xmlroot.users.append(usr.to_xml())

    def __create_root(self):
        self.xmlroot                 = objectify.Element('language_database', lang=self.lang)
        self.xmlroot.parts_of_speech = objectify.Element('parts_of_speech')
        self.xmlroot.roots           = objectify.Element('roots')
        self.xmlroot.sources         = objectify.Element('sources')
        self.xmlroot.surface_forms   = objectify.Element('surface_forms')
        self.xmlroot.users           = objectify.Element('users')

    def find(self, id=0, section=None, **kwargs):
        """A generic method to find any of the models contained in the current language database.
            If kwargs are specified, a model will match if ANY of the paris match.
            @type  id:      int
            @param id:      The unique ID for the model to find. (Default: 0 - won't find anything)
            @type  section: str
            @param section: The section (or type of model) to find. One of
                model_list_map.values(). (Default: None)
            @param kwargs:  Other arbitrary attributes to search on. Eg. find(name='Foo')
            @rtype:         list
            @return:        A list of matching models.
            """
        assert id is None or isinstance(id, int)

        if not section is None and section not in self.model_list_map.values():
            section=None

        sections = section and [getattr(self, section)] or [getattr(self, s) for s in self.model_list_map.values()]
        models = []

        for sec in sections:
            for model in sec:
                if model.id == id:
                    models.append(model)
                elif kwargs:
                    match = True
                    for key, val in kwargs.items():
                        if not (hasattr(model, key) and getattr(model, key) == val):
                            match = False
                            break

                    if match:
                        models.append(model)

        return models

    def load(self, filename='lang.'+FILE_EXTENSION):
        """Load a language database from the specified file.
            @type  filename: basestring
            @param filename: The full path to the file to load the language database from.
            """
        xmlroot = objectify.parse(open(filename, 'r')).getroot()

        # Sanity checking for basic language database structure...
        if xmlroot.tag != 'language_database':
            raise LanguageDBFormatError(_('Invalid root tag: %s' % xmlroot.tag, self))

        if 'lang' not in xmlroot.keys():
            raise LanguageDBFormatError('No language code specified!', self)

        self.filename = filename
        self.lang     = xmlroot.get('lang')
        self.xmlroot  = xmlroot

        root_children = [c.tag for c in xmlroot.iterchildren()]
        for section in self.model_list_map.values():
            if section not in root_children:
                setattr(xmlroot, section, objectify.Element(section))
                raise LanguageDBFormatWarning('No top-level "%s" tag.' % section)
            else:
                for child in getattr(xmlroot, section).iterchildren():
                    model = ModelFactory.create_model_from_elem(child)
                    mlist = getattr(self, self.model_list_map[model.tag])

                    if model in mlist:
                        raise DuplicateModelError(str(model))

                    mlist.append(model)

    def save(self, filename=None):
        """Save the represented language database to the specified file.
            @type  filename: basestring
            @param filename: The path and name of the file to store the language database in.
            """
        if filename is None and not self.filename is None:
            filename = self.filename

        if filename is None:
            raise IOError('No filename given!')

        f = open(filename, 'w')
        # FIXME: Find a way to make deannotate() below actually remove those
        # annoying pytype and xsi attribs.
        objectify.deannotate(self.xmlroot)
        print >> f, etree.tostring(
            self.xmlroot,
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8'
        )
        f.close()

        self.filename = filename

    # SPECIAL METHODS #
    def __str__(self):
        filepart = self.filename and '[file="%s"]' % self.filename or '[no file]'
        return '%s[lang="%s"]%s[POS %d|R %d|SRC %d|SF %d|U %d]' % \
            (
                self.__class__.__name__, self.lang, filepart,
                len(self.parts_of_speech),
                len(self.roots),
                len(self.sources),
                len(self.surface_forms),
                len(self.users)
            )
