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

"""Contains the Menu class which handles menu selections."""

import gtk, gtk.glade
import os

from common import Configuration, _
from models import Source, SurfaceForm

class Menu(object):
    """
    Class that handles menu options and selections.
    """

    # CONSTRUCTOR #
    def __init__(self, glade_xml, gui):
        """Constructor.
            @type  glade_xml: gtk.glade.XML
            @param glade_xml: The Glade XML object to load widgets from.
            """
        assert isinstance(glade_xml, gtk.glade.XML)
        assert not gui is None

        self.config    = Configuration()
        self.glade_xml = glade_xml
        self.gui       = gui

        self.__init_widgets()

    # METHODS #
    def create_source_from_file(self, filename):
        """Create a model.Source for the given filename."""
        fname = os.path.split(filename)[1]
        self.gui.dlg_source.run(fname)
        name = self.gui.dlg_source.name
        desc = self.gui.dlg_source.description
        import_user_id = self.config.options['user_id']

        print 'Before now source'
        src = Source(name=name, filename=fname, desc=desc, import_user_id=import_user_id)
        print "New source's ID: %d" % (src.id)
        return src

    def __init_widgets(self):
        """Get and initialize widgets from the Glade object."""
        self.widgets = (
            # File menu
            'mnu_open',
            'mnu_save',
            'mnu_saveas',
            'mnu_quit',
            # Database menu
            'mnu_emaildb',
            'mnu_import',
            'mnu_roots',
            # Help menu
            'mnu_about'
        )

        for widget_name in self.widgets:
            widget = self.glade_xml.get_widget(widget_name)
            widget.connect('activate', self.__on_item_activated)
            setattr(self, widget_name, widget)

    # SIGNAL HANDLERS #
    def handler_open(self):
        """Display an "Open" dialog and try to open the file as a language database."""
        filename = self.gui.get_open_filename()
        if filename is None:
            return

        if not os.path.exists(filename):
            self.gui.show_error(_( 'File does not exist: %s' % (filename) ))
            return

        try:
            self.config.options['current_database'].load(filename=filename)
        except exc:
            self.gui.show_error(_( 'Error load database from %s' % (filename) ))
            print _( 'Error loading database from %s: %s' % (filename, str(exc)) )
            return

        # Ask the main GUI object to reload the database everywhere...
        self.gui.reload_database()

    def handler_save(self):
        """Save the contents of the current open database."""
        try:
            self.config.options['current_database'].save()
        except exc:
            self.gui.show_error(_('Error saving database!'))
            print _( 'Error saving database: %s' % (exc) )
            return

    def handler_saveas(self):
        """Display a "Save as" dialog and try to save the language database to
            the selected file."""
        filename = self.gui.get_save_filename()
        if filename is None:
            return

        if os.path.exists(filename) and not self.gui.prompt(_( 'File %s already exists.\n\nOverwrite?' % (filename) )):
            return

        try:
            self.config.options['current_database'].save(filename)
        except exc:
            self.gui.show_error('Error saving database to file %s!' % (filename))
            print 'Error saving database to %s: %s' % (filename, exc)

    def handler_quit(self):
        """Quit the application after confirmation."""
        if self.gui.prompt(_('Are you sure you want to quit?')):
            self.gui.quit()

    def handler_emaildb(self):
        db = self.config.options['current_database']

        try:
            db.save()
        except exc:
            self.gui.show_error(_('Unable to save database before e-mailing!'))
            print _( 'Unable to save database before e-mailing: %s' % (exc) )
            return

        subj = _('Language database: ') + str(db)
        os.system('xdg-email --utf8 --subject "%s" --attach "%s"' % (subj, db.filename))
        # FIXME: The above line does not attach the file as expected (Linux/Thunderbird)!

    def handler_import(self):
        """Import words from a text file."""
        db = self.config.options['current_database']
        user_id = self.config.options['user_id']
        filename = self.gui.get_open_filename(_('Open word list...'))

        if filename is None:
            return

        src = self.create_source_from_file(filename)
        db.add_source(src)

        f = open(filename, 'r')
        line = f.readline()

        while line:
            # Ignore comments:
            if line.lstrip().startswith('#'):
                continue

            word = line.rstrip()
            print ('Word: %s' % word),

            # Make sure we don't add a word that already exists:
            if db.find(section='surface_forms', value=word):
                line = f.readline()
                continue

            print '(A)'

            db.add_surface_form(
                SurfaceForm(value=word, status='todo', user_id=user_id, source_id=src.id)
            )
            line = f.readline()

        f.close()

    def handler_roots(self):
        """Show the root management window/dialog. NOT YET IMPLEMENTED!"""
        # TODO: Implement this method
        self.gui.show_error(_('This functionality is not yet implemented.'))

    def __on_item_activated(self, menu_item):
        """Signal handler for all menu items."""
        if not menu_item.name.startswith('mnu_'):
            return

        # The following looks up the appropriate signal handler for a menu item
        # by changing the leading 'mnu_' of the menu item's name to 'handler_'.
        # ie. 'mnu_save' becomes 'handler_save', which is called with no arguments.
        handler_name = 'handler_%s' % (menu_item.name[4:])
        getattr(self, handler_name)()
