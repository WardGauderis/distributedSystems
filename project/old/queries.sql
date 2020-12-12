-- teams given division
select distinct t.id
from team t
         join match m on t.id = m.away_team_id or t.id = m.home_team_id
where m.division_id = 1
order by t.id;

-- best attack
select goals.id, sum(goals.sum)
from (
         select t.id, sum(m.goals_home_team)
         from team t
                  join match m on t.id = m.home_team_id
         where m.division_id = 1
         group by t.id
         union
         select t.id, sum(m.goals_away_team)
         from team t
                  join match m on t.id = m.away_team_id
         where m.division_id = 1
         group by t.id
     ) as goals
group by goals.id
order by sum(goals.sum) desc
limit 1;

-- best defence
select goals.id, sum(goals.sum)
from (
         select t.id, sum(m.goals_away_team)
         from team t
                  join match m on t.id = m.home_team_id
         where m.division_id = 1
         group by t.id
         union
         select t.id, sum(m.goals_home_team)
         from team t
                  join match m on t.id = m.away_team_id
         where m.division_id = 1
         group by t.id
     ) as goals
group by goals.id
order by sum(goals.sum)
limit 1;

--clean sheet
select clean_sheets.id, sum(clean_sheets.count)
from (
         select t.id, count(m.id)
         from team t
                  join match m on t.id = m.home_team_id
         where m.division_id = 1
           and goals_away_team = 0
         group by t.id
         union
         select t.id, count(m.id)
         from team t
                  join match m on t.id = m.away_team_id
         where m.division_id = 1
           and goals_home_team = 0
         group by t.id
     ) as clean_sheets
group by clean_sheets.id
order by sum(clean_sheets.count) desc
limit 1;

-- played against
select count(*)
from match m
where (m.home_team_id = 33 and m.away_team_id = 67
    or m.home_team_id = 67 and m.away_team_id = 33)
  and (date < (current_date at time zone 'CET')::date
    or time < (current_time at time zone 'CET')::time)
  and (status is null);

-- gewonnen
select count(*)
from match m
where (m.home_team_id = 33 and m.away_team_id = 67 and m.goals_home_team > m.goals_away_team
    or m.home_team_id = 67 and m.away_team_id = 33 and m.goals_home_team < m.goals_away_team)
  and (date < (current_date at time zone 'CET')::date
    or time < (current_time at time zone 'CET')::time)
  and (status is null);


-- al gespeeld
select *
from match
where (date <= (current_date at time zone 'CET')::date
    or time < (current_time at time zone 'CET')::time)
  and (status is null)
order by date desc;

-- select to_date(concat(date_part('year', date), '-', '08-29'), 'YYYY-MM-DD') + matchweek * 7
-- from match
-- where date = to_date('2018-09-05', 'YYYY-MM-DD')
--   and home_team_id = 33;
