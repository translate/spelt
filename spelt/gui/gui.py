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

"""Contains the main GUI class."""

# External imports
import gtk, gtk.glade

# Other sub-modules
from common   import Configuration, _
from models   import LanguageDB

# From the gui package
from dlg_source import DlgSource
from edit_area  import EditArea
from menu       import Menu
from wordlist   import WordList


class GUI(object):
    """The main GUI class. Also contains commonly used functionality."""

    # CONSTRUCTOR #
    def __init__(self):
        self.glade = gtk.glade.XML('../share/spelt/spelt.glade')
        self.config = Configuration()

        # FIXME: The following values for the configuration is only for use
        # until the Configuration class gets some functionality.
        self.config.options['previous_database_path'] = 'test_langdb.xldb'
        self.config.options['user_id'] = 999

        # Main window
        self.main_window = self.glade.get_widget('wnd_main')
        self.main_window.connect('destroy', lambda *w: gtk.main_quit())

        # Load last database
        db = LanguageDB(lang='')
        self.config.options['current_database'] = db

        if self.config.options.has_key('previous_database_path'):
            db.load(self.config.options['previous_database_path'])

        # Initialize other GUI components
        self.__create_dialogs()
        self.menu      = Menu(self.glade, gui=self)
        self.word_list = WordList(self.glade, langdb=db, gui=self)
        self.edit_area = EditArea(self.glade, self.word_list, langdb=db, gui=self)

        self.main_window.show_all()

    def __del__(self):
        """Destructor."""
        self.open_chooser.destroy()
        self.save_chooser.destroy()

    # METHODS #
    def __create_dialogs(self):
        self.open_chooser = gtk.FileChooserDialog(
            title=_('Select language database to open'),
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,gtk.RESPONSE_OK)
        )

        self.save_chooser = gtk.FileChooserDialog(
            title=_('Save as...'),
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,gtk.RESPONSE_OK)
        )

        filter = gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern('*')

        self.open_chooser.add_filter(filter)
        self.save_chooser.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name(_('Language Databases'))
        filter.add_mime_type('text/xml')
        filter.add_pattern('*.' + LanguageDB.FILE_EXTENSION)

        self.open_chooser.add_filter(filter)
        self.save_chooser.add_filter(filter)

        # Message dialog
        self.dlg_error = gtk.MessageDialog(
            parent=self.main_window,
            flags=gtk.DIALOG_MODAL,
            type=gtk.MESSAGE_ERROR,
            buttons=gtk.BUTTONS_OK,
            message_format=''
        )

        self.dlg_info = gtk.MessageDialog(
            parent=self.main_window,
            flags=gtk.DIALOG_MODAL,
            type=gtk.MESSAGE_INFO,
            buttons=gtk.BUTTONS_OK,
            message_format=''
        )

        self.dlg_prompt = gtk.MessageDialog(
            parent=self.main_window,
            flags=gtk.DIALOG_MODAL,
            type=gtk.MESSAGE_QUESTION,
            buttons=gtk.BUTTONS_YES_NO,
            message_format=''
        )

        # Source dialog wrapper
        self.dlg_source = DlgSource(self.glade)

    def get_open_filename(self, title=_('Select language database to open')):
        """Display an "Open" dialog and return the selected file.
            @rtype  str
            @return The filename selected in the "Open" dialog. None if the selection was cancelled."""
        self.open_chooser.set_title(title)
        res = self.open_chooser.run()
        self.open_chooser.hide()

        if res != gtk.RESPONSE_OK:
            return None

        return self.open_chooser.get_filename()

    def get_save_filename(self, title=_('Select language database to open')):
        """Display an "Save" dialog and return the selected file.
            @rtype  str
            @return The filename selected in the "Save" dialog. None if the selection was cancelled."""
        res = self.save_chooser.run()
        self.save_chooser.hide()

        if res != gtk.RESPONSE_OK:
            return None

        return self.save_chooser.get_filename()

    def show_error(self, text, title=_('Error!')):
        self.dlg_error.set_markup(text)
        self.dlg_error.set_title(title)
        self.dlg_error.run()
        self.dlg_error.hide()

    def show_info(self, text, title=_('Information')):
        self.dlg_info.set_markup(text)
        self.dlg_info.set_title(title)
        self.dlg_info.run()
        self.dlg_info.hide()

    def prompt(self, text, title=_('Prompt')):
        self.dlg_prompt.set_markup(text)
        self.dlg_prompt.set_title(title)
        res = self.dlg_prompt.run()
        self.dlg_prompt.hide()

        return res == gtk.RESPONSE_YES

    def quit(self):
        # TODO: self.config.save()
        gtk.main_quit()

    def reload_database(self):
        """Have all sub-components reload its database information."""
        db = self.config.options['current_database']
        self.edit_area.refresh(langdb=db)
        self.word_list.refresh(langdb=db)
