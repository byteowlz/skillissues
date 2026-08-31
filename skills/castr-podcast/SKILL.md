---
name: castr-podcast
description: "Manage podcast episodes, scripts, sources, and comments in CastR via its REST API. Use when working with podcast episodes, writing or editing scripts, adding research sources, managing comments, importing/exporting markdown scripts, or interacting with CastR in any way."
---

# CastR Podcast Management Agent Skill

Triggers: "podcast", "episode", "script", "castr", "show notes", "sources for episode",
"add a block", "write the intro", "podcast script", "episode prep".

## Authentication

All API calls use a **service account API key** with the `castr_sa_` prefix.

The key must be set as environment variable `CASTR_API_KEY` or stored in the user's config.
If no key is available, ask the user to provide one.

```bash
# All requests use Bearer auth
curl -H "Authorization: Bearer $CASTR_API_KEY" https://castr.app/api/v1/...
```

**Base URL**: Use environment variable `CASTR_URL` if set, otherwise `https://castr.app`.

## Data Model

- **Show**: A podcast series (e.g., "OUTATIME"). Has hosts (speakers).
- **Episode**: One installment of a show. Has metadata, blocks, sections, sources, comments, scratchpad.
- **Section**: Named chapter within an episode (e.g., "Intro", "Main Discussion", "Outro"). Has a color and position.
- **Block**: A script block -- one speaker's text within a section. Has speaker_id, content (markdown), position.
- **Source**: Research link, video, note, etc. attached to an episode.
- **Comment**: Listener comment from any platform (YouTube, Spotify, agent-created).
- **Scratchpad**: Working notes, ideas, todos attached to an episode.
- **Speaker**: A person who appears on the podcast (host or guest). Has id, name, slug, type.

## API Reference

### Shows & Speakers (read-only)

```bash
# List all shows
curl -H "Authorization: Bearer $CASTR_API_KEY" "$CASTR_URL/api/v1/shows"
# Response: { "shows": [{ "id", "slug", "title", "description", "episode_count", "hosts": [...] }] }

# List all speakers
curl -H "Authorization: Bearer $CASTR_API_KEY" "$CASTR_URL/api/v1/speakers"
curl -H "Authorization: Bearer $CASTR_API_KEY" "$CASTR_URL/api/v1/speakers?type=host"
curl -H "Authorization: Bearer $CASTR_API_KEY" "$CASTR_URL/api/v1/speakers?type=guest"
# Response: { "speakers": [{ "id", "name", "slug", "type", "avatar", "bio", "active" }] }
```

### Episodes

```bash
# List all episodes
curl -H "Authorization: Bearer $CASTR_API_KEY" "$CASTR_URL/api/v1/episodes"
# Response: { "episodes": [{ "id", "title", "show_id", "show_title", "episode_number", ... }] }

# Get full episode (includes blocks, sections, sources, comments, scratchpad, speakers)
curl -H "Authorization: Bearer $CASTR_API_KEY" "$CASTR_URL/api/v1/episodes/EPISODE_ID"

# Create episode
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "Episode Title", "show_id": "SHOW_ID", "episode_number": 42}' \
  "$CASTR_URL/api/v1/episodes"

# Update episode metadata
curl -X PUT -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Title", "episode_number": 42, "published_on": "2026-03-15"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID"

# Delete episode
curl -X DELETE -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID"
```

### Script Blocks

Blocks are the core content units. Each block belongs to a speaker and optionally a section.
Blocks are ordered by `position` (integers, typically increments of 10).

```bash
# List blocks for episode
curl -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/blocks"

# Create block
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"speaker_id": "tommy", "content": "Welcome to the show!", "section_id": "SECTION_ID"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/blocks"

# Update block
curl -X PUT -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"block_id": "BLOCK_ID", "content": "Updated text", "speaker_id": "roman"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/blocks"

# Delete block
curl -X DELETE -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/blocks?block_id=BLOCK_ID"
```

### Sections

```bash
# List sections
curl -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/sections"

# Create section
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "Main Discussion", "color": "blue", "description": "Core topic"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/sections"

# Update section
curl -X PUT -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"section_id": "SECTION_ID", "title": "Renamed Section", "color": "red"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/sections"

# Delete section
curl -X DELETE -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/sections?section_id=SECTION_ID"
```

### Sources

Source types: `link`, `video`, `audio`, `image`, `note`

```bash
# List sources
curl -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/sources"

# Add source
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "link", "title": "Research Paper", "content": "https://example.com/paper", "notes": "Relevant to section 2"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/sources"

# Update source
curl -X PUT -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"source_id": "SOURCE_ID", "notes": "Updated notes"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/sources"

# Delete source
curl -X DELETE -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/sources?source_id=SOURCE_ID"
```

### Comments

```bash
# List comments
curl -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/comments"

# Create comment (e.g., agent leaving a review note)
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "This section needs more examples", "platform": "agent", "tags": ["review"]}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/comments"

# Resolve/tag a comment
curl -X PUT -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"comment_id": "COMMENT_ID", "is_resolved": true, "tags": ["addressed"]}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/comments"

# Delete comment
curl -X DELETE -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/comments?comment_id=COMMENT_ID"
```

