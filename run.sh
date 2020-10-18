#! /bin/bash

set -e

dir="mc"

mkdir -p "$dir"

if [[ ! -f "$dir"/eula.txt ]]; then
    printf "Type YES to indicate you agree to the minecraft EULA
    (https://account.mojang.com/documents/minecraft_eula).\nType YES to agree:"

    read -r answer
    if [[ "$answer" != "YES" ]]; then
        exit 1
    else
cat <<EOF > "$dir"/eula.txt
#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).
#"$(date)"
eula=true
EOF
    fi
fi



if [[ ! -f mc/server.jar ]]; then
    echo "Downloading Minecraft Server jar to '$dir'"
    wget -O "$dir"/server.jar https://launcher.mojang.com/v1/objects/f02f4473dbf152c23d7d484952121db0b36698cb/server.jar
fi

if [[ -f "$dir"/eula.txt ]]; then
    echo "Starting Minecraft Server"
    ./runserver.py
fi
