# Hog Uploader

project for combining video clips into continuous files and uploading to youtube

[playlist](https://www.youtube.com/playlist?list=PLtZv6jHN_L88JZmqB7yhdxAtm3MEn3CQH)

## Usage

* Setup OAuth 2.0 Desktop Client in Google Cloud Platform (GCP):
    * In GCP navigate to the Credentials page
    * Create credentials
    * OAuth client ID
    * Desktop app application type
* Download OAuth Client JSON file


* Run the following commands:

    ```
    uv sync
    uv run hog --input-dir input --output-dir output --upload --oauth-client-secrets-file client_secret_135093931493-kfb6t1nl7ir9063lelmcl1kkdsb3sne4.apps.googleusercontent.com.json --youtube-playlist-id PLtZv6jHN_L88JZmqB7yhdxAtm3MEn3CQH
    ```
    
## Help
```
usage: hog [-h] [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR] [--video-extension {.mp4,.mkv,.mov,.avi}]
           [--upload | --no-upload | --upload-only] [--oauth-client-secrets-file OAUTH_CLIENT_SECRETS_FILE]
           [--youtube-playlist-id YOUTUBE_PLAYLIST_ID]

options:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR
                        Directory containing input video files
  --output-dir OUTPUT_DIR
                        Output directory for raw, concatenated and uploaded videos
  --video-extension {.mp4,.mkv,.mov,.avi}
                        Extension of input and ouput video; defaults to .mp4
  --upload, --no-upload
                        Upload concatenated videos to YouTube; defaults to --upload
  --upload-only         Only upload videos that have been concatenated
  --oauth-client-secrets-file OAUTH_CLIENT_SECRETS_FILE
                        Path of the JSON file that contains the OAuth client secrets; required with --upload
  --youtube-playlist-id YOUTUBE_PLAYLIST_ID
                        YouTube playlist ID to add uploaded videos to; required with --upload
```


## Tests

```
uv run pytest
```