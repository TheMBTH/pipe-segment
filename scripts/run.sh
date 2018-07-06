#!/usr/bin/env bash
set -e

THIS_SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"

display_usage() {
	echo "Available Commands"
	echo "  segment                     run the segmenter in dataflow"
	echo "  identity_messages_monthly   generate monthly identity message summaries"
	echo "                              per segment"
	echo "  segment_identity            generate monthly vessel_ids per segment"
	echo "  segment_info                create a segment_info table with one row per segment"
	}


if [[ $# -le 0 ]]
then
    display_usage
    exit 1
fi


case $1 in
  identity_messages_monthly)
    ${THIS_SCRIPT_DIR}/identity_messages_monthly.sh "${@:2}"

  ;;

  segment_identity)
    ${THIS_SCRIPT_DIR}/segment_identity.sh "${@:2}"
  ;;

  segment_info)
    ${THIS_SCRIPT_DIR}/segment_info.sh "${@:2}"
  ;;

  segment)

    python -m pipe_segment "${@:2}"
    ;;

  *)
    display_usage
    exit 0
    ;;
esac
