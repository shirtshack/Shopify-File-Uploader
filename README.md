# Product Uploader
A set of scripts to automate upload of products to Amazon and Shopify. 

## Development Requirements

- Python 3.12.4 or later
- Pip

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/amazon-product-uploader.git
   cd amazon-product-uploader
   ```
2. Create a virtual environment and activate it
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Copy file `.env.example` to `.env` and complete the environment variables.

## Usage

1. Start the streamlit application:
    ```sh 
    export $(cat .env | xargs)
    make local_server
    ```
2. Open your web browser and navigate to `http://localhost:8501`.

3. Start using the UI.


## Deployment

Deployment is triggered automatically on every push to branch `main`.

## Project structure

## GCP

Deployment to GCP happens automatically after pushing to the `main` branch. This triggers a build on google cloud build services and deploys both containers to cloud run. 

Log in to google cloud console and go to the Cloud Run service to see deployment details.


### Google Drive and service account

The template files are picked up from a shared g-drive [folder](https://drive.google.com/drive/u/0/folders/1Q3QEHV0mIw3ntM1yDxOy3R80eVttWzCQ). The compute service account needs to be added as viewer to this folder in order for this to work. You need a valid service account json file to run the system locally. 