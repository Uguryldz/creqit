#!/bin/bash
set -e
cd ~/creqit-bench || exit

echo "::group::Create Test Site"
mkdir ~/creqit-bench/sites/test_site
cp "${GITHUB_WORKSPACE}/.github/helper/db/$DB.json" ~/creqit-bench/sites/test_site/site_config.json

if [ "$DB" == "mariadb" ]
then
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "SET GLOBAL character_set_server = 'utf8mb4'";
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "SET GLOBAL collation_server = 'utf8mb4_unicode_ci'";

  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "CREATE DATABASE test_creqit";
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "CREATE USER 'test_creqit'@'localhost' IDENTIFIED BY 'test_creqit'";
  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "GRANT ALL PRIVILEGES ON \`test_creqit\`.* TO 'test_creqit'@'localhost'";

  mariadb --host 127.0.0.1 --port 3306 -u root -ptravis -e "FLUSH PRIVILEGES";
fi
if [ "$DB" == "postgres" ]
then
  echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE DATABASE test_creqit" -U postgres;
  echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE USER test_creqit WITH PASSWORD 'test_creqit'" -U postgres;
fi
echo "::endgroup::"

echo "::group::Modify processes"
sed -i 's/^watch:/# watch:/g' Procfile
sed -i 's/^schedule:/# schedule:/g' Procfile

if [ "$TYPE" == "server" ]
then
  sed -i 's/^socketio:/# socketio:/g' Procfile
  sed -i 's/^redis_socketio:/# redis_socketio:/g' Procfile
fi

if [ "$TYPE" == "ui" ]
then
  sed -i 's/^web: bench serve/web: bench serve --with-coverage/g' Procfile
fi
echo "::endgroup::"

bench start &> ~/creqit-bench/bench_start.log &

echo "::group::Install site"
if [ "$TYPE" == "server" ]
then
  CI=Yes bench build --app creqit &
  build_pid=$!
fi

bench --site test_site reinstall --yes

if [ "$TYPE" == "server" ]
then
  # wait till assets are built successfully
  wait $build_pid
fi
echo "::endgroup::"
