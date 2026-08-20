# Q1. A session is (user_pseudo_id, ga_session_id); events without ga_session_id belong to no
# session. How many sessions have their first event between 2026-07-01 00:00:00 and 2026-07-07
# 23:59:59 UTC (inclusive week), and what is the median session duration (last event - first event;
# single-event sessions count as 0) for those sessions, in seconds?
# Memo prompt for Q1: GA4's event_date is property-local time. State the time semantics your models treat
# as canonical, and what that means for when a day's partition is closed.


import duckdb
raw_events = duckdb.sql("""
                SELECT 
                        to_timestamp(CAST(LEFT(event_timestamp, 10 )  as int64)) ga_event_timestamp,
                        date(ga_event_timestamp) as event_date,
                        event_name,
                        user_pseudo_id,
                        unnest(event_params, recursive:=true) as event_params
                        FROM read_json_auto('events/*.jsonl',
                        auto_detect = TRUE, union_by_name = TRUE) as events
                            
                            """)


fct_ga_events = duckdb.sql("""
                SELECT
                ga_event_timestamp,
                event_name,
                user_pseudo_id,
                int_value as ga_session_id,
                concat(user_pseudo_id, ga_session_id) as session,
                rank() OVER(PARTITION BY user_pseudo_id,ga_session_id ORDER by ga_event_timestamp asc) as session_rank
                FROM raw_events
                WHERE key = 'ga_session_id'
                and key is not NULL
""")
print('fct_ga_events')
print(fct_ga_events)

first_event_period = duckdb.sql("""
                SELECT 
                count(distinct session) as session_count
                FROM fct_ga_events
                    WHERE ga_event_timestamp between '2026-07-01 00:00:00' and '2026-07-07 23:59:59'
                AND session_rank = 1
""")
print('# of sessions that have their first event between 2026-07-01 00:00:00 and 2026-07-07 23:59:59 UTC (inclusive week)')
print(first_event_period)

median = duckdb.sql("""
                with max as (SELECT 
                    distinct session as session,
                    max(session_rank) as last_event
                    from fct_ga_events
                    group by 1),
                
                max_time as (SELECT
                    max.session,
                    max.last_event,
                    ga_event_timestamp,
                    from max
                    left join fct_ga_events e 
                        on max.session = e.session 
                    where session_rank = last_event
                    AND ga_event_timestamp between '2026-07-01 00:00:00' and '2026-07-07 23:59:59'
                    ),
                
                min as (SELECT
                    distinct session as session,
                    session_rank as first_event,
                    ga_event_timestamp,
                    from fct_ga_events
                    where session_rank = 1
                    AND ga_event_timestamp between '2026-07-01 00:00:00' and '2026-07-07 23:59:59'
                    
                    ),
                    
                duration as (select 
                distinct max_time.session as session,
                max_time.ga_event_timestamp - min.ga_event_timestamp as session_duration,
                row_number() OVER(ORDER by session_duration) as rank,
                first_event,
                last_event
                from max_time
                left join min on max_time.session = min.session
                order by session_duration)
                
                select
                    session_duration
                    from duration
                    where rank = (select count(distinct session)/2 as session_count from duration)
                    
                    
                

"""
)
print('median session duration from first to last event')
print(median)

# Across the full 14 days: how many distinct web transactions
# (donation_complete.transaction_id) are there, how many match a Salesforce donation, and what is
# the attribution rate?
# • Memo prompt for Q2: what do you tell the fundraising team about the transactions that don't match — and
# does a donation dated outside its campaign's window count toward that campaign's total?

fct_donations= duckdb.sql(""" 
with stg_donation_events as (SELECT 
                    *
                   FROM raw_events
                   WHERE event_name = 'donation_complete'
                   AND key = 'transaction_id'),
    
    stg_donations as (SELECT  
                        donations.campaign_id,
                        date(donated_at) as donated_at_date,
                        transaction_id as transaction_id,
                        name as campaign_name,
                        starts_on as campaign_start_date,
                        ends_on as campaign_end_date,
                        email
                    FROM read_csv('salesforce/donations.csv') as donations
                        LEFT JOIN read_csv('salesforce/campaigns.csv') as campaigns 
                            ON campaigns.campaign_id = donations.campaign_id
                        LEFT JOIN read_csv('salesforce/contacts.csv') as contacts
                            ON contacts.contact_id = donations.contact_id
                    WHERE transaction_id is not NULL)
        
                SELECT
                event_date,
                donated_at_date, ---salesforce
                string_value as web_transaction_id,
                transaction_id as salesforce_transaction_id,
                campaign_id,
                campaign_name,
                campaign_start_date,
                campaign_end_date,
                email,
                user_pseudo_id
           from stg_donation_events
           full outer join stg_donations
           on stg_donations.transaction_id = stg_donation_events.string_value
           order by 1
   
           """)


