import requests
import os
import shutil
import json
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get all categories in qBittorrent
def get_all_categories(qb_api_url):
    categories_url = f"{qb_api_url}/api/v2/torrents/categories"
    try:
        response = requests.get(categories_url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get categories. Error: {str(e)}")

# Function to get the list of torrents with a specific category from qBittorrent
def get_category_torrents(qb_api_url, category):
    torrents_url = f"{qb_api_url}/api/v2/torrents/info"
    params = {'category': category}
    try:
        response = requests.get(torrents_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get torrents with category '{category}'. Error: {str(e)}")

# Function to get a list of subfolders in the provided path
def get_subfolders(path):
    if os.path.exists(path) and os.path.isdir(path):
        return [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
    else:
        logger.error(f"Path {path} does not exist or is not a directory.")
        return None

# Function to delete a folder and its content
def delete_folder(folder_path):
    try:
        # Set full permissions before attempting to delete
        os.chmod(folder_path, 0o777)
        shutil.rmtree(folder_path)
        logger.info(f"Folder deleted: {folder_path}")
    except PermissionError as e:
        logger.error(f"Failed to delete folder {folder_path}. Permission denied. Error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to delete folder {folder_path}. Error: {str(e)}")

# Main script
if __name__ == "__main__":
    # Check if the required command line arguments are provided
    if len(sys.argv) != 3:
        logger.error("Error: Please provide the QB_API_URL and CHECK_PATH as command line arguments.")
        sys.exit(1)

    # Get command line arguments
    qb_api_url = sys.argv[1]
    check_path = sys.argv[2]

    # Get all categories in qBittorrent
    all_categories = get_all_categories(qb_api_url)

    if all_categories:
        for category in all_categories:
            # Get the list of torrents with the specified category
            category_torrents = get_category_torrents(qb_api_url, category)

            # Get a list of subfolders in the provided path
            subfolders = get_subfolders(os.path.join(check_path, category))
            if subfolders is not None:
                # Check against the list of torrents and full paths
                if not category_torrents:
                    # If no torrents are active for the category, review all folders
                    missing_folders = subfolders
                else:
                    # If torrents are active, only review folders not associated with torrents
                    missing_folders = [folder for folder in subfolders if os.path.basename(os.path.join(check_path, category, folder)) not in [os.path.basename(os.path.join(torrent['save_path'], torrent['name'])) for torrent in category_torrents]]

                if missing_folders:
                    logger.info(f"Folders not associated with torrents for category '{category}':")
                    for folder in missing_folders:
                        folder_path = os.path.join(check_path, category, folder)
                        logger.info(folder_path)

                        # Uncomment the following line to delete the folder and its content
                        delete_folder(folder_path)
            else:
                logger.info(f"No subfolders found in path '{os.path.join(check_path, category)}'.")
    else:
        logger.error("Unable to fetch categories from qBittorrent.")
