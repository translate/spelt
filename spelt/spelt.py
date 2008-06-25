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

import gtk
import os

from gui    import GUI
from common import _

GLADE_DIRS = [
    ['..',    'share', 'spelt'], # TODO: Check if both are necessary
    ['share', 'spelt']
]

class Spelt(object):
    """Main entry point for Spelt."""
    def __init__(self, basepath):
        """Creates a gui.GUI object."""
        self.gui = GUI(self.find_glade(basepath, 'spelt.glade'))

    def find_glade(self, basepath, glade_filename):
        """This method is based on the load_glade_file() function in VirTaal's virtaal/main_window.py."""
        for glade_dir in GLADE_DIRS:
            path = glade_dir + [glade_filename]
            file = os.path.join(basepath or os.path.dirname(__file__), *path)

            if os.path.exists(file):
                return file

        raise Exception(_('Could not find Glade file: ') + glade_filename)

    def run(self):
        """Calls gtk.main()"""
        gtk.main()
