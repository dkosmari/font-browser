#!/bin/env python3
import sys
import os
import gettext
import locale
import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gdk,\
                          GLib,\
                          Gio,\
                          Gtk,\
                          Pango,\
                          PangoCairo


bin_location = os.path.dirname(os.path.realpath(__file__))

locale_dir = "@localedir@"
pkg_data_dir = "@pkgdatadir@"
if locale_dir.startswith("@"):
    locale_dir = bin_location + "/locale"
if pkg_data_dir.startswith("@"):
    pkg_data_dir = bin_location


application_id = "org.example.font-browser"
application_name = "font-browser"


locale.bindtextdomain(application_name, locale_dir)
gettext.install(application_name, locale_dir)



# column IDs for fonts_list
FONTS_LIST_COL_FONT_FAMILY_NAME = 0
FONTS_LIST_COL_FONT_FAMILY = 1
FONTS_LIST_COL_SELECTED = 2

# column IDs for comp_list
COMP_LIST_COL_FONT_FAMILY_NAME = 0


# TODO: add "show font info" context menu entry


# helper class to bind all named GUI components
class GUI:
    def __init__(self, builder):
        objects = builder.get_objects()
        for obj in objects:
            try:
                name = Gtk.Buildable.get_name(obj)
                if name is not None and not name.startswith("___"):
                    #print("named:", name)
                    self.__setattr__(name, obj)
            except:
                #print("not buildable:", obj)
                pass # just ignore things that aren't Gtk.Buildable

    def add(self, builder, name):
        self.__setattr__(name, builder.get_object(name))



