tracker_list=$(curl -Ns https://trackerslist.com/all_aria2.txt)

aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port 6800 --check-certificate=false \
   --max-connection-per-server=10 --rpc-max-request-size=1024M \
   --bt-tracker="[$tracker_list]" --bt-max-peers=0 --seed-time=0.01 --min-split-size=10M \
   --follow-torrent=mem --split=10 \
   --daemon=true --allow-overwrite=true --max-overall-download-limit=0 \
   --max-overall-upload-limit=1K --max-concurrent-downloads=6 \
   --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36" --peer-id-prefix=-qB4250- --peer-agent=qBittorrent/4.2.5 \
   --disk-cache=64M --file-allocation=prealloc --continue=true \
   --max-file-not-found=5 --max-tries=20 --auto-file-renaming=true \
   --bt-enable-lpd=true --seed-time=0.01 --seed-ratio=1.0 \
   --bt-force-encryption=true --bt-require-crypto=true --bt-min-crypto-level=arc4 \
   --content-disposition-default-utf8=true --http-accept-gzip=true --reuse-uri=true
