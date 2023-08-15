# Hog Uploader

project for combining video clips into continuous files and uploading to youtube

[playlist](https://www.youtube.com/playlist?list=PLtZv6jHN_L88JZmqB7yhdxAtm3MEn3CQH)

## Usage

* Setup OAuth 2.0 Desktop Client in Google Cloud Platform
* Download OAuth Client JSON file and rename to `youtube_secrets.json`
* Move `youtube_secrets.json` to the root of this directory
* Add your video files into a folder called `input` in the root of this directory
* Run the following commands:

    ```
    poetry install
    poetry run hog [--upload-only]
    ```
    ```
    Options:
        --upload-only           Only uploads files in output folder to the YouTube playlist
    ```


