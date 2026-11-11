# Natives Pipeline-Board

Eigenes Bundle, keine Abhaengigkeit der Ingestion. Drei Tabellen zeigen
Betriebsstatus, Expectations je Update und Fehler der letzten sieben Tage.
Keine eigene Event-Kopie, keine neue Datenbank und kein App-Server.

Vom Repository aus mit der vorhandenen Python-Umgebung:

```powershell
uv run python monitoring/build.py --workspace-id 1234 --pipeline-id <pipeline-uuid>
cd monitoring
$env:BUNDLE_VAR_warehouse_id = '<warehouse-id>'
databricks bundle validate
databricks bundle plan -o json | Out-File -Encoding utf8NoBOM .databricks/plan.json
if ($LASTEXITCODE -ne 0) { throw 'Plan fehlgeschlagen' }
Get-Content .databricks/plan.json
databricks bundle deploy --plan .databricks/plan.json
```

PowerShell 7; CLI 1.25.0. IDs stammen aus dem echten Sandbox-Lauf. Die Build-Datei
ist ignoriert und muss vor jedem Deployment erzeugt werden. Nach Aenderungen
erneut bauen und planen. Erst den Entwurf pruefen, dann im Workspace freigeben.
Keine Credentials in ein geteiltes Dashboard einbetten. SQL-Filter sind keine
Berechtigungsgrenze; Systemtabellenrechte und Dashboard-Freigaben separat setzen.

`NO_EVENTS` bedeutet fehlenden Nachweis, nicht fehlerfreie Daten. Auch ein Lauf
ohne Fehler ist keine fachliche Abnahme. DQ-Werte sind regelbezogene Zaehler und
duerfen nicht ueber verschiedene Regeln zu einer Anzahl fehlerhafter Zeilen
addiert werden. Fehlende erwartete Regeln muessen separat in der Abnahme auffallen.

Quelle: [native Events und Dashboard](https://docs.databricks.com/aws/en/ldp/monitor-and-query-events).
Die drei SQL-Dateien kapseln den aktuellen Systemtabellenpfad. Lokal werden
Struktur und Begrenzung geprueft, nicht Databricks-SQL-Ausfuehrung oder Rendering.
