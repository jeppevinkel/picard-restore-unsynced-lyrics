# -*- coding: utf-8 -*-
#
# Keep UNSYNCEDLYRICS and LYRICS as separate tags for Vorbis comment files,
# and give unsyncedlyrics the same multi-line editor as lyrics.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import mutagen

from picard.formats.vorbis import VCommentFile
from picard.plugin3.api import PluginApi

LYRICS = 'lyrics'
UNSYNCED = 'unsyncedlyrics'

_added_multiline = False


def _base(key):
    """Return 'lyrics' or 'unsyncedlyrics' if key belongs to one of those
    families (including 'name:description' variants), else None."""
    for base in (UNSYNCED, LYRICS):
        if key == base or key.startswith(base + ':'):
            return base
    return None


def _read_raw_lyrics(filename):
    """Read lyrics-family Vorbis comments straight from the file.

    Returns {lowercased_key: [values]}, or None if the file can't be read.
    """
    try:
        audio = mutagen.File(filename)
    except Exception:
        return None
    if audio is None or audio.tags is None:
        return None
    raw = {}
    for key, value in audio.tags:  # Vorbis comments are (key, value) pairs
        lkey = key.lower()
        if _base(lkey) is None:
            continue
        raw.setdefault(lkey, []).append(value)
    return raw


def _apply(metadata, raw):
    """Replace every lyrics/unsyncedlyrics key in metadata with the raw values."""
    for key in list(metadata.keys()):
        if _base(key) is not None:
            del metadata[key]
    for key, values in raw.items():
        metadata[key] = values


def file_post_load_processor(api: PluginApi, file):
    if not isinstance(file, VCommentFile):
        return
    raw = _read_raw_lyrics(file.filename)
    if not raw:
        return
    # Nothing was merged unless the file actually has an UNSYNCEDLYRICS tag.
    if not any(_base(key) == UNSYNCED for key in raw):
        return
    _apply(file.metadata, raw)
    _apply(file.orig_metadata, raw)  # so the file isn't shown as modified
    api.logger.debug("Kept %s separate from %s for %s", UNSYNCED, LYRICS, file.filename)


def _add_multiline_editor(api: PluginApi):
    """Make the Edit Tag dialog use its multi-line editor for unsyncedlyrics."""
    global _added_multiline
    try:
        from picard.ui.metadatabox import edittagdialog
        tags = edittagdialog.MULTILINE_TAGS
        if UNSYNCED not in tags:
            tags.add(UNSYNCED)  # mutate in place, don't rebind
            _added_multiline = True
    except Exception as e:
        api.logger.warning("Could not enable multi-line editing for %s: %s", UNSYNCED, e)


def enable(api: PluginApi):
    api.register_file_post_load_processor(file_post_load_processor)
    _add_multiline_editor(api)


def disable():
    global _added_multiline
    if _added_multiline:
        try:
            from picard.ui.metadatabox import edittagdialog
            edittagdialog.MULTILINE_TAGS.discard(UNSYNCED)
        except Exception:
            pass
        _added_multiline = False