***Decision Memo***


1. I utilized the event_timestamp as the time source of truth since it is in UTC time and derived a date field from the timestamp. A day ends at time 23:59:59 UTC and begins at 00:00:00. This means that the "day" does not necessarily align with the timezone the data is viewed in. I would consider altering this to EST for front end users. 

2a. To determine the number of web transactions that existed in the last 14 days, I only wanted to see donations that contained a web donation. For this section, I removed the donations that existed in Salesforce, but not as a web donation. Additionally, I had to consider the fact that the Salesforce csv contained a wider pool of dates, which would skew the attribution rate if it were not narrowed to the same date range as the web's 14 days. I included null Salesforce donation dates as well so it would keep rows where there was only a web and not a Salesforce record. 

2b. I provided a table with information regarding the records that existed only in web transactions or only in Salesforce to the fundraising team. The goal here is for the fundraising team to be able to identify the individuals without a Salesforce record and update the CRM accordingly. For the individuals without a web donation record, perhaps the donation team needs to confirm that the donation was actually completed, or they need to indicate in the CRM that the donation was obtained in a different method than web (e.g. check or over the phone).

2c. For any donations outside of the campaign window, I would not attribute those donations to a campaign, unless if a donor specifically requests the donation to be attributed to the campaign window.  

3a. I would include A in the slide deck, because it shows finalized numbers for the period. A broadcast week is final when every air_date has a live_7 attribution demonstrating that the viewing window is over. This ensures the numbers are stable.

3b. I would caveat that the device-scoped event count can only account for devices that can be tracked by GA4. These events are only accounting for the audience watching on the website, and thus does not highlight the total audience. A panel-based audience may be not be representative of the total audience but it does encompass all viewing platforms. 

**Identity**
This is a classic problem when dealing with web events. If a user happens to log in to watch a video, their session and user_psuedo_id becomes attached to their contact_id. Because it is an extra step that is presumably not required to watch Sesame Street, it is unlikely I can say definitively that a donor watched a video before donating. I would refuse to claim x% of video watchers donate after or x% of donors watched a video beforehand. I would be able to provide a list of individuals who signed in before watching and then provided their donation information afterwards. 

**Refused/Deferred**

-I refused or deferred building much of the GA tables including modeling out each event_name and each event_param. I only defined these terms as relevant to the task. In the future, it would be likely helpful to dive into page_location information to fct_ga_events and to add login information to the fct_donation table. I also did not use the intraday model which would be helpful to track event progression over the course of the previous day. 

-I also did not dive deeply into contacts.csv and only utilized it briefly as a source of information for the fundraising team regarding mismatched donations. This could be cleaned up to remove deleted records. 

-I did not touch donation amount in donations.csv, which could be modeled to show lifetime value, avg donation, and time series models.

-I did not examine household ratings which could be tracked over time and network.


**Incremental loading**
if this ran hourly: 
I am imagining the incremental load would be most useful for GA4, so that is the schema I will be referencing below.
Ideally, I would want to skip records that have not changed in the timeframe, and append the records that are new. 

*merge key:*  I would use a unique pkey using something like gen_random_uuid() as event_id--- this should be unique and not null and immutable

*watermark:* timestamp of the last upload 

*late-data policy:* Hold until next refresh  

*intraday-file policy:* It can get quite expensive to run jobs multiple times a day, so unless it is deemed critical to have intraday live data, I would advise having the full data refresh to occur once a day. The front end users would then have data up to date from the last complete day. 

**Questions for Upstream Owners**
1. For the GA4 owners: What does the event_param {key: percent, {value: int}} reference? 
2. For the Salesforce owners: Are some donations received in methods outside of web donations? How is this notated in Salesforce?

**AI Use**

I did not use AI in this project.
  
