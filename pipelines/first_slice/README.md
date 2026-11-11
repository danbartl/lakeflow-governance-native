# Erster nativer Durchlauf

**Teststrategie ab 17. Oktober:** [Native Pipeline-Unit-Tests](tests/native/README.md)
sind der Standard fuer Verarbeitungslogik. Der unten beschriebene Dateidurchlauf
bleibt ein Integrationstest. Lokal pruefen wir nur Konfiguration, nicht CDC oder DQ
mit einer zweiten Engine. Der Vertrag bleibt metadata-driven und verbindlich.

Dies ist ab jetzt der empfohlene Einstieg. Ein synthetischer Datenbestand,
ein JSON-Vertrag, eine direkte Lakeflow-Pipeline, ein Bundle. Kein Compiler,
kein Wheel-Build, kein SDP-META, keine Spark-Installation fuer lokale Tests.
Nur fuer eine isolierte Entwicklungsumgebung; keine Produktionsfreigabe.

## Lokal

Vom Repository-Verzeichnis:

```powershell
uv sync --frozen
uv run pytest pipelines/first_slice/tests -q
```

Die lokalen Tests pruefen die Konfiguration. Native Testdateien werden lokal
nicht gesammelt und nicht als bestanden gewertet.

## Databricks

Voraussetzungen: CLI 1.25.0, Workspace-Login, Serverless-Pipelines, vorhandener Sandbox-
Katalog, Berechtigungen zum Anlegen von Tabellen sowie ein beschreibbares UC Volume.
Ein neues Schema und einen leeren Lieferordner nur fuer diesen Versuch verwenden.
Die Quelle muss CSV-Aenderungsereignisse liefern, keine Vollabzuege.

Die folgenden Befehle verwenden PowerShell 7 (Plan-JSON ohne UTF-8-BOM).

```powershell
cd pipelines/first_slice
databricks auth login --host https://<workspace-host>
$env:BUNDLE_VAR_catalog = '<sandbox_catalog>'
$env:BUNDLE_VAR_schema = '<fresh_sandbox_schema>'
$env:BUNDLE_VAR_source_path = '/Volumes/<catalog>/<schema>/<volume>/<fresh_folder>'
$env:BUNDLE_VAR_owner = '<responsible_team>'
databricks fs mkdirs "dbfs:$env:BUNDLE_VAR_source_path"
databricks fs cp fixtures/01.csv "dbfs:$env:BUNDLE_VAR_source_path/01.csv"
databricks bundle validate
New-Item -ItemType Directory -Force .databricks | Out-Null
databricks bundle plan -o json | Out-File -Encoding utf8NoBOM .databricks/plan.json
if ($LASTEXITCODE -ne 0) { throw 'Bundle-Plan fehlgeschlagen' }
Get-Content .databricks/plan.json
# Erst nach Pruefung der geplanten Aenderungen ausfuehren:
databricks bundle deploy --plan .databricks/plan.json
databricks pipelines dry-run accounts
databricks pipelines run accounts
```

Im Workspace ein Notebook im bereitgestellten Bundle-Dateiverzeichnis oeffnen,
den Zielkatalog und das Zielschema mit `USE CATALOG` / `USE SCHEMA` auswaehlen:

```python
from verify import verify

verify(spark, "after_01")
```

Danach lokal die zweite Datei liefern und erneut ausfuehren:

```powershell
databricks fs cp fixtures/02.csv "dbfs:$env:BUNDLE_VAR_source_path/02.csv"
databricks pipelines run accounts
```

Im Notebook `verify(spark, 'after_02')` ausfuehren. Die zweite Lieferung prueft
Update, Delete und eine verspaetete Aenderung. Danach ohne neue Datei erneut
starten und dieselben Sollwerte pruefen. Kein Full Refresh zwischen den Stufen.
Die Pruefung benoetigt Notebook-Compute; sie ist bewusst kein weiterer Job-Runner.

Bei reinen Codeaenderungen `databricks bundle sync --watch` in einem Terminal,
`databricks pipelines run accounts` im zweiten. Aenderungen an Bundle-Ressourcen
erfordern einen neuen Plan und anschliessend `deploy --plan`. Ein Regelwechsel
ist noch nicht Teil dieser Abnahme.

## Deployment-Werkzeuge

