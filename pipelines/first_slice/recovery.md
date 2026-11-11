# Rewind im Entwicklungsziel

Target `recovery` aktiviert Rewind auf PREVIEW. Ein eigenes Schema und ein
eigenes beschreibbares Volume verwenden; keine Nutzung produktiver Quellen.
Dies ist ein vorbereiteter manueller Versuch, kein bereits bestandener Test.

1. Mit `-t recovery` planen und deployen; Fixture `01.csv` wie im Runbook liefern.
2. Pipeline erfolgreich ausfuehren, `verify(spark, 'after_01')` pruefen und einen
   verfuegbaren Rewind-Punkt im Workspace feststellen. Dessen ID/Zeit und Update-ID
   festhalten. Ohne vorhandenen Punkt nicht mit dem Fehlerexperiment beginnen.
3. Fixture `02.csv` liefern, erneut ausfuehren und `after_02` pruefen.
4. Pipeline anhalten, falls ein Update laeuft. Im Workspace auf den unter Schritt 2
   dokumentierten Punkt zuruecksetzen. Vor dem Replay `after_01` pruefen.
5. Ohne Full Refresh erneut starten. Die zweite Datei muss erneut verarbeitet
   werden; `after_02` muss stimmen. Noch einmal ohne neue Lieferung starten:
   weder doppelte Historie noch zusaetzliche Bronze-Zeilen.
6. Punkt, Quellinventar, Tabellenstaende, Code-Commit, Update-IDs und Soll/Ist-
   Ergebnisse in der [Abnahmevorlage](../../docs/qualification-record.md) festhalten.

Quelldateien und Delta-Historie fuer den Versuch aufbewahren. Kein `VACUUM`,
Full Refresh oder manuelles Checkpoint-Loeschen zwischen den Schritten. Rewind
und Replay sind getrennte Operationen; nachgelagerte externe Verbraucher werden
nicht automatisch zurueckgesetzt. Bei falscher Transformation erst korrigierten
Code deployen, dann replayen. Der Versuch oben isoliert zunaechst den State-Restore.

Referenz: [Rewind](https://docs.databricks.com/aws/en/ldp/rewind).
