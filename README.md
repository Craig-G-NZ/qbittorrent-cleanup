# qbittorrent-cleanup

Part of my automate for my home server setup. Jenkins periodically calls teh script to clean up folders where a torrent has been deleted but for some reason orphaned files/folders may remain.

    qbittorrent-cleanup.py "qbittorrent_website_url_and_port" "folder_path"

You will be notified via console what folders have been deleted but there is no other logging or notifications.
