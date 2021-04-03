drop table users cascade;
drop table stocks;
drop table tickers cascade;
drop table favourites;
drop table notes;
drop table following;

with favor_companies(id, name) as 
(
    select mentors.id, tickers.name 
    from favourites, tickers,
    (select id2 as id from following 
    where id1 = 1) mentors
    where mentors.id = favourites.id 
    and favourites.ticker = tickers.ticker
    group by mentors.id, tickers.name 
    order by mentors.id asc, tickers.name asc
),
freq_companies(name, freq) as 
(
    select name, count(*)
    from favor_companies
    group by name 
    order by name asc
)
select * from freq_companies;

with trending_companies(name, followers) as 
(
    select tickers.name, count(favourites.id)
    from favourites, tickers
    where favourites.ticker = tickers.ticker 
    group by tickers.name 
    order by count(favourites.id) desc, tickers.name asc
)
select * from trending_companies limit 10;