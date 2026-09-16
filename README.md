# Stremio Search for Wox

A fast, lightweight Wox v2 plugin for searching your local Stremio library and the Cinemeta online catalog, directly launching titles in the Stremio Desktop application or web player.

## Features

- **Instant Local & Online Search**: Seamlessly search both your personal Stremio library and the global Cinemeta catalog.
- **Deep-linking to Stremio Desktop**: Press Enter to immediately open the title in the Stremio Desktop client.
- **Comprehensive Actions**:
  - **Open in Stremio Desktop** (Default action)
  - **Open in Web Browser** (Launches `web.stremio.com`)
  - **Sync Stremio Library** (Forces immediate background synchronization with your Stremio account)
  - **Copy Stremio Link** / **Copy Web Link** (Copies shareable URL to clipboard)
- **Automatic Authentication**: Discovers your local Stremio session token automatically from local storage on Windows.
- **Power User Mode**: Optional mode requiring `?` suffix to search the online catalog (e.g. `sm dune?`), keeping plain searches strictly local.


## Usage

Type the trigger keyword `sm` followed by your query:

```text
sm <query>
```

### Examples:
- `sm`  Shows your local library titles or prompts to sync if empty.
- `sm dune`  Searches for "dune" across your local library and the Stremio catalog.
- `sm severance`  Finds and opens TV series.



## Power User Mode

Enable **"Require '?' for online catalog search"** in Wox Settings:

- `sm dune`  Searches your local Stremio library only (no network requests / API calls to Cinemeta).
- `sm dune?`  Queries the online Cinemeta catalog i.e Stremio Catalog Search. 

