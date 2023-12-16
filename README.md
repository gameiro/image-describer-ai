# Google Drive Image Caption Enhancement

This Python script interacts with Google Drive, retrieves image files, and enhances their captions using various AI models provided by Google Cloud Platform (GCP) Vertex AI.

## Overview

The script performs the following actions:

1. **Initialization:**
   - Sets up logging and environment variables for configuration.
   - Initializes GCP Vertex AI for image and text processing.

2. **Functions:**
   - `download_image`: Downloads image content from Google Drive.
   - `convert_heic_to_png`: Converts HEIC images to PNG format.
   - `process_captions_async`: Processes captions asynchronously using a text generation AI model.
   - `process_image_caption_async`: Retrieves captions from images asynchronously using an image text model.
   - `process_images`: Processes images and their captions in parallel.
   - `get_all_files_from_drive`: Retrieves all image files from a specified Google Drive folder.
   - `chunks`: Splits a list into smaller chunks.

3. **Execution:**
   - Fetches image files from Google Drive.
   - Processes images and their captions, generating improved captions using Vertex AI Vision.
   - Creates a Markdown file containing the improved captions using Vertex AI Text model predict.
   - Generates a summary for a blog post based on the captions.
   - Store the summary file in the GCP Drive folder

4. **High Level:**
![Alt text](diagram.png)

## Usage

1. Set up the necessary environment variables:
   - `CAPTION_SHORT_TEXT_CONTEXT`: Context for caption enhancement.
   - `GCP_PROJECT_ID`: GCP project ID.
   - `GCP_DRIVE_FOLDER_ID`: Google Drive folder ID.
   - `GCP_DRIVE_FETCH_PAGE_SIZE`: Page size for fetching files (default is 100).

2. Run the script `python images_ai_blog_generator.py`.

## Requirements

- Python 3.x
- Google Cloud Platform (GCP) account and API credentials
- Installed Python packages: `google-cloud-aiplatform`, `google-api-python-client`, `Flask`, `heic2png`, `google-auth`

## Configuration

1. Obtain service account credentials for GCP.
2. Set up the `client_secrets.json` file.
3. Update environment variables or use default values in the script.

## License

This project is licensed under the [MIT License](LICENSE).

Feel free to contribute or raise issues.

For more details, refer to the script documentation.