print('fct_donations')
print(fct_donations)

web_transactions = duckdb.sql("""
                    select 
                        count(distinct web_transaction_id) as web_transaction_count,
                        count(distinct salesforce_transaction_id) as salesforce_transaction_count,
                        salesforce_transaction_count/web_transaction_count
                    from fct_donations
                        where (donated_at_date between '2026-07-01' and '2026-07-14' or donated_at_date is NULL)
                        and web_transaction_id is not NULL ---only examining donations with a web transaction, not any solely in salesforce
""")
print('Web Transactions count in the last 14 days and attribution rate to salesforce donations')
print(web_transactions)

transactions_dont_match_info = duckdb.sql("""
                    select 
                        web_transaction_id,
                        salesforce_transaction_id,
                        campaign_name,
                        donated_at_date,
                        coalesce(email,user_pseudo_id) as identifier
                    from fct_donations
                        where (donated_at_date between '2026-07-01' and '2026-07-14' or donated_at_date is NULL)
                        and (web_transaction_id is NULL or salesforce_transaction_id is NULL)""")

print('Information regarding web or salesforce donations that do not have a corresponding record in the other database.')
print(transactions_dont_match_info)



memo_2 = duckdb.sql("""
                SELECT
                campaign_name,
                donated_at_date,
                campaign_start_date,
                campaign_end_date,
                salesforce_transaction_id,
                donated_at_date- campaign_start_date as datediff_start,
                donated_at_date-campaign_end_date as datediff_end
                from fct_donations
                WHERE campaign_name is not NULL
                AND datediff_start <=0
                AND datediff_end >=0

""")
print(memo_2)

#  A telecast's reportable audience is its live_7 row if one has been delivered, otherwise its live_sd
# row;
# if the same telecast and stream appear in more than one delivery file, the most recent delivery wins.
# For Sesame Street telecasts with air_date in the broadcast week Mon 2026-07-06 through Sun 2026-07-12:
# (a) the total reportable audience (sum of avg_audience_k) using every delivered file;
# (b) the same total as it would have been reported using only files delivered on or before 2026-07-21;
# (c) the count of site video_start events for Sesame Street episodes (episode_id beginning SST-) in that
# same week, UTC.
# Memo prompt for Q3: which of (a)/(b) goes in the board deck, what is your rule for calling a broadcast week
# final, and what caveat goes under a slide that shows a panel-based audience estimate next to a
# device-scoped event count?

raw_ratings = duckdb.sql(""" SELECT * 
                        FROM read_csv('ratings/*.csv', union_by_name = true,filename=true)""")

stg_ratings = duckdb.sql("""SELECT 
                            avg_audience_k as reportable_audience,
                            stream,
                            air_date,
                            telecast_id,
                           cast(concat(substring(filename,24, 4),'-',substring(filename,28,2), '-',substring(filename,30,2)) as date) as delivery_date,
                        FROM raw_ratings
                     WHERE program_id = 'SST'
                     order by air_date desc""")
        
fct_ratings = duckdb.sql("""SELECT *,
        row_number() OVER(PARTITION by telecast_id ORDER BY delivery_date desc) as row_num
            FROM stg_ratings
        ORDER BY air_date """)

print(fct_ratings)

stg_video_events = duckdb.sql("""
        SELECT 
            event_name as video_start_events, 
            ga_event_timestamp,
            string_value as episode_id
        from raw_events
        where event_name = 'video_start'
        and key = 'episode_id'
        and string_value like 'SST-%'
        
        
""")
a = duckdb.sql("""
        SELECT 
            sum(reportable_audience) as total_reportable_audience
        FROM fct_ratings
        where row_num = 1
        AND air_date between '2026-07-06' and '2026-07-12'


""")
print('(a) the total reportable audience (sum of avg_audience_k) using every delivered file')
print(a)

b = duckdb.sql("""
        with b as (SELECT 
            reportable_audience,
            telecast_id,
            delivery_date,
            row_number() OVER(PARTITION by telecast_id ORDER BY delivery_date desc) as row_num
        FROM stg_ratings
        where air_date between '2026-07-06' and '2026-07-12'
        AND delivery_date <= '2026-07-21'
        QUALIFY row_num =1)
            
        select 
            sum(reportable_audience) as total_reportable_audience
            from b
""")
print('(b) the same total as it would have been reported using only files delivered on or before 2026-07-21')
print(b)


c = duckdb.sql("""
        SELECT 
            count(video_start_events)
        from stg_video_events
       where ga_event_timestamp between '2026-07-06 00:00:00-04' and '2026-07-12 23:59:59-04'
""")
print('(c) the count of site video_start events for Sesame Street episodes (episode_id beginning SST-) in that same week, UTC.')
print(c)









