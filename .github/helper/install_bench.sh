#!/bin/bash
set -e
cd ~ || exit

verbosity="${BENCH_VERBOSITY_FLAG:-}"

start_time=$(date +%s)
echo "::group::Install Bench"
pip install creqit-bench
echo "::endgroup::"
end_time=$(date +%s)
echo "Time taken to Install Bench: $((end_time - start_time)) seconds"

git config --global init.defaultBranch main
git config --global advice.detachedHead false

start_time=$(date +%s)
echo "::group::Init Bench & Install creqit"
bench $verbosity init creqit-bench --skip-assets --python "$(which python)" --creqit-path "${GITHUB_WORKSPACE}"
echo "::endgroup::"
end_time=$(date +%s)
echo "Time taken to Init Bench & Install creqit: $((end_time - start_time)) seconds"

cd ~/creqit-bench || exit

start_time=$(date +%s)
echo "::group::Install App Requirements"
bench $verbosity setup requirements --dev
if [ "$TYPE" == "ui" ]
then
  bench $verbosity setup requirements --node;
fi
end_time=$(date +%s)
echo "::endgroup::"
echo "Time taken to Install App Requirements: $((end_time - start_time)) seconds"