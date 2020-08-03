ACLOCAL_AMFLAGS = -I m4

SUBDIRS = po

dist_bin_SCRIPTS = font-browser
BUILT_SOURCES = font-browser
CLEANFILES = font-browser

font-browser: $(srcdir)/font-browser.py
	$(SED) \
		-e 's|[@]prefix@|$(prefix)|g' \
		-e 's|[@]localedir@|$(localedir)|g' \
		-e 's|[@]pkgdatadir@|$(pkgdatadir)|g' \
		< "$<" > "$@"


GRESOURCE_FILE = font-browser.gresource
GRESOURCE_XML = $(srcdir)/$(GRESOURCE_FILE).xml

pkgdata_DATA = $(GRESOURCE_FILE)
BUILT_SOURCES += $(GRESOURCE_FILE)
CLEANFILES += $(GRESOURCE_FILE)

RESOURCES_DIR = $(srcdir)/resources
RESOURCES := $(shell $(GLIB_COMPILE_RESOURCES) \
			--generate-dependencies \
			$(GRESOURCE_XML) \
			--sourcedir=$(RESOURCES_DIR))

$(GRESOURCE_FILE): $(GRESOURCE_XML) $(RESOURCES)
	$(info building $@ from $<)
	$(GLIB_COMPILE_RESOURCES) $< --target=$@ --sourcedir=$(RESOURCES_DIR)

