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

CURL_RETRY_DELAY=3 # seconds
CURL_RETRIES=20 # seconds

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
    curl -f -sS "localhost:5000/search?q=*:*" > /dev/null
}

function with_backoff {
  local max_attempts=${CURL_RETRIES}
  local timeout=${CURL_RETRY_DELAY}
  local attempt=0
  local exitCode=0

  while (( $attempt < $max_attempts ))
  do
    set +e
    "$@"
    exitCode=$?
    set -e

    if [[ $exitCode == 0 ]]; then
      break
    fi

   	printf ". "
    sleep $timeout
    attempt=$(( attempt + 1 ))
  done

  if [[ $exitCode != 0 ]]
  then
    echo "Failed too many times" 1>&2
  else
	  printf "\n"
  fi

  return $exitCode
}


trap cleanup EXIT
set -e

for os in ${OSES[@]} ; do
    printf "Testing libreant installation on ${os}\n"
    docker build --file="${LIBREANT_SRC}/.docker/dockerfile-${os}" --tag="${PREFIX}${os}" "${LIBREANT_SRC}"
    docker run --rm -p 5000:5000 -d --name ${PREFIX}${os} ${PREFIX}${os}
    with_backoff test_libreant_search
    docker kill ${PREFIX}${os}
done
