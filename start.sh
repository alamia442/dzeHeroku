#!/bin/sh

DOWNLOADER="curl -fsSL --connect-timeout 3 --max-time 3 --retry 2"
TRACKER=$(
            ${DOWNLOADER} https://trackerslist.com/all_aria2.txt &&
                ${DOWNLOADER} https://cdn.jsdelivr.net/gh/XIU2/TrackersListCollection@master/all_aria2.txt &&
                ${DOWNLOADER} https://trackers.p3terx.com/all_aria2.txt | sort -u
        )
echo -e "
--------------------[BitTorrent Trackers]--------------------
${TRACKER}
--------------------[BitTorrent Trackers]--------------------
"
#tracker_list=$(curl -Ns https://trackerslist.com/all_aria2.txt)
ran=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)
# Start aria2c
aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port 6800 --check-certificate=false \
   --max-connection-per-server=16 --rpc-max-request-size=10M \
   --bt-tracker="[$TRACKER]" --bt-max-peers=128 --seed-time=0.01 --min-split-size=4M \
   --follow-torrent=true --split=32 \
   --daemon=true --allow-overwrite=true --max-overall-download-limit=0 \
   --max-overall-upload-limit=2M --max-concurrent-downloads=7 \
   --user-agent="Transmission 2.94" --peer-id-prefix=-TR2940-"[$ran]" --peer-agent="Transmission 2.94" \
   --disk-cache=64M --file-allocation=prealloc --continue=true \
   --max-file-not-found=6 --max-tries=0 --auto-file-renaming=true \
   --bt-enable-lpd=true --seed-time=0.01 --seed-ratio=1.0 \
   --bt-force-encryption=true --bt-require-crypto=true --bt-min-crypto-level=arc4 \
   --content-disposition-default-utf8=true --http-accept-gzip=true --reuse-uri=true \
   --enable-peer-exchange=true --bt-request-peer-speed-limit=10M \
   --enable-dht=true --dht-file-path=/app/dht.dat --dht-entry-point=dht.transmissionbt.com:6881

python3 -m pip install -U -r requirements.txt

python3 -m bot
