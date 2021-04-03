CREATE TABLE users(
    id SERIAL UNIQUE PRIMARY KEY,
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
    constraint id_ref foreign key (id) references users(id) on delete cascade,
    constraint ticker_ref foreign key (ticker) references tickers(ticker)
);

CREATE TABLE following(
    id1 INTEGER,
    id2 INTEGER,
    constraint fol_key primary key (id1,id2),
    constraint id1_ref foreign key (id1) references users(id) on delete cascade,
    constraint id2_ref foreign key (id2) references users(id) on delete cascade
);

create table notes (
    id integer,
    note varchar,
    constraint notes_key primary key (id, note),
    constraint id_ref foreign key (id) references users(id)
);


\copy users from './users.csv' delimiter ',' csv header;
\copy tickers from './tickers.csv' delimiter ',' csv header;
\copy stocks from './stocks.csv' delimiter ',' csv header;
\copy favourites from './favourites.csv' delimiter ',' csv header;
\copy notes from './notes.csv' delimiter ',' csv header;
\copy following from './following.csv' delimiter ',' csv header;
 