class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id=application_id,
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        GLib.set_application_name(_("Font Browser"))
        GLib.set_prgname(application_id)
        Gtk.Window.set_default_icon_name(application_id)

        self.gui = None
        self.show_only_selected = False
        self.search_tokens = []
        self.selected_font_name = ""
        self.font_reloader_source = None # source for idle callback to load fonts

        resource = Gio.Resource.load(pkg_data_dir + "/font-browser.gresource")
        Gio.resources_register(resource)



    def do_startup(self):
        Gtk.Application.do_startup(self)

        builder = Gtk.Builder.new_from_resource(
            self.get_resource_base_path() + "/font-browser.glade")
        builder.connect_signals(self)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)


        # put all named glade objects into self.gui
        self.gui = GUI(builder)
        # some don't work because they're not Gtk.Buildable
        self.gui.add(builder, "fonts_select_cell")
        self.gui.add(builder, "fonts_name_cell")
        self.gui.add(builder, "fonts_sample_cell")
        self.gui.add(builder, "fonts_list_filter")
        self.gui.add(builder, "comp_text_cell")


        self.gui.about_dialog.add_button(_("Close"), Gtk.ResponseType.CLOSE)

        # sets custom filtering function
        self.gui.fonts_list_filter.set_visible_func(self.filter_visible_fonts)

        self.gui.fonts_context_menu.attach_to_widget(self.gui.fonts_tree_view)

        self.reload_fonts()
        # call once to keep in sync
        self.on_sample_text_entry_changed(self.gui.sample_text_entry)
        self.on_sample_scale_spin_changed(self.gui.sample_scale_spin)
        self.on_comp_text_entry_changed(self.gui.comp_text_entry)
        self.on_comp_size_spin_changed(self.gui.comp_size_spin)

        self.clear_all_test_labels()


    def do_activate(self):
        self.gui.main_window.set_application(self)
        self.gui.main_window.present()


    def clear_all_test_labels(self):
        self.gui.comp_list.clear()


    def reload_fonts(self):
        # cancel the idle font reload callback, if it's running
        if self.font_reloader_source is not None:
            GLib.source_remove(self.font_reloader_source)
            self.font_reloader_source = None

        self.gui.fonts_list.clear()
        self.clear_all_test_labels()
        # ask PangoCairo for the fonts
        font_map = PangoCairo.font_map_get_default()
        families = font_map.list_families()
        families.sort(key=lambda x: x.get_name().lower())
        self.font_reloader_source = GLib.idle_add(self.reload_fonts_idle, families)


    def reload_fonts_idle(self, families):
        if len(families) == 0:
            # processed everything
            self.gui.fonts_tree_view.columns_autosize()
            self.font_reloader_source = None
            return False
        fam = families.pop(0)
        self.gui.fonts_list.append([fam.get_name(), fam, False])
        return True


    def refilter(self):
        self.gui.fonts_list_filter.refilter()


    def filter_visible_fonts(self, model, iter, data):
        row = model[iter]
        if self.show_only_selected:
            if not row[FONTS_LIST_COL_SELECTED]:
                return False
        return self.filter_if_search_match(row)


    def filter_if_search_match(self, row):
        if not self.search_tokens:
            return True
        haystack = row[FONTS_LIST_COL_FONT_FAMILY_NAME].lower()
        assert isinstance(haystack, str)
        # every token must exist somewhere in the font name
        for needle in self.search_tokens:
            if haystack.find(needle) == -1:
                return False
        return True


    def fonts_context_popup(self):
        self.font_list_context_menu.popup()


    def append_comparison(self, font_family_name):
        self.gui.comp_list.append([font_family_name])


    def remove_comparison(self, font_family_name):
        to_remove = None
        for row in self.gui.comp_list:
            if row[COMP_LIST_COL_FONT_FAMILY_NAME] == font_family_name:
                to_remove = self.gui.comp_list.get_iter(row.path)
        if to_remove is not None:
            self.gui.comp_list.remove(to_remove)


    def toggle_font_selection(self, row):
        newval = not row[FONTS_LIST_COL_SELECTED]
        font_family_name = row[FONTS_LIST_COL_FONT_FAMILY_NAME]
        row[FONTS_LIST_COL_SELECTED] = newval
        if newval:
            self.append_comparison(font_family_name)
        else:
            self.remove_comparison(font_family_name)


    def do_fonts_popup_menu(self, event, is_pointer):
        sel = self.gui.fonts_tree_view.get_selection()
        model, iter = sel.get_selected()
        if model is None or iter is None:
            return False
        row = model[iter]
        self.selected_font_name = row[FONTS_LIST_COL_FONT_FAMILY_NAME]
        label = _('Copy "{}" to clipboard').format(self.selected_font_name)
        self.gui.copy_font_name_entry.set_label(label)

        if event is not None:
            event_time = event.get_time()
            button = event.button
        else:
            event_time = Gtk.get_current_event_time()
            button = 0

        if is_pointer:
            self.gui.fonts_context_menu.popup_at_pointer(event)
        else:
            self.gui.fonts_context_menu.popup_at_widget(self.gui.fonts_tree_view,
                                                        Gdk.Gravity.NORTH_WEST,
                                                        Gdk.Gravity.NORTH_WEST,
                                                        event)
        return True



    ##################
    # Event handlers #
    ##################

    def on_quit(self, action, param):
        self.quit()


    def on_about(self, action, param):
        self.gui.about_dialog.run()
        self.gui.about_dialog.hide()


    def on_sample_text_entry_changed(self, editable: Gtk.Entry) -> None:
        text = editable.get_text()
        self.gui.fonts_sample_cell.set_property("text", text)
        self.gui.fonts_sample_column.queue_resize()


    def on_sample_scale_spin_changed(self, spin: Gtk.SpinButton):
        scale = spin.get_value()
        self.gui.fonts_sample_cell.set_property("scale", scale)
        self.gui.fonts_sample_column.queue_resize()


    def on_only_selected_switch_state_set(self, switch: Gtk.Switch, new_value):
        self.show_only_selected = new_value
        self.refilter()
        return False # False means "don't stop normal behavior"


    def on_filter_entry_search_changed(self, entry: Gtk.SearchEntry):
        search_text = entry.get_text().lower()
        self.search_tokens = search_text.split()
        self.refilter()


    def on_refresh_fonts_button_clicked(self, button: Gtk.Button):
        self.reload_fonts()


    def on_fonts_tree_view_row_activated(self, tree_view, path, column):
        self.toggle_font_selection(tree_view.get_model()[path])


    # handle right-click context menu
    def on_fonts_tree_view_button_press_event(self, widget, event : Gdk.EventButton):
        if event.triggers_context_menu() and event.type == Gdk.EventType.BUTTON_PRESS:
            return self.do_fonts_popup_menu(event, True)
        return False


    def on_fonts_tree_view_popup_menu(self, widget):
        return self.do_fonts_popup_menu(None, True)


    def on_comp_text_entry_changed(self, editable: Gtk.Editable):
        text = editable.get_text()
        self.gui.comp_text_cell.set_property("text", text)
        self.gui.comp_text_column.queue_resize()


    def on_comp_size_spin_changed(self, spin):
        size = spin.get_value()
        self.gui.comp_text_cell.set_property("size-points", size)
        self.gui.comp_text_column.queue_resize()


    def on_copy_font_name_entry_activate(self, menu_item):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.selected_font_name, -1)


    def on_bold_toggle_toggled(self, button: Gtk.ToggleButton):
        active = button.get_active()
        if active:
            w = Pango.Weight.BOLD
        else:
            w = Pango.Weight.NORMAL
        self.gui.comp_text_cell.set_property("weight", w)
        self.gui.comp_text_column.queue_resize()


    def on_italic_toggle_toggled(self, button: Gtk.ToggleButton):
        active = button.get_active()
        if active:
            s = Pango.Style.ITALIC
        else:
            s = Pango.Style.NORMAL
        self.gui.comp_text_cell.set_property("style", s)
        self.gui.comp_text_column.queue_resize()


    def on_underline_toggle_toggled(self, button: Gtk.ToggleButton):
        active = button.get_active()
        if active:
            u = Pango.Underline.SINGLE
        else:
            u = Pango.Underline.NONE
        self.gui.comp_text_cell.set_property("underline", u)
        self.gui.comp_text_column.queue_resize()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
