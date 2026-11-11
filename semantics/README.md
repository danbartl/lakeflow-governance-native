# Fachliche Begriffe nativ publizieren

Der PoC verwendet Pages, keinen eigenen Glossar-Server. `publish.py` erzeugt
standardmaessig nur den REST-Aufruf als JSON. Das Beispiel enthaelt ausschliesslich
synthetische Definitionen. Eine vorhandene Testdomaene und deren Resource-ID sind
Voraussetzung; der Publisher vergibt keine Rechte und legt keine Domaene an.

```powershell
$domain = 'domains/<domain-uuid>'
$request = [guid]::NewGuid().ToString()
uv run python semantics/publish.py semantics/concepts/account-balance.json --domain $domain --request-id $request
# Nach Pruefung denselben Request mit --apply ausfuehren:
uv run python semantics/publish.py semantics/concepts/account-balance.json --domain $domain --request-id $request --apply --profile bank
```

Request-ID fuer Wiederholungen aufbewahren; sie ist pro neuem Begriff neu zu
erzeugen. Die Antwort enthaelt `name: pages/<uuid>`. Fuer spaetere Aenderungen
`--page-name pages/<uuid>` statt `--request-id` verwenden. Ein wiederholtes Create
mit derselben Request-ID aktualisiert keinen geaenderten Inhalt. Neue Pages sind
Entwuerfe; `--publish` publiziert explizit. Updates erhalten den Publikationsstatus.
Der Publisher prueft bei Updates Domaene und concept-id, bevor er Inhalte ersetzt.
Er bietet keine transaktionale Sperre gegen parallele UI-Bearbeitung.

Fuer diesen PoC ist Git die fuehrende Quelle der beschriebenen Felder; Pages ist
die Publikation. Keine parallelen manuellen Aenderungen daran vornehmen. Ein
spaeterer Stewardship-Betrieb kann Pages als fuehrend festlegen, dann entfaellt
der Git-Publisher fuer diese Felder. Kein bidirektionaler Sync.

Tabellen-Wikis werden nativ in Catalog Explorer gepflegt. Das Beispiel unten
kann dort als Entwurf erprobt werden; eine Wiki-API wird hier nicht erfunden.
Asset-Verweise im Beispiel sind Text, keine implementierten Asset-Link-API-Objekte.
Governed Tags, Spaltenrechte, Korrekturfreigaben und fachliche Versionsauswahl
bleiben eigenstaendige Anforderungen. Der Publisher zertifiziert keine Daten.

Vor echten Inhalten: Publikationsrechte einschraenken, Klassifikation und
Datenresidenz pruefen. Preview-Status verhindert den Versuch nicht; sensible
Inhalte bleiben ausgeschlossen. Keine produktiven Daten in Pages oder Wikis.

Referenz: [Pages REST API](https://docs.databricks.com/api/knowledge/v1/page).
Lokal sind Request-Form, Wiederholbarkeit und Schutz vor fremden Updates getestet;
die Workspace-API wurde noch nicht aufgerufen.
