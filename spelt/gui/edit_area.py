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

from models import LanguageDB, PartOfSpeech, Root, SurfaceForm
from wordlist import WordList

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

        self.glade_xml = glade_xml
        self.gui       = gui
        self.langdb    = langdb
        self.word_list = word_list
        self.word_list.word_selected_handlers.append(self.on_surface_form_selected)
        self.__init_widgets()

    # METHODS #
    def on_surface_form_selected(self, sf):
        self.lbl_word.set_markup('<b>%s</b>' % sf.value)

        if self.langdb is None:
            return

        res = self.langdb.find(id=sf.root_id, section='roots')

        if res:
            pass

    def refresh(self, langdb=None):
        """Reload data from self.langdb database."""
        if not langdb is None and isinstance(langdb, LanguageDB):
            self.langdb = langdb

        if not self.langdb or not isinstance(self.langdb, LanguageDB):
            return

        self.pos_store.clear()
        self.root_store.clear()
        [self.pos_store.append([model]) for model in self.langdb.parts_of_speech]
        [self.root_store.append([model]) for model in self.langdb.roots]

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
        self.pos_store = gtk.ListStore(gobject.TYPE_PYOBJECT)
        self.cmb_pos.clear()
        self.cmb_pos.pack_start(pos_cell)
        self.cmb_pos.set_cell_data_func(pos_cell, self.__render_pos)
        self.cmb_pos.set_model(self.pos_store)
        self.cmb_pos.connect('changed', self.__on_cmb_pos_changed)

        root_cell = gtk.CellRendererText()
        self.root_store = gtk.ListStore(gobject.TYPE_PYOBJECT)
        self.cmb_root.clear()
        self.cmb_root.pack_start(root_cell)
        self.cmb_root.set_cell_data_func(root_cell, self.__render_root)
        self.cmb_root.set_model(self.root_store)
        self.cmb_root.connect('changed', self.__on_cmb_root_changed)

        # Setup autocompletion
        pos_cell = gtk.CellRendererText()
        pos_completion = gtk.EntryCompletion()
        pos_completion.clear()
        pos_completion.pack_start(pos_cell)
        pos_completion.set_cell_data_func(pos_cell, self.__render_pos)
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

    def __on_match_selected(self, completion, store, iter, combo):
        # FIXME: This method still doesn't work after various attempts.
        # combo.set_active_iter(store.convert_iter_to_child_iter(iter)) should
        # work, but doesn't.
        pass

    def __on_cmb_pos_changed(self, cmb):
        iter = cmb.get_active_iter()
        if iter is None: return
        model = cmb.get_model().get_value(iter, 0)
        pos_text = '%s | %s' % (model.shortcut, model.name)
        cmb.child.set_text( pos_text )

    def __on_cmb_root_changed(self, cmb):
        iter = cmb.get_active_iter()
        if iter is None: return
        model = cmb.get_model().get_value(iter, 0)
        cmb.child.set_text( model.value )

    def __render_pos(self, layout, cell, store, iter):
        """Cell data function that renders a part-of-speech from it's model in
            the gtk.ListStore.
            
            See gtk.CellLayout.set_cell_data_func()'s documentation for
            description of parameters. For the sake of practicality, not that
            "store.get_value(iter, 0)" returns the object from the selected
            (double clicked) line (a models.PartOfSpeech model in this case)."""
        model = store.get_value(iter, 0)
        if model is None: return
        pos_text = '%s | %s' % (model.shortcut, model.name)
        cell.set_property('text', pos_text)

    def __render_root(self, layout, cell, store, iter):
        """Cell data function that renders a root word from it's model in
            the gtk.ListStore.
            
            See gtk.CellLayout.set_cell_data_func()'s documentation for
            description of parameters. For the sake of practicality, not that
            "store.get_value(iter, 0)" returns the object from the selected
            (double clicked) line (a models.Root model in this case)."""
        model = store.get_value(iter, 0)
        if model is None: return
        cell.set_property('text', model.value)

    def __match_pos(self, completion, key, iter):
        model = self.pos_store.get_value(iter, 0)
        return model.shortcut.startswith(key) or model.name.startswith(key)

    def __match_root(self, completion, key, iter):
        model = self.root_store.get_value(iter, 0)
        return model.value.startswith(key)
