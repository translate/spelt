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

import gobject, gtk, gtk.glade

from common   import exceptions, _
from models   import LanguageDB, PartOfSpeech, Root, SurfaceForm
from wordlist import WordList

COL_TEXT, COL_MODEL = range(2)

class EditArea(object):
    """
    This class represents the editing area on the GUI.
    """

    # CONSTRUCTOR #
    def __init__(self, glade_xml, word_list, langdb=None, gui=None):
        """Constructor.
            @type  glade_xml: gtk.glade.XML
            @param glade_xml: The Glade XML object to load widgets from.
            """
        assert isinstance(glade_xml, gtk.glade.XML)
        assert isinstance(word_list, WordList)

        self.current_sf = None
        self.glade_xml  = glade_xml
        self.gui        = gui
        self.langdb     = langdb
        self.word_list  = word_list
        self.word_list.word_selected_handlers.append(self.on_surface_form_selected)
        self.__init_widgets()

    # METHODS #
    def on_surface_form_selected(self, sf):
        self.current_sf = sf
        self.lbl_word.set_markup('<b>%s</b>' % sf.value)

        if self.langdb is None:
            return

        if not sf.root_id:
            self.cmb_root.child.set_text('')
            self.cmb_pos.child.set_text('')
            self.cmb_root.set_active(-1)
            self.cmb_pos.set_active(-1)
            return

        roots_found = self.langdb.find(id=sf.root_id, section='roots')
        # The roots_found list can have a maximum of 1 element, because we
        # search the database on ID's. ID's are guaranteed to be unique by the
        # models (via it's inheritence of IDModel).
        if roots_found:
            self.select_root(roots_found[0])
        else:
            raise exceptions.RootError(_( 'No root object found with ID %d' % (sf.root_id) ))

    def pos_tostring(self, pos):
        """How a PartOfSpeech object should be represented as a string in the GUI.

            @type  pos: PartOfSpeech
            @param pos: The PartOfSpeech object to get a string representation for.
            @rtype      str
            @return     The string representation of the parameter PartOfSpeech."""
        if not pos:
            return ''
        assert isinstance(pos, PartOfSpeech)
        # TODO: Test RTL scripts
        return '%s | %s' % (pos.shortcut, pos.name)

    def root_tostring(self, root):
        """How a Root object should be represented as a string in the GUI.

            @type  pos: Root
            @param pos: The Root object to get a string representation for.
            @rtype      str
            @return     The string representation of the parameter Root."""
        if not root:
            return ''
        return unicode(root.value) # TODO: Test unicode significance.

    def refresh(self, langdb=None):
        """Reload data from self.langdb database."""
        if not langdb is None and isinstance(langdb, LanguageDB):
            self.langdb = langdb

        if not self.langdb or not isinstance(self.langdb, LanguageDB):
            return

        self.pos_store.clear()
        self.root_store.clear()
        [self.pos_store.append([self.pos_tostring(model), model]) for model in self.langdb.parts_of_speech]
        [self.root_store.append([self.root_tostring(model), model]) for model in self.langdb.roots]

    def select_root(self, root):
        """Set the root selected in the cmb_root combo box to that of the parameter.

            @type  root: models.Root
            @param root: The root to select in the combo box."""
        assert isinstance(root, Root)
        iter = self.root_store.get_iter_root()

        while self.root_store.iter_is_valid(iter):
            if self.root_store.get_value(iter, COL_MODEL) == root:
                self.cmb_root.set_active_iter(iter)
                break

            iter = self.root_store.iter_next(iter)

    def select_pos(self, pos):
        """Set the part of speech selected in the cmb_pos combo box to that of
            the parameter.

            @type  pos: models.PartOfSpeech
            @param pos: The part of speech to select in the combo box."""
        assert isinstance(pos, PartOfSpeech)
        iter = self.pos_store.get_iter_root()

        while self.pos_store.iter_is_valid(iter):
            if self.pos_store.get_value(iter, COL_MODEL) == pos:
                self.cmb_pos.set_active_iter(iter)
                break

            iter = self.pos_store.iter_next(iter)

    def __init_widgets(self):
        """Get and initialize widgets from the Glade object."""
        widgets = (
            'lbl_word',
            'btn_blacklist',
            'btn_reject',
            'cmb_root',
            'cmb_pos',
            'btn_add_root',
            'btn_mod_root'
        )

        for widget_name in widgets:
            setattr(self, widget_name, self.glade_xml.get_widget(widget_name))

        self.lbl_word.set_markup('<b>[nothing]</b>')

        # Initialize combo's
        pos_cell = gtk.CellRendererText()
        self.pos_store = gtk.ListStore(str, gobject.TYPE_PYOBJECT)
        self.cmb_pos.clear()
        self.cmb_pos.pack_start(pos_cell)
        self.cmb_pos.add_attribute(pos_cell, 'text', COL_TEXT)
        self.cmb_pos.set_cell_data_func(pos_cell, self.__render_pos)
        self.cmb_pos.set_model(self.pos_store)
        self.cmb_pos.set_text_column(COL_TEXT)
        self.cmb_pos.connect('changed', self.__on_cmb_pos_changed)

        root_cell = gtk.CellRendererText()
        self.root_store = gtk.ListStore(str, gobject.TYPE_PYOBJECT)
        self.cmb_root.clear()
        self.cmb_root.pack_start(root_cell)
        self.cmb_root.add_attribute(root_cell, 'text', COL_TEXT)
        self.cmb_root.set_model(self.root_store)
        self.cmb_root.set_text_column(COL_TEXT)
        self.cmb_root.connect('changed', self.__on_cmb_root_changed)

        # Setup autocompletion
        pos_cell = gtk.CellRendererText()
        pos_completion = gtk.EntryCompletion()
        pos_completion.clear()
        pos_completion.pack_start(pos_cell)
        pos_completion.set_model(self.pos_store)
        pos_completion.set_match_func(self.__match_pos)
        pos_completion.connect('match-selected', self.__on_match_selected, self.cmb_pos)
        self.cmb_pos.child.set_completion(pos_completion)

        root_cell = gtk.CellRendererText()
        root_completion = gtk.EntryCompletion()
        root_completion.clear()
        root_completion.pack_start(root_cell)
        root_completion.set_cell_data_func(root_cell, self.__render_root)
        root_completion.set_model(self.root_store)
        root_completion.set_match_func(self.__match_root)
        root_completion.connect('match-selected', self.__on_match_selected, self.cmb_root)
        self.cmb_root.child.set_completion(root_completion)

        self.refresh()

    def __on_cmb_pos_changed(self, cmb_pos):
        assert cmb_pos is self.cmb_pos

        # TODO: Handle root with different POS here.

    def __on_cmb_root_changed(self, cmb_root):
        assert cmb_root is self.cmb_root

    def __on_match_selected(self, completion, store, iter, combo):
        child_iter = store.convert_iter_to_child_iter(iter)
        if combo is self.cmb_root:
            self.cmb_pos.grab_focus()
        else:
            self.btn_reject.grab_focus()
        combo.set_active_iter(child_iter)
        combo.child.set_text( combo.get_model().get_value(child_iter, COL_TEXT) )

        return True

    def __match_pos(self, completion, key, iter):
        model = self.pos_store.get_value(iter, COL_MODEL)
        return model.shortcut.lower().startswith(key) or model.name.lower().startswith(key)

    def __match_root(self, completion, key, iter):
        model = self.root_store.get_value(iter, COL_MODEL)
        return model.value.startswith(key)
