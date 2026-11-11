# Synthetische Kontohistorie

Die Tabelle `accounts_history` ist ausschliesslich ein Entwicklungsbeispiel.
Sie enthaelt die nach Ereignisreihenfolge historisierten Betraege synthetischer
Konten. `account_id` ist der fachliche Schluessel. `amount` ist ein ganzzahliger
Betrag in Minor Units; es ist keine Waehrungsumrechnung enthalten.

`__START_AT` und `__END_AT` begrenzen das halboffene Gueltigkeitsintervall in
Sequenznummern, nicht in Kalenderzeit. Ein leeres Ende bezeichnet eine aktive
Version. Rueckwirkende Ereignisse koennen die Historie korrigieren. Diese Tabelle
speichert keine zusaetzliche Systemzeit und ist daher nicht bitemporal.

Quelle: synthetische CSV-Lieferungen des First Slice. Fachlicher Begriff:
`sandbox.account_balance`. Technischer Vertrag: `pipelines/first_slice/dataset.json`.
Fehlerhafte fachliche Ereignisse werden in `accounts_quarantine` ausgesondert.
Ein erfolgreicher Lauf ist keine fachliche oder regulatorische Freigabe.
