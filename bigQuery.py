followingFavQuery = "select distinct tickers.ticker,tickers.name from favourites, tickers,(select id2 as id from following where id1 = '{}') mentors where mentors.id = favourites.id and favourites.ticker = tickers.ticker"