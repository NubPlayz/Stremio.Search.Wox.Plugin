<h1 align="center">
  <img
    src="https://raw.githubusercontent.com/Stremio/stremio-brand/master/logos/PNG/stremio-logo-800px.png"
    width="70"
    alt="Stremio"
  />
  <br>
  Stremio Search for Wox
</h1>

<p align="center">
  A Wox plugin for searching and launching Stremio movies and TV shows.
  <br>
  Directly launch titles in the Stremio Desktop application or web player.
</p>

<p align="center">

  <a href="https://github.com/NubPlayz/Stremio.Search.Wox.Plugin/releases">
    <img src="https://img.shields.io/github/v/release/NubPlayz/Stremio.Search.Wox.Plugin?style=for-the-badge&logo=github&label=Release" alt="Latest Release">
  </a>

</p>

<p align="center">
  <img src="https://img.shields.io/badge/Wox-v2-7c3aed?style=flat-square&logo=wox&logoColor=white" alt="Wox">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Stremio-Plugin-8A2BE2?style=flat-square" alt="Stremio">
</p>



## Usage

Type the trigger keyword `sm` followed by your query:

```text
sm <query>
```
## Screenshots
### Search movies and shows directly from flow launcher & directly open it!
<img width="762" height="572" alt="image" src="https://github.com/user-attachments/assets/2b8f9942-ba78-4e83-8d33-5ffee337c468" />

### Click Or Enter to open it in Stremio App directly !

<img width="1535" height="811" alt="image" src="https://github.com/user-attachments/assets/b7a038ba-5273-4e09-a26c-66d97ef7de72" />

### Or open it in Stremio Web!

<img width="1532" height="764" alt="image" src="https://github.com/user-attachments/assets/ca0dc5f0-ebed-40de-bc2c-b21185ecbc51" />

### All actions

<img width="362" height="444" alt="image" src="https://github.com/user-attachments/assets/c14577dd-43e1-4d63-a449-cada08fc361a" />

### View your local library directly from Wox

<img width="805" height="576" alt="image" src="https://github.com/user-attachments/assets/6a9ba61e-08f5-473c-a676-591347aafb55" />

## Features

- **Instant Local & Online Search**: Seamlessly search both your personal Stremio library and the global Cinemeta catalog.
- **Deep-linking to Stremio Desktop**: Press Enter to immediately open the title in the Stremio Desktop client.
- **Actions**:
  - **Open in Stremio Desktop** (Default action)
  - **Open in Web Browser** (Launches `web.stremio.com`)
  - **Sync Stremio Library** 
  - **Copy Stremio App Link**
  - **Copy Stremio Web Link**
- **Automatic Authentication**: Discovers your local Stremio session token automatically from local storage on Windows.
- **Power User Mode**: Optional mode requiring `?` suffix to search the online catalog (e.g. `sm dune?`), keeping plain searches strictly local.





### Examples:
- `sm`  Shows your local library titles or prompts to sync if empty.
- `sm dune`  Searches for "dune" across your local library and the Stremio catalog.
- `sm severance`  Finds and opens TV series.



## Power User Mode

Enable **"Require '?' for online catalog search"** in Wox Settings:

- `sm dune`  Searches your local Stremio library only (no network requests / API calls to Cinemeta).
- `sm dune?`  Queries the online Cinemeta catalog i.e Stremio Catalog Search. 

<h2>
  <img
    src="https://www.google.com/s2/favicons?domain=flowlauncher.com&sz=64"
    width="42"
    height="42"
    alt="Flow Launcher"
  />
  Stremio Search for Flow Launcher
</h2>


This **Stremio Search** plugin is also available for [Flow Launcher](https://www.flowlauncher.com/).

The [**Github link**](https://github.com/NubPlayz/Stremio-search-flowLauncher-plugin) for Stremio Search flow.

Search and launch Stremio movies and TV shows directly from Flow Launcher.
