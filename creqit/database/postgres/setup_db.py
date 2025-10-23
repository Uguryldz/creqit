import os
import re

import creqit
from creqit.database.db_manager import DbManager
from creqit.utils import cint


def setup_database():
	root_conn = get_root_connection()
	root_conn.commit()
	root_conn.sql("end")
	root_conn.sql(f'DROP DATABASE IF EXISTS "{creqit.conf.db_name}"')

	# If user exists, just update password
	if root_conn.sql(f"SELECT 1 FROM pg_roles WHERE rolname='{creqit.conf.db_user}'"):
		root_conn.sql(f"ALTER USER \"{creqit.conf.db_user}\" WITH PASSWORD '{creqit.conf.db_password}'")
	else:
		root_conn.sql(f"CREATE USER \"{creqit.conf.db_user}\" WITH PASSWORD '{creqit.conf.db_password}'")
	root_conn.sql(f'CREATE DATABASE "{creqit.conf.db_name}"')
	root_conn.sql(f'GRANT ALL PRIVILEGES ON DATABASE "{creqit.conf.db_name}" TO "{creqit.conf.db_user}"')
	if psql_version := root_conn.sql("SHOW server_version_num", as_dict=True):
		semver_version_num = psql_version[0].get("server_version_num") or "140000"
		if cint(semver_version_num) > 150000:
			root_conn.sql(f'ALTER DATABASE "{creqit.conf.db_name}" OWNER TO "{creqit.conf.db_user}"')
	root_conn.close()


def bootstrap_database(verbose, source_sql=None):
	creqit.connect()
	import_db_from_sql(source_sql, verbose)

	creqit.connect()
	if "tabDefaultValue" not in creqit.db.get_tables():
		import sys

		from click import secho

		secho(
			"Table 'tabDefaultValue' missing in the restored site. "
			"This may be due to incorrect permissions or the result of a restore from a bad backup file. "
			"Database not installed correctly.",
			fg="red",
		)
		sys.exit(1)


def import_db_from_sql(source_sql=None, verbose=False):
	if verbose:
		print("Starting database import...")
	db_name = creqit.conf.db_name
	if not source_sql:
		source_sql = os.path.join(os.path.dirname(__file__), "framework_postgres.sql")
	DbManager(creqit.local.db).restore_database(
		verbose, db_name, source_sql, creqit.conf.db_user, creqit.conf.db_password
	)
	if verbose:
		print("Imported from database %s" % source_sql)


def get_root_connection():
	if not creqit.local.flags.root_connection:
		from getpass import getpass

		if not creqit.flags.root_login:
			creqit.flags.root_login = (
				creqit.conf.get("root_login") or input("Enter postgres super user [postgres]: ") or "postgres"
			)

		if not creqit.flags.root_password:
			creqit.flags.root_password = creqit.conf.get("root_password") or getpass(
				"Postgres super user password: "
			)

		creqit.local.flags.root_connection = creqit.database.get_db(
			socket=creqit.conf.db_socket,
			host=creqit.conf.db_host,
			port=creqit.conf.db_port,
			user=creqit.flags.root_login,
			password=creqit.flags.root_password,
			cur_db_name=creqit.flags.root_login,
		)

	return creqit.local.flags.root_connection


def drop_user_and_database(db_name, db_user):
	root_conn = get_root_connection()
	root_conn.commit()
	root_conn.sql(
		"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = %s",
		(db_name,),
	)
	root_conn.sql("end")
	root_conn.sql(f"DROP DATABASE IF EXISTS {db_name}")
	root_conn.sql(f"DROP USER IF EXISTS {db_user}")
