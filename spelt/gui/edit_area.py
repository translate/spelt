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

import datetime
import gobject, gtk, gtk.glade

from common   import Configuration, exceptions, _
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

        self.config     = Configuration()
        self.current_sf = None
        self.glade_xml  = glade_xml
        self.gui        = gui
        self.langdb     = langdb
        self.wordlist   = wordlist

        self.wordlist.word_selected_handlers.append(self.on_surface_form_selected)
        self.__init_widgets()

    # METHODS #
    def check_pos_text(self, text=None):
        """If text was entered into cmb_pos, handle that text."""
        if text is None:
            text = self.cmb_pos.child.get_text()

        if not text:
            self.select_pos(None)
            self.cmb_pos.grab_focus()
            return

        shortcut, name = ('|' in text) and ( [substr.strip() for substr in text.split('|')] ) or ('_', text)
        # Search for POS on value and shortcut
        pos = self.langdb.find(section='parts_of_speech', name=name, shortcut=shortcut)

        if pos and len(pos) > 0:
            # NOTE: If more than one part of speech matches, we use the first one
            self.select_pos(pos[0])

            if pos[0].id != self.current_root.pos_id:
                self.set_sensitive(btn_add_root=True, btn_mod_root=True)
                self.set_visible(btn_ok=False, btn_add_root=True, btn_mod_root=True)
        else:
            # If we get here, we have a new part of speech
            self.select_pos(None)
            # Only create a new part of speech if the config says we are allowed:
            if not self.config.options['may_create_pos']:
                self.cmb_pos.grab_focus()
                return
            self.cmb_pos.child.set_text(text)
            self.current_pos = PartOfSpeech(name=name, shortcut=shortcut)

            # Determine which buttons should be shown/active
            if self.cmb_root.get_active() < 0:
                # If no existing root is selected, we have a new root and btn_mod_root should be hidden
                self.set_sensitive(btn_ok=False, btn_add_root=True, btn_mod_root=False)
                self.set_visible(btn_ok=False, btn_mod_root=False)
            else:
                # Otherwise, only the part of speech have change; show btn_{add,mod}_root
                self.set_sensitive(btn_ok=False, btn_add_root=True, btn_mod_root=True)
                self.set_visible(btn_ok=False, btn_add_root=True, btn_mod_root=True)

        # Select the focus to the first button in the list that is both visible and active
        for btn in (self.btn_ok, self.btn_add_root, self.btn_mod_root):
            if btn.get_property('visible') and btn.get_property('sensitive'):
                btn.grab_focus()

    def check_root_text(self, text=None):
        """If text was entered into cmb_root, handle that text."""
        if text is None:
            text = self.cmb_root.child.get_text()

        if not text:
            self.select_root(None)
            return

        # First check if the text in entry is that of an existing root:
        roots = self.langdb.find(section='roots', value=text)

        if roots and len(roots) > 0:
            # NOTE: If more than one root matches, we use the first one
            self.select_root(roots[0])
        else:
            # If we get here, we have a new root on our hands
            self.select_root(None) # Deselect root
            self.cmb_root.child.set_text(text)
            self.current_root = Root(
                value   = text,
                user_id = self.config.options['user_id'],
                date    = datetime.datetime.now()
            )
            self.select_pos(None)  # Deselect POS

            self.set_visible(btn_ok=False, btn_add_root=True)
            self.set_sensitive(cmb_pos=True, btn_add_root=False)

        self.cmb_pos.grab_focus()

    def on_surface_form_selected(self, sf):
        """A proxied event handler for when a surface form is selected in the
            word list.

            See the documentation of spelt.gui.WordList.word_selected_handlers for
            the use of this method."""
        if sf is None:
            self.lbl_word.set_markup('')
            self.select_root(None)
            self.set_sensitive(btn_reject=False, btn_ignore=False)
            self.set_visible(btn_ok=False)
            return

        self.current_sf = sf
        self.lbl_word.set_markup('<b>%s</b>' % sf.value)

        if self.langdb is None:
            return

        # Set GUI to its initial state
        self.set_sensitive(
            btn_reject=True,
            btn_ignore=True,
            btn_ok=True,
            btn_add_root=True,
            btn_mod_root=True,
            cmb_pos=True
        )
        self.set_visible(btn_ok=True, btn_add_root=False, btn_mod_root=False)

        if not sf.root_id:
            # sf does not have an associated root, so there's nothing to select
            # in the combo boxes.
            self.select_root(None)
        else:
            roots_found = self.langdb.find(id=sf.root_id, section='roots')
            # The roots_found list can have a maximum of 1 element, because we
            # search the database on ID's. ID's are guaranteed to be unique by the
            # models (via it's inheritence of IDModel).
            if roots_found:
                self.select_root(roots_found[0])
            else:
                raise exceptions.RootError(_( 'No root object found with ID %d' % (sf.root_id) ))

        self.cmb_root.grab_focus()

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
        if root is None:
            # Deselect root
            self.cmb_root.set_active(-1)
            self.cmb_root.child.set_text('')
            self.select_pos(None) # This deselects the part of speech too.
            self.set_sensitive(cmb_pos=False)
            return
        assert isinstance(root, Root)
        iter = self.root_store.get_iter_first()

        while self.root_store.iter_is_valid(iter):
            if self.root_store.get_value(iter, COL_MODEL) == root:
                self.cmb_root.set_active_iter(iter)
                self.current_root = root
                self.set_sensitive(cmb_pos=True)

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
        if pos is None:
            # Deselect POS
            self.cmb_pos.set_active(-1)
            self.cmb_pos.child.set_text('')
            return
        assert isinstance(pos, PartOfSpeech)
        iter = self.pos_store.get_iter_first()

        while self.pos_store.iter_is_valid(iter):
            if self.pos_store.get_value(iter, COL_MODEL) == pos:
                self.cmb_pos.set_active_iter(iter)
                self.current_pos = pos
                break

            iter = self.pos_store.iter_next(iter)

    def set_sensitive(self, **kwargs):
        """Set widgets' sensitivity based on keyword arguments.

            Example: "set_sensitive(cmb_pos=False) disables cmb_pos."""
        for widget, sensitive in kwargs.items():
            if hasattr(self, widget):
                getattr(self, widget).set_sensitive(sensitive)

    def set_visible(self, **kwargs):
        """Set widgets' visibility based on keyword arguments.

            Example: "set_visible(btn_ok=False)" will hide btn_ok."""
        for widget, visible in kwargs.items():
            if hasattr(self, widget):
                getattr(self, widget).set_property('visible', visible)

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
        self.cmb_pos.connect('changed', self.__on_cmb_changed, self.select_pos)
        self.cmb_root.connect('changed', self.__on_cmb_changed, self.select_root)
        # ComboBoxEntry's Entry
        self.cmb_pos.child.connect('activate', self.__on_entry_activated, self.check_pos_text)
        self.cmb_root.child.connect('activate', self.__on_entry_activated, self.check_root_text)
        # EntryCompletions
        self.pos_completion.connect('match-selected', self.__on_match_selected, self.cmb_pos, self.select_pos)
        self.root_completion.connect('match-selected', self.__on_match_selected, self.cmb_root, self.select_root)

    def __match_pos(self, completion, key, iter):
        model = self.pos_store.get_value(iter, COL_MODEL)
        if model is None:
            return False
        return model.shortcut.lower().startswith(key) or model.name.lower().startswith(key)

    def __match_root(self, completion, key, iter):
        model = self.root_store.get_value(iter, COL_MODEL)
        if model is None:
            return False
        return model.value.startswith(key)

    # GUI SIGNAL HANDLERS #
    def __on_btn_add_root_clicked(self, btn):
        """Add the current root to the language database."""
        if self.langdb.find(id=self.current_root.id, section='roots'):
            # The root already exists, so we have to duplicate it. It should have a different POS, though.
            self.current_root = Root(
                value   = self.current_root.value,
                user_id = self.config.options['user_id'],
                date    = datetime.datetime.now()
            )
        self.current_root.pos_id = self.current_pos.id
        self.langdb.add_root(self.current_root)

        if self.cmb_pos.get_active() < 0:
            self.langdb.add_part_of_speech(self.current_pos)

        self.refresh()

        # Update GUI
        self.set_sensitive(btn_ok=True, btn_add_root=False, btn_mod_root=False)
        self.set_visible(  btn_ok=True, btn_add_root=False, btn_mod_root=False)
        self.btn_ok.grab_focus()

    def __on_btn_ignore_clicked(self, btn):
        """Set the currently selected surface form's status to "ignored"."""
        if not self.current_sf:
            return

        self.current_sf.status = 'ignored'
        self.gui.reload_database()

    def __on_btn_mod_root_clicked(self, btn):
        """Update the current root with the selected part of speech."""
        if self.cmb_pos.get_active() < 0:
            self.langdb.add_part_of_speech(self.current_pos)

        self.current_root.date    = datetime.datetime.now()
        self.current_root.pos_id  = self.current_pos.id
        self.current_root.user_id = self.config.options['user_id']

        self.refresh()

        # Update GUI
        self.set_sensitive(btn_ok=True, btn_add_root=False, btn_mod_root=False)
        self.set_visible(  btn_ok=True, btn_add_root=False, btn_mod_root=False)
        self.btn_ok.grab_focus()

    def __on_btn_ok_clicked(self, btn):
        """Save changes made to the selected surface form, save it and move on
            to the next one."""
        root = None
        pos  = None

        if self.current_sf.root_id != self.current_root.id:
            self.current_sf.root_id = self.current_root.id
            self.current_sf.user_id = self.config.options['user_id']

        self.current_sf.status  = 'classified'
        self.current_sf.date    = datetime.datetime.now()

        self.wordlist.refresh() # This will select the next word at the top of the word list

    def __on_btn_reject_clicked(self, btn):
        """Set the currently selected surface form's status to "rejected"."""
        if not self.current_sf:
            return

        self.current_sf.status = 'rejected'
        self.gui.reload_database()

    def __on_cmb_changed(self, combo, select_model):
        """Handler for the "changed" event of a gtk.ComboBox.

            @type  select_model: function
            @param select_model: The model that should handle the selection of
                the new model."""
        iter = combo.get_active_iter()

        if not iter is None:
            model = combo.get_model().get_value(iter, COL_MODEL)
            select_model(model)

    def __on_match_selected(self, completion, store, iter, combo, select_model):
        """Handler for the "match-selected" event of ComboBoxEntries'
            EntryCompletions.

            See the PyGtk API documentation for the definition of the first 3
            parameters. It should be obvious, though.
            @type  combo: gtk.ComboBoxEntry
            @param combo: The combo box for which a match was selected.
            @type  select_model: function
            @param select_model: The function to which the selected model
                should be passed to handle its selection."""
        child_iter = store.convert_iter_to_child_iter(iter)
        model = combo.get_model().get_value(child_iter, COL_MODEL)
        select_model(model)

        return True

    def __on_entry_activated(self, entry, text_handler):
        """Handler for the "activated" event of a gtk.Entry.

            It is used here for the child Entries of the ComboBoxEntries.
            @type  text_handler: function
            @param text_handler: The function that will handle the text entered."""
        text_handler(entry.get_text())

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
