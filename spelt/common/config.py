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

"""Contains the Configuration class."""

from singleton import SingletonMeta

class Configuration(object):
    """Singleton access to the program's configuration."""

    __metaclass__ = SingletonMeta # Make this a Singleton class

    def __init__(self, configFilename='config.prefs'):
        self.options = {}

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.options)
