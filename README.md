# Restore Unsynced Vorbis Lyrics

A MusicBrainz Picard 3 plugin that keeps the `UNSYNCEDLYRICS` Vorbis comment
as its own tag, instead of merging it into `lyrics`.

## The problem

Picard 3.0 maps `UNSYNCEDLYRICS` to `lyrics` when it loads Vorbis comment
files ([PICARD-3199](https://tickets.metabrainz.org/browse/PICARD-3199)). If a file has synced lyrics in `LYRICS` and plain lyrics
in `UNSYNCEDLYRICS`, saving it writes both into `LYRICS`. The plain text
can end up as the first `LYRICS` comment, and players that read the first
one stop showing the synced lyrics. The original `UNSYNCEDLYRICS` tag is left
untouched, and edits to it no longer reach the file.

Example of a file saved without this plugin (values truncated):

```
UNSYNCEDLYRICS=<plain text...>
LYRICS=<plain text...>
LYRICS=[id: ...
```

## What this plugin does

- Re-reads the lyric tags from the file after load and keeps `lyrics` and
  `unsyncedlyrics` as separate tags (including `:description` variants).
- Adds `unsyncedlyrics` to the Edit Tag dialog's multi-line tag list, so
  line breaks survive editing.

With the plugin, the same file saves as:

```
UNSYNCEDLYRICS=<plain text...>
LYRICS=[id: ...
```

## Install

> [!NOTE]
> Picard warns that the plugin is not in the official registry. That is expected for third-party plugins. Restart Picard after installing, and remove and re-add any files that were already loaded.

Plugins options -> Install -> URL, or:
```
picard-cli plugins install --ref v1.0.0 https://github.com/Jeppevinkel/picard-restore-unsynced-lyrics
```

## Tested

- Picard 3.0.5
- FLAC files only. Ogg Vorbis and Opus are untested.
- Files with and without MusicBrainz release data.

## Limitations

- It re-reads each Vorbis file's tags once on load.
- The multi-line editor change patches a private Picard constant
  (`MULTILINE_TAGS`). If a future Picard version renames it, the plugin logs a
  warning and the rest keeps working.
- Back up your files and compare tags with `metaflac` before bulk saves.

## Repairing a file already saved with the merge

If a file was saved by Picard 3.0 without this plugin, `LYRICS` may contain an
extra copy of the plain text next to the synced lyrics. To fix it:

1. Work on a copy of the file, or make a backup.
2. Enable this plugin, then load the file in Picard.
3. Select the file and open **Edit Tag** on `lyrics`. Delete the value that
   is the plain (non-timestamped) text, and keep the synced one.
4. Save, then check the result:
   ```
   metaflac --export-tags-to=- "FILE.flac" | cut -c1-30 | grep -E '^(UNSYNCED)?LYRICS='
   ```
   You should see one `UNSYNCEDLYRICS=` and one `LYRICS=`.

## License

GPL-2.0-or-later