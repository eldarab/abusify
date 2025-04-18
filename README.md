# Abusify

Notebook friendly Spotify downloader.

## Setup

### 1. Create a Spotify App

* Open a Spotify account.
* Create a new Spotify app called *abusify* using this link [https://developer.spotify.com/dashboard/create](https://developer.spotify.com/dashboard/create). 
* Copy the *Client ID* and *Client secret*, you will use them in the next step.

### 2. Setup Google Drive

In your Google Drive root folder, create a file called `.env-spotify-client` that looks like this example. 
Make sure to replace the client id and secret with your app's credentials. 

```text
SPOTIFY_CLIENT_ID=e5a6cb439d8a6cb5a456c93e6a5c48ba
SPOTIFY_CLIENT_SECRET=554636aab8459c5e96aeba438cba6cdc
```

### 3. Setup Google Colab

* Open [Google Colab](https://colab.research.google.com/).
* Create a new notebook called *abusify.ipynb*.

### 4. Install `abusify`

Execute this one-liner in the first cell of your notebook:

```shell
!rm -rf abusify && git clone https://github.com/eldarab/abusify.git && cd abusify && pip install .
```

### 5. Setup `abusify`

Execute this code in the second cell of your notebook.

```python
from google.colab import drive
from pathlib import Path
from dotenv import load_dotenv

drive.mount('/content/drive', force_remount=True)

DRIVE_ROOT    = Path("/content/drive") / "MyDrive"
MUSIC_DIR     = DRIVE_ROOT / "music"
LOGS_DIR      = DRIVE_ROOT / "logs"
ENV_FILE      = DRIVE_ROOT / ".env-spotify-client"

load_dotenv(ENV_FILE)

from abusify import configure_logging
configure_logging(
    logs_dir=LOGS_DIR,
    level="INFO",
    log_filename="abusify.log"
)

from abusify import Abusify
app = Abusify(MUSIC_DIR)
```

## Usage

Download `track` / `album` / `artist` / `playlist`:

```python
from abusify import EntityType
app.download("שיר אהבה בדואי צליל מכוון", EntityType.TRACK)
```

Download a direct link obtained from a Google or Spotify search:

```python
app.download("https://open.spotify.com/track/35yPWAgABmbcHvS6u1m6Gh?si=9f35ca9f0b13448c")
```