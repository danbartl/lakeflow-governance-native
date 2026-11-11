SELECT workspace_id, pipeline_id, update_id,
  CAST(event_time AS STRING) AS event_time, message
FROM system.lakeflow_pipeline_events_preview.pipeline_events
WHERE workspace_id = '__WORKSPACE_ID__'
  AND pipeline_id = '__PIPELINE_ID__'
  AND level = 'ERROR'
  AND event_time >= current_timestamp() - INTERVAL 7 DAYS
ORDER BY event_time DESC
