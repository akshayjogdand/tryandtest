
begin;

delete from stats_predictionfieldstat where match_id = 444;
delete from stats_teamstat where match_id = 444;
delete from stats_playerstat where match_id = 444;

delete from stats_predictionfieldstat where match_id = 487;
delete from stats_teamstat where match_id = 487;
delete from stats_playerstat where match_id = 487;

delete from stats_predictionfieldstat where match_id = 481;
delete from stats_teamstat where match_id = 481;
delete from stats_playerstat where match_id = 481;

delete from stats_predictionfieldstat where match_id = 462;
delete from stats_teamstat where match_id = 462;
delete from stats_playerstat where match_id = 462;

delete from stats_predictionfieldstat where match_id = 458;
delete from stats_teamstat where match_id = 458;
delete from stats_playerstat where match_id = 458;



./manage.py compute_match_submission_stats --match-id=444

BEGIN;

delete from predictions_membersubmissiondata where member_submission_id in
(select id from predictions_membersubmission where match_id=444);

delete from predictions_membersubmission where match_id=444;

delete from stats_predictionfieldstat where match_id = 444;
delete from stats_teamstat where match_id = 444;
delete from stats_playerstat where match_id = 444;
---
delete from predictions_membersubmissiondata where member_submission_id in
(select id from predictions_membersubmission where match_id=487);

delete from predictions_membersubmission where match_id=487;

delete from stats_predictionfieldstat where match_id = 487;
delete from stats_teamstat where match_id = 487;
delete from stats_playerstat where match_id = 487;
---
delete from predictions_membersubmissiondata where member_submission_id in
(select id from predictions_membersubmission where match_id=481);

delete from predictions_membersubmission where match_id=481;

delete from stats_predictionfieldstat where match_id = 481;
delete from stats_teamstat where match_id = 481;
delete from stats_playerstat where match_id = 481;
---
delete from predictions_membersubmissiondata where member_submission_id in
(select id from predictions_membersubmission where match_id=462);

delete from predictions_membersubmission where match_id=462;

delete from stats_predictionfieldstat where match_id = 462;
delete from stats_teamstat where match_id = 462;
delete from stats_playerstat where match_id = 462;
---
delete from predictions_membersubmissiondata where member_submission_id in
(select id from predictions_membersubmission where match_id=458);

delete from predictions_membersubmission where match_id=458;

delete from stats_predictionfieldstat where match_id = 458;
delete from stats_teamstat where match_id = 458;
delete from stats_playerstat where match_id = 458;




---
-- IPL 2020 TPREDS
---
BEGIN;

delete from predictions_membersubmissiondata where member_submission_id in
(select id from predictions_membersubmission where tournament_id = 37);

delete from predictions_membersubmission where tournament_id = 37;

BEGIN;
delete from stats_predictionfieldstat where tournament_id = 37;
delete from stats_teamstat where tournament_id = 37;
delete from stats_playerstat where tournament_id = 37;


select distinct stat_name from stats_playerstat;


BEGIN;
delete from stats_predictionfieldstat where match_id = 730;
delete from stats_teamstat where match_id = 730;
delete from stats_playerstat where match_id =  730 and stat_name like 'selection_%';

BEGIN;
delete from stats_predictionfieldstat where match_id = 731;
delete from stats_teamstat where match_id = 731;
delete from stats_playerstat where match_id =  731 and stat_name like 'selection_%';


-- M7
BEGIN; delete from stats_predictionfieldstat where match_id = 732; delete from stats_teamstat where match_id = 732;
delete from stats_playerstat where match_id =  732 and stat_name like 'selection_%'; COMMIT;


-- M8
BEGIN; delete from stats_predictionfieldstat where match_id = 733; delete from stats_teamstat where match_id = 733; delete from stats_playerstat where match_id =  733 and stat_name like 'selection_%';


-- M9
BEGIN; delete from stats_predictionfieldstat where match_id = 734; delete from stats_teamstat where match_id = 734;
delete from stats_playerstat where match_id =  734 and stat_name like 'selection_%';
