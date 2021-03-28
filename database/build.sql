CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    gender VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

\copy users from './users.csv' delimiter ',' csv header;