### Scratchpad

Types: `note`, `todo`, `idea`, `question`

```bash
# List scratchpad items
curl -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/scratchpad"

# Add scratchpad item
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "idea", "title": "Talking point", "content": "Discuss the latest AI developments", "color": "blue"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/scratchpad"

# Update scratchpad item
curl -X PUT -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"item_id": "ITEM_ID", "content": "Updated content", "is_pinned": true}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/scratchpad"

# Delete scratchpad item
curl -X DELETE -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/scratchpad?item_id=ITEM_ID"
```

### Markdown Import/Export

The most powerful feature for agents. Export the entire episode script as markdown, or import
markdown to create/replace blocks.

```bash
# Export episode as markdown
curl -H "Authorization: Bearer $CASTR_API_KEY" \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/markdown"
# Add ?include_sources=true to also get sources in markdown format

# Import markdown (replace all blocks)
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "---\ntitle: Episode 42\n---\n\n# Intro\n\n## Tommy\n\nWelcome!\n\n## Roman\n\nHello!\n", "mode": "replace"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/markdown"

# Import markdown (append to existing)
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "## Tommy\n\nOne more thing...\n", "mode": "append"}' \
  "$CASTR_URL/api/v1/episodes/EPISODE_ID/markdown"
```

#### Markdown Format

The markdown format uses YAML frontmatter and headers:

```markdown
---
title: "Episode Title"
episode_id: abc123
episode number: 42
date of recording: 2026-03-01
published on: 2026-03-15
guests: Dr. Smith
youtube: <https://youtube.com/watch?v=...>
spotify: <https://open.spotify.com/episode/...>
apple podcasts: <https://podcasts.apple.com/...>
---

# Section Name [color: blue]

## speaker_id

Block content goes here. This is what the speaker says.
Supports **markdown** formatting.

## another_speaker_id

Their response or content.

# Another Section [color: red]

## speaker_id

More content in the next section.
```

**Key rules:**
- `# Header` = Section title (optional `[color: colorname]` suffix)
- `## Header` = Speaker ID (lowercase, e.g., `tommy`, `roman`, `ginee`)
- Everything after `## speaker` until the next `##` or `#` is the block content
- Frontmatter fields are optional but respected on import

## Common Workflows

### 1. Prepare a new episode

```bash
# 1. Get shows and pick the right one
curl -H "Authorization: Bearer $CASTR_API_KEY" "$CASTR_URL/api/v1/shows"

# 2. Create the episode
curl -X POST -H "Authorization: Bearer $CASTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "The Future of X", "show_id": "SHOW_ID", "episode_number": 15}' \
  "$CASTR_URL/api/v1/episodes"

# 3. Create sections
curl -X POST ... -d '{"title": "Intro", "color": "green"}'
curl -X POST ... -d '{"title": "Main Discussion", "color": "blue"}'
curl -X POST ... -d '{"title": "Outro", "color": "purple"}'

# 4. Import a full script via markdown
curl -X POST ... -d '{"markdown": "...", "mode": "replace"}'

# 5. Add research sources
curl -X POST ... -d '{"type": "link", "title": "Key Study", "content": "https://..."}'
```

### 2. Review and annotate an existing episode

```bash
# 1. Get full episode
curl "$CASTR_URL/api/v1/episodes/EPISODE_ID"

# 2. Export as markdown to read
curl "$CASTR_URL/api/v1/episodes/EPISODE_ID/markdown"

# 3. Leave review comments
curl -X POST ... -d '{"content": "The intro could be punchier", "tags": ["review"]}'

# 4. Add scratchpad notes
curl -X POST ... -d '{"type": "idea", "title": "Callback to episode 12"}'
```

### 3. Bulk update script content

```bash
# 1. Export current markdown
curl "$CASTR_URL/api/v1/episodes/EPISODE_ID/markdown" > episode.json

# 2. Edit the markdown content

# 3. Re-import with replace mode
curl -X POST ... -d '{"markdown": "...", "mode": "replace"}'
```

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

Common error codes:
- `INVALID_API_KEY` (401) - Missing or invalid service account key
- `INSUFFICIENT_SCOPE` (403) - Key lacks required permission
- `RATE_LIMIT_EXCEEDED` (429) - Too many requests (default: 120/min)
- `NOT_FOUND` (404) - Resource not found
- `VALIDATION` (400) - Invalid request body
- `INTERNAL_ERROR` (500) - Server error

## Important Notes

- Speaker IDs are slugs like `tommy`, `roman`, `ginee` -- use `GET /api/v1/speakers` to discover them
- Block positions are integers; use increments of 10 to leave room for insertions
- The markdown import/export is the fastest way to create or update full scripts
- Service account actions are tracked via `created_by_sa_id` columns for audit
- Rate limit defaults to 120 requests/minute per service account
