#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# tint2-panel-config - Simple GUI to tweak the panel
# Copyright (C) 2013  Eugenio "g7" Paolantonio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from gi.repository import Gtk, GMenu, GObject, Gio
import quickstart
import os
import xdg.DesktopEntry

CONFIG = os.path.expanduser("~/.config/tint2/secondary_config")

tr = quickstart.translations.Translation("tint2-panel-config")
tr.install()
tr.bind_also_locale()

GLADEFILE = "./tint2-panel-config.glade"
if not os.path.exists(GLADEFILE):
	# Fallback to /usr/share/tint2-panel-config
	GLADEFILE = "/usr/share/tint2-panel-config/tint2-panel-config.glade"

@quickstart.builder.from_file(GLADEFILE)
class GUI:
	
	tree = None
	
	events = {
		"destroy" : (
			"main",
		),
		"delete-event" : (
			"add_launcher",
		),
		"toggled" : (
			"enabled_checkbox",
		),
		"clicked" : (
			"add_button",
			"remove_button",
			"launcher_ok_button",
			"launcher_cancel_button",
			"close_button",
		),
		"cursor-changed" : (
			"enabled_treeview",
			"launcher_add_treeview",
		)
	}
	
	def menu_iterate(self, directory, menu_iter=None, create_menu_iter=False, skip=None):
		""" Iterates through the menu entries and adds them to the launcher_add_treeview. """
		
		if not directory: return
		if not skip: skip = ()
		directory_iter = directory.iter()
		_next = directory_iter.next()

		if create_menu_iter:
			menu_iter = self.launcher_add_model.append(None, (directory.get_name(), None, directory.get_icon()))

		while _next != GMenu.TreeItemType.INVALID:
			_current = _next
			_next = directory_iter.next()
			
			if _current == GMenu.TreeItemType.DIRECTORY:
				dire = directory_iter.get_directory()
				if not dire or dire.get_menu_id() in skip:
					continue
				
				_menu_iter = self.launcher_add_model.append(menu_iter, (dire.get_name(), None, dire.get_icon()))
				self.menu_iterate(directory_iter.get_directory(), _menu_iter, skip=skip)
			elif _current == GMenu.TreeItemType.ENTRY:
				child = directory_iter.get_entry()
				info = child.get_app_info()
				#print info.get_icon()
				
				self.launcher_add_model.append(
					menu_iter,
					(
						info.get_name(),
						child.get_desktop_file_path(),
						info.get_icon()
					)
				)
				#print child.get_app_info().get_name(), child.get_desktop_file_path()

	def on_enabled_treeview_cursor_changed(self, treeview):
		""" Fired when the user changed something on the enabled_treeview. """
		
		# Enable remove button
		GObject.idle_add(self.objects["remove_button"].set_sensitive, True)

	def on_launcher_add_treeview_cursor_changed(self, treeview):
		""" Fired when the user changed something on the launcher_add_treeview. """
		
		# Get selection
		selection = self.objects["launcher_add_treeview"].get_selection()
		model, treeiter = selection.get_selected()
		
		if not treeiter or model[treeiter][1] == None:
			# no .desktop, this is a Category.
			GObject.idle_add(self.objects["launcher_ok_button"].set_sensitive, False)
		else:
			# Application.
			GObject.idle_add(self.objects["launcher_ok_button"].set_sensitive, True)
	
	@quickstart.threads.thread
	def build_application_list(self):
		""" Builds the application list. """
		
		self.tree = GObject.new(GMenu.Tree, menu_basename="semplice-applications.menu",) #flags=GMenu.TreeFlags.SORT_DISPLAY_NAME)
		self.tree.load_sync()
				
		# Create store
		self.launcher_add_model = Gtk.TreeStore(str, str, Gio.Icon)
		# And link the TreeView to it...
		self.objects["launcher_add_treeview"].set_model(self.launcher_add_model)

		# Column
		column = Gtk.TreeViewColumn("Everything")
		
		# Icon
		cell_icon = Gtk.CellRendererPixbuf()
		column.pack_start(cell_icon, False)
		column.add_attribute(cell_icon, "gicon", 2)

		# Text
		cell_text = Gtk.CellRendererText()
		column.pack_start(cell_text, False)
		column.add_attribute(cell_text, "text", 0)
		
		# Append
		self.objects["launcher_add_treeview"].append_column(column)		
		
		GObject.idle_add(self.menu_iterate, self.tree.get_root_directory(), None, None, ("Preferences", "Administration"))		
		GObject.idle_add(self.menu_iterate, self.tree.get_directory_from_path("/System/Preferences"), None, True)
		GObject.idle_add(self.menu_iterate, self.tree.get_directory_from_path("/System/Administration"), None, True)
		
		GObject.idle_add(self.objects["launcher_add_treeview"].expand_all)
		
		# First start, disable OK button.
		GObject.idle_add(self.objects["launcher_ok_button"].set_sensitive, False)
	
	def on_add_button_clicked(self, button):
		""" Fired when the Add launcher button has been clicked. """
		
		#self.objects["add_launcher"].show_all()
		
		if not self.tree: self.build_application_list()
		
		GObject.idle_add(self.objects["add_launcher"].show_all)
	
	def on_remove_button_clicked(self, button):
		""" Fired when the Remove launcher button has been clicked. """
		
		# Get selection
		selection = self.objects["enabled_treeview"].get_selection()
		model, treeiter = selection.get_selected()
		
		del model[treeiter]
		
		# Disable remove button if we should
		if len(model) == 0: GObject.idle_add(self.objects["remove_button"].set_sensitive, False)
	
	def on_launcher_ok_button_clicked(self, button):
		""" Fired when the OK button in the add_launcher window has been clicked. """
		
		self.objects["add_launcher"].hide()
		
		# Get selection
		selection = self.objects["launcher_add_treeview"].get_selection()
		model, treeiter = selection.get_selected()
		
		self.enabled_model.append((model[treeiter][0], model[treeiter][1], model[treeiter][2]))
	
	def on_launcher_cancel_button_clicked(self, button):
		""" Fired when the Cancel button in the add_launcher window has been clicked. """
		
		self.objects["add_launcher"].hide()
	
	def on_close_button_clicked(self, button):
		""" Fired when the close button has been clicked. """
		
		settings = Gtk.Settings.get_default()
		icon_theme = settings.get_property("gtk-icon-theme-name")
		
		with open(CONFIG, "w") as f:
			if self.objects["ampm_enabled"].get_active():
				f.write("time1_format = %I:%M %p\n")
			if self.objects["enabled_checkbox"].get_active():
				f.write("panel_items = LTSBC\n")
			else:
				f.write("panel_items = TSBC\n")
			f.write("launcher_icon_theme = %s\n" % icon_theme)
			for treeiter in self.enabled_model:
				f.write("launcher_item_app = %s\n" % treeiter[1])				
		
		os.system("killall -SIGUSR1 tint2")
		
		# FIXME (not here, in tint2): when running tint2 with compton,
		# when the panel restarts the user will see icons with white
		# backgrounds and other issues.
		# To fix this we need to restart compositing		
		if os.path.exists(os.path.expanduser("~/.config/.composite_enabled")):
			os.system("pkill compton")
			os.system("compton -b")
		
		Gtk.main_quit()
	
	def on_main_destroy(self, window):
		""" Fired when the main window should be destroyed. """
		
		Gtk.main_quit()
	
	def on_add_launcher_delete_event(self, window, etc):
		""" Fired when the add launcher window should be destroyed. """
		
		window.hide()
		return True
	
	def on_enabled_checkbox_toggled(self, checkbox):
		""" Fired when the enabled checkbox has been toggled. """
		
		if checkbox.get_active():
			GObject.idle_add(self.objects["enabled_box"].set_sensitive, True)
		else:
			GObject.idle_add(self.objects["enabled_box"].set_sensitive, False)
	
	@quickstart.threads.thread
	def initialize(self):
		""" Builds the enabled list. """
		
		# Set-up the enabled_treeview
		self.enabled_model = Gtk.ListStore(str, str, Gio.Icon)
		# Link the treeview
		self.objects["enabled_treeview"].set_model(self.enabled_model)
		
		# Column
		column = Gtk.TreeViewColumn("Everything")
		
		# Icon
		cell_icon = Gtk.CellRendererPixbuf()
		column.pack_start(cell_icon, False)
		column.add_attribute(cell_icon, "gicon", 2)

		# Text
		cell_text = Gtk.CellRendererText()
		column.pack_start(cell_text, False)
		column.add_attribute(cell_text, "text", 0)
		
		# Append
		self.objects["enabled_treeview"].append_column(column)

		# Open config
		with open(CONFIG) as f:
			for line in f.readlines():
				line = line.split("=")
				if line[0].startswith("launcher_item_app"):
					# A launcher!
					path = line[1].strip("\n").replace(" /","/",1)
					desktopentry = xdg.DesktopEntry.DesktopEntry(path)
					iconpath = desktopentry.getIcon()
					if iconpath and iconpath.startswith("/"):
						icon = Gio.Icon.new_for_string(iconpath)
					elif iconpath:
						icon = Gio.ThemedIcon()
						icon.append_name(iconpath.replace(".png",""))
					else:
						icon = None
					self.enabled_model.append((desktopentry.getName(), path, icon))
				elif line[0].startswith("panel_items"):
					# Is the launcher enabled or not?
					if "L" in line[1]:
						# YES!
						self.objects["enabled_checkbox"].set_active(True)
					else:
						# No :/
						GObject.idle_add(self.objects["enabled_box"].set_sensitive, False)
				elif line[0].startswith("time1_format"):
					# AM/PM?
					if "%p" in line[1]:
						# Yes!
						self.objects["ampm_enabled"].set_active(True)
					else:
						# No
						self.objects["ampm_enabled"].set_active(False)

		# First start, disable remove button.
		if len(self.enabled_model) == 0: GObject.idle_add(self.objects["remove_button"].set_sensitive, False)

	
	def __init__(self):
		""" Initialize the GUI. """
		
		self.initialize()
		
		self.objects["main"].show_all()
		
quickstart.common.quickstart(GUI)
