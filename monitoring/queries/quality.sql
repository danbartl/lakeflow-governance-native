SELECT
  workspace_id, pipeline_id, update_id,
  coalesce(rule.dataset, origin.dataset_name) AS dataset_name,
  rule.name AS rule_name,
  sum(rule.passed_records) AS passed_records,
  sum(rule.failed_records) AS failed_records
FROM system.lakeflow_pipeline_events_preview.pipeline_events
LATERAL VIEW explode(variant_get(details, '$.flow_progress.data_quality.expectations',
  'ARRAY<STRUCT<name:STRING,dataset:STRING,passed_records:BIGINT,failed_records:BIGINT>>')) e AS rule
WHERE workspace_id = '__WORKSPACE_ID__'
  AND pipeline_id = '__PIPELINE_ID__'
  AND event_type = 'flow_progress'
  AND event_time >= current_timestamp() - INTERVAL 7 DAYS
GROUP BY workspace_id, pipeline_id, update_id,
  coalesce(rule.dataset, origin.dataset_name), rule.name
