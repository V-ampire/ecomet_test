select ps.phrase as phrase
  , 
  arrayZip(groupArray(toInt32(ps.hour)), groupArray(toInt32(ps.hour_views))) as views_by_hour
from (
  select phrase
    , (dateName('hour', dt)) as hour
    , sum(views) as hour_views
  from test.phrases_views
  where toDate(dt) = today()
  and campaign_id =  3333333
  group by phrase, dateName('hour', dt)
) as ps
group by ps.phrase
;