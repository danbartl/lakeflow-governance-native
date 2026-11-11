SELECT
  count(*) AS event_count,
  count_if(level = 'ERROR') AS error_events,
  CAST(max(event_time) AS STRING) AS last_event,
  CASE WHEN count(*) = 0 THEN 'NO_EVENTS'
       WHEN count_if(level = 'ERROR') > 0 THEN 'ERROR_EVENTS_PRESENT'
       ELSE 'EVENTS_PRESENT_NOT_A_QUALITY_APPROVAL' END AS evidence_status
FROM system.lakeflow_pipeline_events_preview.pipeline_events
WHERE workspace_id = '__WORKSPACE_ID__'
  AND pipeline_id = '__PIPELINE_ID__'
  AND event_time >= current_timestamp() - INTERVAL 7 DAYS
