#!/bin/bash

SEND_FILE () {
  # Gather args && shift
  FILE=$1; shift;
  
  # Validate the file
  if [ ! -f "$FILE" ]; then
    printf "$FILE not found. We are skipping...\n"
    return
  fi

  # Any extra args
  EXTRA_ARGS=$@

  # Move the weight
  echo "Copying file $FILE to $HOST..."
  cat $FILE | ssh $USER@$HOST "cat > ~/$FILE"
  echo "Copied file successfully!"
}

ARGS=( "$@" )
# TODO: Print help text if unmatched args
# echo "Found ${#ARGS[@]} args:"

USER=$1; shift; unset 'ARGS[0]'
HOST=$1; shift; unset 'ARGS[1]'
printf "Preparing to send files to $USER@$HOST...\n"

# Remove files from args

for i in "${ARGS[@]}"
do
  # printf "$i\n"
  SEND_FILE $i
done

