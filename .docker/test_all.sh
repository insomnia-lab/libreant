#! /bin/bash
#
# Test libreant installation on different OS
#
# This script test the installation of libreant on different Operating Systems.
# For each operating system the following action will be performed:
#  - Build a docker image with libreant installed on it
#  - Run the container
#  - Test if the research page is working. This implies also testing that elasticsearch is working.
#	 The very first attempts may failed due to the startup time of both the container and elasticsearch.


DIR=$(dirname "$(readlink -f "$0")")

LIBREANT_SRC=$(readlink -f ${DIR}/..)

CURL_RETRIES=12 # 78 seconds

DEBIAN="debian-stable"
UBUNTU="ubuntu-lts"
ARCH="arch"

OSES=( ${DEBIAN} ${UBUNTU} ${ARCH} )
PREFIX="libreant-inst-test__"


function cleanup {
    for os in ${OSES[@]}; do
        docker kill ${OSES[@]/#/"$PREFIX"} > /dev/null 2>&1
    done
}

function test_libreant_search {
    curl -fsS "localhost:5000/search?q=*:*"  #> /dev/null
}


# this implements a linear backoff
# it will wait 1, then 2, then... $CURL_RETRIES seconds
function with_backoff {
  local max_attempts=${CURL_RETRIES}
  local attempt=1
  local exitCode=0

  # while condition is inside the loop!
  while true
  do
    set +e
    "$@"
    exitCode=$?
    set -e

    if [[ $exitCode == 0 ]]; then
      break
    fi

    # check before sleeping
    (( attempt <= max_attempts )) || break
   	printf ". "
    sleep $attempt
    attempt=$(( attempt + 1 ))
  done

  if [[ $exitCode != 0 ]]
  then
    echo "Failed too many times -- $*" 1>&2
  else
	  printf "\n"
  fi

  return $exitCode
}


trap cleanup EXIT
set -e

i=1
for os in "${OSES[@]}" ; do
    echo "Testing libreant installation on ${os}"
    docker build --file="${LIBREANT_SRC}/.docker/dockerfile-${os}" --tag="${PREFIX}${os}" "${LIBREANT_SRC}"
    docker run --rm -p 5000:5000 -d --name "${PREFIX}${os}" "${PREFIX}${os}"
    if ! with_backoff curl -fsS 'http://localhost:5000'; then
        echo "Failed docker test $i/${#OSES[@]}: $os" >&2
        echo "at step 1 (home page)" >&2
        exit 1
    fi
    if ! with_backoff test_libreant_search; then
        echo "Failed docker test $i/${#OSES[@]}: ${os}" >&2
        echo "at step 2 (search)" >&2
        docker kill "${PREFIX}${os}"
        exit 1
    fi
    echo "Docker test $i/${#OSES[@]} (${os})    [OK]"
    docker kill "${PREFIX}${os}"
    i=$((i+1))
done
echo "All test passed"