Die Bundles verwenden explizit die Direct Engine und verlangen CLI 1.25.0;
der lokale CI-Workflow installiert dieselbe Version. Unter Windows
laesst sich eine vorhandene Installation mit
`winget upgrade --id Databricks.DatabricksCLI --exact --version 1.25.0`
aktualisieren. Anschliessend `databricks version` pruefen.

Vor jedem Deployment einen Plan erzeugen und pruefen.
Ziel, Profil und Variablen bei Plan und Deployment identisch halten;
bei Aenderungen an Code, Konfiguration oder Ziel einen neuen Plan erzeugen.
Plan-Dateien koennen sensible Konfigurationswerte enthalten: nicht committen oder
ungeprueft als CI-Artefakte veroeffentlichen. `.databricks/` ist bereits ignoriert.

Bestehender Terraform-Bundle-State wird beim Deployment automatisch migriert.
Zuerst im isolierten Entwicklungsziel qualifizieren, bestehende Bundle-Namen und
Workspace-Pfade beibehalten und insbesondere Loeschungen/Neuanlagen im Plan pruefen.
Bei Migrationsfehlern abbrechen und Ursache klaeren; keinen State loeschen und
keinen Full Refresh als Reparatur verwenden. CLI 1.25.0 bietet keinen Terraform-
Fallback. Diese Migration wurde hier ohne Workspace-Zugang nicht ausgefuehrt.

Grundlage: [Direct Engine](https://docs.databricks.com/aws/en/dev-tools/bundles/direct).
Native Pipeline-Tests bleiben separat im Web-Editor auszufuehren; ein erfolgreicher
Plan ersetzt weder diese Tests noch den Datei-Integrationstest.

## Grenzen und naechste Entscheidung

Weitere Entwicklungswege sind vorbereitet: [Bronze-Mocking](tests/native/README.md),
[Recovery mit Rewind](recovery.md), [natives DQ-Board](../../monitoring/README.md)
und [native Fachbegriffe](../../semantics/README.md). Preview-Status allein ist
kein Ausschlusskriterium. Verfuegbarkeit und reale Ausfuehrung werden trotzdem
geprueft; ein Channel-Name garantiert keine konkrete Runtime-Unterversion.

Die beiden Silver-Ziele verwenden `cluster_by_auto=True`: die Plattform waehlt
Clustering-Schluessel, statt dass wir Partitionierungslogik pflegen. Benoetigte
Workspace-Freigaben fuer automatisches Liquid Clustering vor dem Lauf pruefen.
Das ist kein Performanceversprechen fuer kleine Fixtures.
Details zu Auswahl und bewusst nicht eingebauten Features:
[Architekturentscheidungen](../../docs/decisions/README.md).

- Owner, Domaene, Quelle und Vertragsversion werden als Tabellenproperties erfasst,
  nicht als UC Governed Tags oder Berechtigungsrichtlinien.
- Dateipfad und Verarbeitungszeit bleiben in Bronze erhalten; Silver enthaelt
  nur fachliche Spalten. Eine vollstaendige Berichts-Lineage ist nicht implementiert.
- Der CSV-Parser ist auf FAILFAST eingestellt; das Zusammenspiel mit Auto Loaders
  Datenrettung bei Typfehlern ist noch nativ zu pruefen. Fachlich ungueltige Zeilen
  gehen in Quarantaene. Gleiche Schluessel/Zeitpunkte mit widerspruechlichen Werten sind
  nicht qualifiziert und muessen im Liefervertrag ausgeschlossen werden.
- Bitemporalitaet, Excel/ZIP, DQX, App, Security und Zertifizierung sind vertagt,
  nicht abgeschafft. Kein BCBS-239-Konformitaetsnachweis.
- Lauf-IDs, Ergebnisse und Fehler des ersten Versuchs manuell protokollieren.
  Erst danach den Umfang des naechsten Inkrements festlegen.
- `bundle destroy` ersetzt keine bewusste Bereinigung der erzeugten UC-Daten.

Native Ausfuehrung hier noch nicht erfolgt: Es fehlen Databricks-Zugangsdaten.
API-Grundlage: [AUTO CDC](https://docs.databricks.com/aws/en/ldp/cdc) und
[Bundle-Beispiele](https://docs.databricks.com/aws/en/dev-tools/bundles/examples).
