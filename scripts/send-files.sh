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

  # Setup vars
  # USER=root
  # HOST=165.227.65.220

  # Move the weight
  echo "Copying file $FILE to $HOST..."
  cat $FILE | ssh $USER@$HOST "cat > ~/$FILE"
  echo "Copied file successfully!"
}

ARGS=( "$@" )
echo "Found ${#ARGS[@]} args:"

USER=$1; shift;
HOST=$1; shift;
printf "Preparing to send files to $USER@$HOST...\n"

for i in "${ARGS[@]}"
do
  # printf "$i\n"
  SEND_FILE $i
done

