# EXO RP – FiveM Scripts

Hier verwalten wir die eigenen FiveM-Scripts für den Gaming4Free-Testserver.

- Eigene Ressourcen liegen unter `resources/[local]/`.
- Änderungen auf `main` starten den automatischen SFTP-Upload.
- Vor dem Upload müssen einmalig GitHub-Actions-Secrets eingerichtet werden.
- Der Workflow ändert nur die eigenen Ressourcen und verwaltet ausschließlich seinen gekennzeichneten Bereich in `server.cfg`. Er erstellt vor der ersten Änderung eine Sicherung.
- **Wichtig:** Ein SFTP-Upload führt keinen automatischen Neustart des FiveM-Servers aus. Neue Scripts sind nach einem Neustart verfügbar.

## Einmalige Verbindung zu Gaming4Free

Öffne **Settings → Secrets and variables → Actions** in diesem Repository und lege diese **Repository secrets** an:

| Name | Inhalt |
| --- | --- |
| `SFTP_HOST` | Hostname aus Gaming4Free → Server Settings → SFTP Information |
| `SFTP_PORT` | Port aus der SFTP-Verbindungsadresse |
| `SFTP_USERNAME` | Vollständiger SFTP-Benutzername |
| `SFTP_PASSWORD` | SFTP-Passwort, **nur als GitHub-Secret**, niemals in eine Datei oder einen Chat kopieren |
| `SFTP_HOST_FINGERPRINT` | Bestätigter SSH-Hostkey-Fingerabdruck des Hosting-Servers (Format: `SHA256:...`) |

Den Fingerabdruck vor der Freigabe mit Gaming4Free oder einer bereits von dir verifizierten SFTP-Verbindung abgleichen. Niemals blind einen unbekannten Fingerabdruck übernehmen.

**Optional:** Wenn das SFTP-Startverzeichnis nicht der Ordner mit `resources` und `server.cfg` ist, lege unter **Variables → Actions** die Variable `SFTP_REMOTE_ROOT` mit dem richtigen Startpfad an. Normalerweise reicht `.`.

Dann unter **Actions → Deploy EXO RP scripts → Run workflow** einmal starten. Bei Änderungen am Ordner `resources/` läuft der Upload danach automatisch.

## Test

Nach erfolgreichem Upload und einem Serverneustart in FiveM per F8 oder Chat `/exotest` ausführen.

## Sicherheit

Das Repository ist derzeit öffentlich: Lege keine Tokens, Passwörter, Lizenzschlüssel oder personenbezogene Daten in Dateien ab. Ändere `server.cfg` nicht hier im Repository, sondern ausschließlich über den markierten Bereich des Deployments. Die Verbindung über SFTP gibt keinen Zugriff auf den Hoster selbst oder seine Serverkonsole.
