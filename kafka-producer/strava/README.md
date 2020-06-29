# Strava

## API v3

The Strava provider interface currently utilizes the following APIs:
* `/athlete/activities`
* `/activities/{id}`

## Web Scraping

### Mechanism
1. Scraping user ids of athletes' public profiles
2. Scraping public activity ids for each athlete
3. Scraping public information on athletes' activities (API only allows access to authorized users' activities)

## Activity Faker / Generator
Generating fake data in the format of Strava API v3 `/activities/{id}`.

*IMPORTANT: Not suited to anonymize activities*

### Mechanism


Generates fake numeric, geo and token data for a base example activity ([example-activity.json](kafka-producer/strava/example-activity.json)) with Python `Faker`, `random` and `secret` libraries while trying to maintain semantic data integrity.

Some data integrity aspects are verified on a very basic level for max, average and perturbed data fields (see [`def verify_data_integrity(activity)`](https://github.com/peng-data-minimization/fitness-data-pipeline/blob/develop/kafka-producer/strava/generator.py#L46-L49). For instance max data field values of activity subset (segment, lab or split) cannot be higher than of overall activity values. Also average data fields and perturbed data fields have of subactivities have to roughly add up overall activity values. If those integrity tests fail, activity data generation is re-run and integrity tests are retried. Still there is much to be improved.

### Goal

Used to put realistic load on the pipeline, test data minimization processing and data visualization.

### Currently generated data field
* `id`
* `athlete`
* `embed_token`
* `external_id`
* `achievement_count`
* `upload_id`
* `upload_id_str`
* `map`
* `type`
* `start_date`
* `start_date_local`
* `elapsed_time`
* `moving_time`
* `average_heartrate`
* `max_heartrate`
* `average_speed`
* `max_speed`
* `calories`
* `distance`
* `elev_low`
* `elev_high`
* `total_elevation_gain`
* `start_latitude`
* `start_longitude`
* `start_latlng`
* `end_latlng`
* `utc_offset`
* `timezone`
* `name`
* `segment['id']`
* `segment['activity']['id']`
* `segment['athlete']['id']`
* `segment['max_heartrate']`
* `segment['average_heartrate']`
* `segment['elapsed_time']`
* `segment['moving_time']`
* `segment['start_date']`
* `segment['start_date_local']`
* `lap['activity']['id']`
* `lap['athlete']['id']`
* `lap['max_heartrate']`
* `lap['average_heartrate']`
* `lap['max_speed']`
* `lap['average_speed']`
* `lap['distance']`
* `lap['elapsed_time']`
* `lap['moving_time']`
* `lap['calories']`
* `lap['start_date']`
* `lap['start_date_local']`
* `lap['total_elevation_gain']`
* `split['average_heartrate']`
* `split['average_speed']`
* `split['elapsed_time']`
* `split['moving_time']`
* `split['distance']`
* `split['elevation_difference']`