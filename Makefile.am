ACLOCAL_AMFLAGS = -I m4

EXTRA_DIST = \
	bootstrap \
	font-browser.desktop \
	font-browser.gresource.xml \
	font-browser.png \
	font-browser.py \
	font-browser.spec.in \
	README.md \
	resources

SUBDIRS = po

dist_bin_SCRIPTS = font-browser
BUILT_SOURCES = font-browser
CLEANFILES = font-browser

font-browser: $(srcdir)/font-browser.py Makefile
	$(SED) \
		-e 's|[@]localedir@|$(localedir)|g' \
		-e 's|[@]pkgdatadir@|$(pkgdatadir)|g' \
		-e 's|[@]PACKAGE_VERSION@|$(PACKAGE_VERSION)|g' \
		< "$<" > "$@"
	chmod +x $@


all-local: font-browser


GRESOURCE_FILE = font-browser.gresource
GRESOURCE_XML = $(srcdir)/$(GRESOURCE_FILE).xml

pkgdata_DATA = $(GRESOURCE_FILE)
BUILT_SOURCES += $(GRESOURCE_FILE)
CLEANFILES += $(GRESOURCE_FILE)

RESOURCES_DIR = $(srcdir)/resources
RESOURCES = $(shell $(GLIB_COMPILE_RESOURCES) \
			--generate-dependencies \
			$(GRESOURCE_XML) \
			--sourcedir=$(RESOURCES_DIR))

$(GRESOURCE_FILE): $(GRESOURCE_XML) $(RESOURCES)
	$(GLIB_COMPILE_RESOURCES) $< --target=$@ --sourcedir=$(RESOURCES_DIR)



desktopdir = $(datadir)/applications
desktop_DATA = font-browser.desktop

icondir = $(datadir)/icons
icon_DATA = font-browser.png


.PHONY: rpm

RPM_TARBALL_NAME = $(HOME)/rpmbuild/SOURCES/$(TARBALL_NAME)

rpm: font-browser.spec dist-gzip
	 [ -e $(RPM_TARBALL_NAME) ] || \
		$(LN_S) $(PWD)/$(TARBALL_NAME) $(RPM_TARBALL_NAME)
	rpmbuild -ba $<

