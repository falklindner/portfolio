# portfolio
 
# Installation:

# Put input files in data/inputs/
# Install CRON job for history_updater after market closure, e.g. 
# (crontab -l && echo "00  22   * * *  cd <path> && /usr/bin/python3 ./history_updater.py") | crontab -

# Install for portfolio_updater
# /bin/bash
# while true 
# do 
# inotifywait -r <path>/data/inputs && cd <path> && /usr/bin/python3 ./transactions_updater.py
# done