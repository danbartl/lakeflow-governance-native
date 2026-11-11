# Native Pipeline-Unit-Tests

Dies ist der primaere Testweg fuer DQ und Silver. Keine Polars-/SQLite-
Nachimplementierung der Pipeline. Die Tests verwenden dieselbe `pipeline.py`
wie der Integrationstest, aber ohne `bronze_pipeline.py` im Pipeline-Graphen.
`accounts_bronze` ist hier ausschliesslich eine gemockte Tabelle.

## Einrichtung

1. Das Bundle mit den Sandbox-Variablen aus dem First-Slice-Runbook konfigurieren.
   Fuer dieses Target ein eigenes Sandbox-Schema waehlen. Ein `source_path`
   ist nicht erforderlich; sein leerer Standardwert ist nur hier zulaessig.
2. `databricks bundle validate -t native-tests` und
   Plan und Deployment mit `-t native-tests` gemaess First-Slice-Runbook ausfuehren.
   In den Pipeline Settings
   kontrollieren: einzige Quelldatei `pipeline.py`, keine Bronze-Datei, kein Glob
   ueber Testdateien. Den Source-Selektor nicht ueberschreiben.
3. Im Web-Editor dieser Pipeline ueber **Add > Test** eine Testdatei anlegen und
   den versionierten Inhalt von `test_pipeline.py` dort verwenden. Sie darf nicht
   als regulaere Pipeline-Quelldatei registriert sein. Aenderungen am Test wieder
   mit der Repository-Datei abgleichen; kein zweiter fachlicher Testbestand.
4. Triggered-Modus, DBR mindestens 18.1 und Verfuegbarkeit der Beta pruefen.
   Pipeline-Owner sowie USE CATALOG und CREATE SCHEMA sind erforderlich.
   Spark-Connect-basierte Environment Versions sind derzeit nicht kompatibel.
5. Tests im Editor einzeln oder als Datei ausfuehren. Keinen normalen Update
   parallel starten. Die Unit-Test-Pipeline nicht mit `bundle run` starten:
   ihre Eingabetabelle entsteht erst durch die Test-Fixture.

Die unqualifizierten Tabellennamen beziehen sich auf den Default-Katalog und
das Default-Schema der Pipeline. Im ersten Lauf die Umleitung in das temporaere
Testschema kontrollieren. Keine Pfadzugriffe, Connectoren oder Governance-DDL
in diese Tests aufnehmen. Bronze, UC-Berechtigungen und Recovery bei echten
Dateilieferungen bleiben separate Sandbox-Integrationstests.

## Bronze mit echten Parsern und gemockten Dateien

Das neue Target `bronze-tests` verwendet dieselben Bronze- und Silver-Dateien.
Es setzt PREVIEW fuer den aktuellen Funktionsumfang; vor Ausfuehrung DBR 18.3+
und ein Environment ohne Spark Connect pruefen. Kein weiterer Preview-Antrag
im Code: fehlende Funktionen schlagen sichtbar fehl.

1. Eigenes Sandbox-Schema setzen und das Target `bronze-tests` planen/deployen.
   `slice.source_path` nicht ueberschreiben. Der Pfad bezeichnet ausschliesslich
   einen synthetischen Testeingang, keine produktive Volume-Quelle.
2. Im Editor ausschliesslich `test_bronze.py` als Testdatei anlegen. Nicht die
   Silver-Mock-Tests parallel ausfuehren: sie schreiben dieselbe Bronze-Tabelle.
3. Der Test registriert `mock_cloud_path` vor jedem ersten Lauf und verwendet
   hochgeladene CSV-Fixtures aus `${workspace.file_path}/fixtures`. Kein Upload
   in einen echten Eingangsordner erforderlich.
4. Geprueft werden Bronze bis SCD1/SCD2, Dateizuordnung, Typen, Quarantaene und
   Wiederanlauf. Ein weiterer Test erwartet einen Parserfehler beim ungueltigen
   BIGINT. Falls die Plattform den Fehler stattdessen rettet, ist der Test rot:
   Parser-/Rescue-Policy klaeren, nicht die Assertion still entfernen.

`/Volumes/` ist keine automatische Sicherheitsgrenze fuer ungemockte Reads.
Deshalb eigenes Target, synthetischer Quellpfad und kein Fallback bei fehlendem
Mock-API. Diese Tests ersetzen keine Rechte-, Maskierungs- oder Recovery-Tests.
Fuer Laufzeitmessungen ersten und zweiten Lauf getrennt protokollieren.

## Nachweisgrenze

Lokal werden diese Tests durch `tests/conftest.py` nicht gesammelt. Im Web-Editor
wird das native Modul direkt importiert: fehlt es, schlaegt der Test sichtbar
fehl, statt als Skip zu verschwinden. Der native Lauf steht noch aus. Zu pruefen sind
weiterhin widerspruechliche Sequenzen in Folgeinkrementen.
Die vorhandenen Tests decken Updates, Deletes, verspaetete Ereignisse, Neustart
ohne neue Daten, exaktes Replay, Silver-Datentypen und die fachliche Aufteilung
in gueltige/ungueltige Zeilen ab. DQ-Schreibmengen werden direkt gegen
`status.flow_info` geprueft; fehlende Metriken gelten nicht als Erfolg.

[Databricks-Referenz](https://docs.databricks.com/aws/en/ldp/unit-testing),
erneut geprueft am 11. November 2026. Aktuell Editor-Ausfuehrung, kein lokaler Ersatz fuer Spark.
