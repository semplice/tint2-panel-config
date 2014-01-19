#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# tint2-panel-config - Simple GUI to tweak the panel
# Copyright (C) 2013 Eugenio "g7" Paolantonio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# This is the distutils-based installation program.
#

from distutils.core import setup

setup(name='tint2-panel-config',
	version='1.0.6',
	description='Simple GUI to tweak the panel',
	author='Eugenio Paolantonio',
	author_email='me@medesimo.eu',
	url='http://github.com/semplice/tint2-panel-config',
	# package_dir={'bin':''},
	scripts=['tint2-panel-config.py'],
	data_files=[("/usr/share/tint2-panel-config", ["tint2-panel-config.glade"]), ("/usr/share/applications", ["tint2-panel-config.desktop"])],
	requires=['gi.repository.Gtk', 'gi.repository.GObject', 'gi.repository.GMenu', 'gi.repository.Gio', 'quickstart', 'os', 'xdg.DesktopEntry'],
)
