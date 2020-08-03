ACLOCAL_AMFLAGS = -I m4

EXTRA_DIST = \
	bootstrap \
	font-browser.desktop \
	font-browser.gresource.xml \
	font-browser.png \
	font-browser.py \
	resources

SUBDIRS = po

dist_bin_SCRIPTS = font-browser
BUILT_SOURCES = font-browser
CLEANFILES = font-browser

font-browser: $(srcdir)/font-browser.py Makefile
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




dist-pkg: all
	echo "Compare fonts side by side." > description-pak
	checkinstall --install=no --pakdir="${builddir}" --backup=no --deldoc=no --deldesc=no --delspec=yes --pkgname="${PACKAGE_NAME}" --pkgversion="${PACKAGE_VERSION}" --pkgsource="${PACKAGE_URL}" --pkglicense="GPLv3" --pkgarch="noarch" --provides="" --requires=""
