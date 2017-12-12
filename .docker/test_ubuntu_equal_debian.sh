#! /bin/bash
DIR=$(dirname "$(readlink -f "$0")")

DEBIAN_DKR="dockerfile-debian-stable"
UBUNTU_DKR="dockerfile-ubuntu-lts"

diff <(tail -n +2 $DIR/${UBUNTU_DKR}) <( tail -n +3 $DIR/${DEBIAN_DKR})  
