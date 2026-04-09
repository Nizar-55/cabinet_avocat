"""
Package init for cabinet project.

This file attempts to use PyMySQL as a drop-in replacement for MySQLdb
when the `mysqlclient` C extension is not available. This lets Django use
MySQL via PyMySQL without requiring compilation of `mysqlclient`.
"""
try:
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	# If PyMySQL is not installed, we'll let Django raise the usual error
	# (e.g. prompting to install mysqlclient). This shim is safe to keep.
	pass

# Apply local monkeypatch to Django template Context copying for Python 3.14
try:
	from . import monkeypatch_context  # applies itself on import
except Exception:
	pass
