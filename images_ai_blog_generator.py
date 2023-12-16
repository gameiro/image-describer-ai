# System 
import logging
import os
import subprocess
import concurrent.futures
# GPC auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
# GPC AI models
import vertexai
from vertexai.vision_models import ImageTextModel, Image
from vertexai.language_models import TextGenerationModel
from heic2png import HEIC2PNG

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Get environment variables or set default values
CAPTION_SHORT_TEXT_CONTEXT = os.getenv('CAPTION_SHORT_CONTEXT')
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
# ID of the folder in Google Drive containing the images
GCP_DRIVE_FOLDER_ID = os.getenv('GCP_DRIVE_FOLDER_ID')
GCP_DRIVE_FETCH_PAGE_SIZE = os.getenv('GCP_DRIVE_FETCH_PAGE_SIZE', 100)
MARKDOWN_FILE_PATH = 'blog_post_summary.md'

# Path to your service account key JSON file
service_account_file = '/secrets/client_secrets.json'

# Define the required scopes for the Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

# Create credentials using the service account key file
credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=SCOPES
)

# Build the Drive service using the created credentials
drive_service = build('drive', 'v3', credentials=credentials)

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Function to download image content
def download_image(drive_service, file_id):
    request = drive_service.files().get_media(fileId=file_id)
    image_content = request.execute()
    return image_content if image_content else None

# Function to convert HEIC image to PNG
def convert_heic_to_png(image_content):
    temp_filename = f'./temp/temp.heic'
    converted_filename = f'./temp/converted.png'
    
    with open(temp_filename, 'wb') as temp_file:
        temp_file.write(image_content)

    conversion_command = ['heic2png', '-i', temp_filename, '-o', converted_filename, '-w']
    subprocess.run(conversion_command)

    return converted_filename

# Function to process captions asynchronously
def process_captions_async(captions_list):
    improved_captions = []
    text_model = TextGenerationModel.from_pretrained("text-bison@002")
    for merged_captions in captions_list:
        to_predict = f"Provide a summary about {CAPTION_SHORT_TEXT_CONTEXT} with about two sentences from the following captions: {merged_captions}"
        parameters = {
            "temperature": 0.3,
            "max_output_tokens": 1024,
            "top_p": 0.8,
            "top_k": 40,
        }
        improved_caption = text_model.predict(to_predict, **parameters)
        improved_captions.append(improved_caption.text)
    return improved_captions


def process_image_caption_async(converted_filename):
    try:
        logging.info(f"Get captions from Image: {converted_filename}.")
        source_image = Image.load_from_file(location=converted_filename)
        
        if source_image is not None:  # Check if the image was loaded successfully
            model = ImageTextModel.from_pretrained("imagetext@001")
            captions = model.get_captions(
                image=source_image,
                number_of_results=1,
                language="en",
            )
            merged_captions = ' '.join(captions)
            return merged_captions
        else:
            logging.error(f"Failed to load the image: {converted_filename}")
            return None
    except Exception as e:
        logging.error(f"Error processing image caption: {e}")
        return None
    
# Function to process images and their captions
def process_images(files):
    improved_captions = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        caption_futures = []
        for i in range(0, len(files), 50):
            image_batch = files[i:i + 50]
            captions_list = []

            for file in image_batch:
                file_id = file['id']
                file_name = file['name']
                converted_filename = ""
                
                image_content = download_image(drive_service, file_id)

                logging.info(f"Converting Image file: {file_name}")

                converted_filename = convert_heic_to_png(image_content)
        
                if converted_filename:
                    caption_future = executor.submit(process_image_caption_async, converted_filename)
                    caption_futures.append(caption_future)
                    
                else:
                    logging.warning(f"File '{file_name}' content not found or is not an image.")
            
            # Wait for all the asynchronous tasks to complete
            concurrent.futures.wait(caption_futures)
            
            # Retrieve the results
            for future in caption_futures:
                try:
                    result = future.result()
                    if result is not None:
                        captions_list.append(result)
                except Exception as e:
                    logging.error(f"Error processing caption: {e}")
            # Remove duplicates from the captions_list
            unique_captions = list(set(captions_list))
            if unique_captions:
                improved_captions.extend(process_captions_async(unique_captions))
    
    return improved_captions

# Function to paginate through the files from Google Drive
def get_all_files_from_drive():
    all_files = []
    page_token = None
    while True:
        results = drive_service.files().list(
            q=f"'{GCP_DRIVE_FOLDER_ID}' in parents and trashed=false and mimeType contains 'image/'",
            fields="nextPageToken, files(id, name)",
            pageSize=GCP_DRIVE_FETCH_PAGE_SIZE,
            pageToken=page_token
        ).execute()
        items = results.get('files', [])
        all_files.extend(items)
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    return all_files

# Splitting a list into chunks
def chunks(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Retrieve all files from Google Drive
files = get_all_files_from_drive()
if not files:
    print("No image files found in the specified folder.")
else:
    improved_captions = process_images(files)
    # Generate markdown
    markdown_content = "# Improved Captions for Professional Blog Post\n\n"

    for index, merged_caption in enumerate(improved_captions, start=1):
        improved_caption = improved_captions[index - 1]
        markdown_content += f"## Caption {index}:\n\n{improved_caption}\n\n"

    markdown_filename = 'improved_captions.md'

    with open(markdown_filename, 'w') as markdown_file:
        markdown_file.write(markdown_content)

    logging.info(f"Markdown file with improved captions created: {markdown_filename}")

    # Split improved_captions into smaller chunks for summarization
    chunk_size = 50  # Adjust the chunk size
    improved_captions_chunks = list(chunks(improved_captions, chunk_size))

    summary_texts = []
    text_model_summary = TextGenerationModel.from_pretrained("text-bison@002")

    # Generate summaries for each chunk of improved captions
    for chunk in improved_captions_chunks:
        improved_captions_combined = ' '.join(chunk)

        summary_parameters = {
            "temperature": 0.5,
            "max_output_tokens": 1000,
            "top_p": 0.7,
            "top_k": 40,
        }

        summary_output = text_model_summary.predict(f"You are professional web blogger that is specialized in Cloud services, write a blog post about 100 sentences with the following captions texts: {improved_captions_combined}", **summary_parameters)
        summary_texts.append(summary_output.text)

    # Combine all summaries into a single blog post summary
    blog_post_summary = "\n\n".join(summary_texts)

    # Create a Markdown file with the summary for the blog post
    summary_markdown_filename = 'blog_post_summary.md'

    with open(summary_markdown_filename, 'w') as summary_file:
        summary_file.write(blog_post_summary)

    print(f"Markdown file with blog post summary created: {summary_markdown_filename}")
    
    # Upload the Markdown file to Google Drive
    file_metadata = {
        'name': 'blog_post_summary.md',  # Replace with the desired name for the file in Drive
        'parents': [GCP_DRIVE_FOLDER_ID]
    }
    media = {'mimeType': 'text/markdown', 'body': open(MARKDOWN_FILE_PATH, 'rb')}
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    print(f'File ID of the uploaded Markdown file: {uploaded_file.get("id")}')
