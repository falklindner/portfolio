# portfolio

A collection of scripts with the aim of automating financial portfolio reporting and dashboarding.

Features so far:

- Importing from CSV with format 
    Booking,Execution,Amount,Name,WKN,Currency,Price,Value,Symbol,Portfolio
- Importing from Comdirect CSV exports

# Usage:

```


<portfolio path>
│   README.md
│   history_updater.py                      -> Python script keeping the history csv up-to-date
|   transaction_updater.py                  -> Python script keeping the transaction csv up-to-date
|   pf_updater.py                           -> Python script keeping the portfolio csv up-to-date
│
└───data
│   │   dict.csv                            -> Dictionary between WKN and Symbol
│   │   t7-xetr-allTradableInstruments.csv  -> List of all traded instruments at XETRA
│   │   transactions.csv                    -> Ordered list of all transactions
|   |   pfview.csv                          -> Daily portfolio statistics
|   |   newhist.csv                         -> Stock history database
│   └───inputs
│       │   input1.csv
│       │   input2.csv
│       │   ...
```

<p> Put input files in data/inputs/ </p>

## Steps for installation 
Install CRON job for history_updater after market closure, e.g.

    (crontab -l && echo "00  22   * * *  cd <portfolio path> && /usr/bin/python3 ./history_updater.py") | crontab -

<p> Install transcations updated with an inotify scripts (needs inotify-tools) </p>
    
    /bin/bash
    while true 
    do 
    inotifywait -r <portfolio path>/data/inputs && cd <portfolio path> && /usr/bin/python3 ./transactions_updater.py
    done
