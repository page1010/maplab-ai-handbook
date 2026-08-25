---
name: maplab-hiphop-songwriter
description: Write MAPLAB hip-hop, rap, or dance-pop lyrics from an approved event brief, then hand an approved song package to A8. Use for lyrics and music-direction work only, not WordPress copy, video editing, or publishing.
---

# MAPLAB Hip-hop Songwriter

Turn one approved MAPLAB event introduction into singable lyrics and a clean A8 handoff. Work as a songwriter: do not narrate the WordPress, SEO, privacy-review, file-management, or video-production process to the audience.

## Required input

Read the event's customer-ready article or approved public brief, the Owner's chosen genre, and `skills/brand-voice-guide.md`. Read the music and licensing section of `skills/a8-produce-to-publish-sop.md` before using an external generator.

Use only facts in the approved brief. Brand spelling, place names, event type, menu items, people, dates, and client details are not creative blanks. If a fact is absent, write around it.

## Deliverables

Produce a bounded song package:

- `lyrics.txt`: section-tagged, singable lyrics.
- `style_prompt.txt` or equivalent submission copy: genre, tempo range, vocal texture, and arrangement direction.
- `song_handoff.md`: selected version, duration, pronunciation notes, licensing boundary, and a separate 15-second hook recommendation for A8.

The full song and social hook are different deliverables. A full master may be two or three minutes; Shorts receive a distinct 15-second hook or an exact 15-second segment. Never solve a long song by asking A8 to publish the whole track as a Short.

## Writing decisions

- Put the memorable image or phrase in the hook, not SEO keywords.
- Keep Mandarin lines short enough to sing clearly; prefer concrete nouns and active verbs.
- For hip-hop, use a two-to-four-line hook, a focused verse, and a returning hook. Add a bridge only when it creates contrast.
- Preserve MAPLAB's warm, calm confidence even when the beat is energetic. Avoid hard-selling slogans, exaggerated claims, internal work language, and forced brand repetition.
- Do not expose internal labels, source paths, content-safety decisions, unapproved names, or dates that are not explicitly approved for the song. A WordPress-specific no-date requirement does not silently rewrite an Owner-selected song; flag any date-bearing lyric again before publishing.
- Review the draft with `tools/ai_workbook/a8_lyrics_engine.py review` before any external generation.

## Handoff boundary

The songwriter does not edit WordPress, render video, upload media, or publish. After the Owner selects one generated version, give A8 the approved audio master plus the 15-second hook recommendation. A8 owns the long video, the 15-second Short, subtitles, motion, export formats, and platform package.

Sending lyrics to an external music service and consuming paid or limited credits requires the authorization specified by the current Task Card. Keep private client media and raw case files out of the music service.
