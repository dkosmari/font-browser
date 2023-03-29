#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.70])
AC_INIT([font-browser], [0.2.1.dev], [])
AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIR([m4])
AM_INIT_AUTOMAKE([foreign])


# Checks for programs.
AC_PROG_LN_S
#AM_PATH_PYTHON([3.7])

AM_PO_SUBDIRS([po])
AM_GNU_GETTEXT([external])
AM_GNU_GETTEXT_REQUIRE_VERSION([0.19])

AM_PATH_GLIB_2_0

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

TARBALL_NAME="${PACKAGE_NAME}-${PACKAGE_VERSION}.tar.gz"
AC_SUBST([TARBALL_NAME])

AC_CONFIG_FILES([Makefile
                 font-browser.spec
                 po/Makefile.in])
AC_OUTPUT
