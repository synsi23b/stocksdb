# stocksdb

1. enter MONGOCON in .env file to connect to mongodb of choice
2. run import_jpy_rate.py to download exchange rate and fill DB
3. download Depotumsaetze.csv from flatex -> depotumsaetze -> zeitraum *start* .. heute -> export csv
4. run import_depot.py to sanitize the data and fill DB. Running multiple times is no problem, not creating double entries

# TODO

5. build_current_depot -> read transactions add / remove stock to build a readable history. Especially, create Sale history with date / exchange rate bought at. Considering "FIFO" of stocks when buying / selling partials