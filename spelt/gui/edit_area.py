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
    def __init__(self, glade_xml, wordlist, langdb=None, gui=None):
        """Constructor.
            @type  glade_xml: gtk.glade.XML
            @param glade_xml: The Glade XML object to load widgets from.
            """
        assert isinstance(glade_xml, gtk.glade.XML)
        assert isinstance(wordlist, WordList)

        self.current_sf = None
        self.glade_xml  = glade_xml
        self.gui        = gui
        self.langdb     = langdb
        self.wordlist   = wordlist
        self.wordlist.word_selected_handlers.append(self.on_surface_form_selected)
        self.__init_widgets()

    # METHODS #
    def on_surface_form_selected(self, sf):
        """A proxied event handler for when a surface form is selected in the
            word list.

            See the documentation of spelt.gui.WordList.word_selected_handlers for
            the use of this method."""
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

                pos_found = self.langdb.find(id=root.pos_id, section='parts_of_speech')
                # The pos_found list can have a maximum of 1 element, because we
                # search the database on ID's. ID's are guaranteed to be unique by the
                # models (via it's inheritence of IDModel).
                if pos_found:
                    self.select_pos(pos_found[0])
                else:
                    raise exceptions.PartOfSpeechError(_( 'No part of speech found with ID %d' % (root.pos_id) ))
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
            'btn_reject',
            'btn_ignore',
            'cmb_root',
            'cmb_pos',
            'btn_ok',
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
        self.cmb_pos.set_model(self.pos_store)
        self.cmb_pos.set_text_column(COL_TEXT)

        root_cell = gtk.CellRendererText()
        self.root_store = gtk.ListStore(str, gobject.TYPE_PYOBJECT)
        self.cmb_root.clear()
        self.cmb_root.pack_start(root_cell)
        self.cmb_root.add_attribute(root_cell, 'text', COL_TEXT)
        self.cmb_root.set_model(self.root_store)
        self.cmb_root.set_text_column(COL_TEXT)

        # Setup autocompletion
        pos_cell = gtk.CellRendererText()
        self.pos_completion = gtk.EntryCompletion()
        self.pos_completion.clear()
        self.pos_completion.pack_start(pos_cell)
        self.pos_completion.set_cell_data_func(pos_cell, self.__render_pos)
        self.pos_completion.set_model(self.pos_store)
        self.pos_completion.set_match_func(self.__match_pos)
        self.cmb_pos.child.set_completion(self.pos_completion)

        root_cell = gtk.CellRendererText()
        self.root_completion = gtk.EntryCompletion()
        self.root_completion.clear()
        self.root_completion.pack_start(root_cell)
        self.root_completion.set_cell_data_func(root_cell, self.__render_root)
        self.root_completion.set_model(self.root_store)
        self.root_completion.set_match_func(self.__match_root)
        self.cmb_root.child.set_completion(self.root_completion)

        self.__connect_signals()

        self.refresh()

    def __connect_signals(self):
        """Connects widgets' signals to their appropriate handlers.

            This method should only be called once (by __init_widgets()), but
            shouldn't break anything if it's called again: the same events will
            just be reconnected to the same handlers."""
        # Buttons
        self.btn_add_root.connect('clicked', self.__on_btn_add_root_clicked)
        self.btn_ignore.connect('clicked', self.__on_btn_ignore_clicked)
        self.btn_mod_root.connect('clicked', self.__on_btn_mod_root_clicked)
        self.btn_ok.connect('clicked', self.__on_btn_ok_clicked)
        self.btn_reject.connect('clicked', self.__on_btn_reject_clicked)
        # Combo's
        self.cmb_pos.connect('changed', self.__on_cmb_pos_changed)
        self.cmb_root.connect('changed', self.__on_cmb_root_changed)
        # EntryCompletions
        self.pos_completion.connect('match-selected', self.__on_match_selected, self.cmb_pos)
        self.root_completion.connect('match-selected', self.__on_match_selected, self.cmb_root)

    def __match_pos(self, completion, key, iter):
        model = self.pos_store.get_value(iter, COL_MODEL)
        return model.shortcut.lower().startswith(key) or model.name.lower().startswith(key)

    def __match_root(self, completion, key, iter):
        model = self.root_store.get_value(iter, COL_MODEL)
        return model.value.startswith(key)

    # GUI SIGNAL HANDLERS #
    def __on_btn_add_root_clicked(self, btn):
        pass

    def __on_btn_ignore_clicked(self, btn):
        """Set the currently selected surface form's status to "ignored"."""
        if not self.current_sf:
            return

        self.current_sf.status = 'ignored'
        self.gui.reload_database()

    def __on_btn_mod_root_clicked(self, btn):
        pass

    def __on_btn_ok_clicked(self, btn):
        pass

    def __on_btn_reject_clicked(self, btn):
        """Set the currently selected surface form's status to "rejected"."""
        if not self.current_sf:
            return

        self.current_sf.status = 'rejected'
        self.gui.reload_database()

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

    def __render_pos(self, layout, cell, store, iter):
        """Cell data function that renders a part-of-speech from it's model in
            the gtk.ListStore.

            See gtk.CellLayout.set_cell_data_func()'s documentation for
            description of parameters. For the sake of practicality, not that
            "store.get_value(iter, COL_MODEL)" returns the object from the selected
            (double clicked) line (a models.PartOfSpeech model in this case)."""
        model = store.get_value(iter, COL_MODEL)
        cell.set_property('text', self.pos_tostring(model))

    def __render_root(self, layout, cell, store, iter):
        """Cell data function that renders a root word from it's model in
            the gtk.ListStore.
            
            See gtk.CellLayout.set_cell_data_func()'s documentation for
            description of parameters. For the sake of practicality, not that
            "store.get_value(iter, COL_MODEL)" returns the object from the selected
            (double clicked) line (a models.Root model in this case)."""
        model = store.get_value(iter, COL_MODEL)
        cell.set_property('text', self.root_tostring(model))
