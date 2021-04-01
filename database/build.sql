CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    gender VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE tickers(
    ticker VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL
);

CREATE TABLE stocks(
    date DATE,
    ticker VARCHAR,
    open FLOAT,
    close FLOAT,
    high FLOAT,
    low FLOAT,
    constraint stocks_key primary key (date,ticker),
    constraint ticker_ref foreign key (ticker) references tickers(ticker)
);

CREATE TABLE favourites(
    id INTEGER,
    ticker VARCHAR,
    constraint fav_key primary key (id,ticker),
    constraint id_ref foreign key (id) references users(id),
    constraint ticker_ref foreign key (ticker) references tickers(ticker)
);

\copy users from 'C:\\Users\\DELL\\Documents\\GitHub\\col362project\\database\\users.csv' delimiter ',' csv header;
\copy tickers from 'C:\\Users\\DELL\\Documents\\GitHub\\col362project\\database\\tickers.csv' delimiter ',' csv header;
\copy stocks from 'C:\\Users\\DELL\\Documents\\GitHub\\col362project\\database\\stocks.csv' delimiter ',' csv header;
\copy favourites from 'C:\\Users\\DELL\\Documents\\GitHub\\col362project\\database\\favourites.csv' delimiter ',' csv header;

 