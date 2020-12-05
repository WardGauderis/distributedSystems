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

-- played against TODO vroeger
select count(*)
from match m
where (m.home_team_id = 1 and m.away_team_id = 2
    or m.home_team_id = 2 and m.away_team_id = 1);

select * from match;



