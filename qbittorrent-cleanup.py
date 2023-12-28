import requests
import os
import shutil
import json
import sys

# Function to load parameters from parameters.json
def load_parameters():
    try:
        with open('parameters.json', 'r') as file:
            parameters = json.load(file)
            return parameters
    except FileNotFoundError:
        print("Parameters file not found. Please create a 'parameters.json' file.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON in 'parameters.json'. Please check the file format.")
        return None

# Function to get all categories in qBittorrent
def get_all_categories(qb_api_url):
    categories_url = f"{qb_api_url}/api/v2/torrents/categories"
    response = requests.get(categories_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get categories with status code: {response.status_code}")
        return None

# Function to get the list of torrents with a specific category from qBittorrent
def get_category_torrents(qb_api_url, category):
    torrents_url = f"{qb_api_url}/api/v2/torrents/info"
    params = {'category': category}
    response = requests.get(torrents_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get torrents with category '{category}' and status code: {response.status_code}")
        return None

# Function to get a list of subfolders in the provided path
def get_subfolders(path):
    if os.path.exists(path) and os.path.isdir(path):
        return [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
    else:
        print(f"Path {path} does not exist or is not a directory.")
        return None

# Function to delete a folder and its content
def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder deleted: {folder_path}")
    except PermissionError as e:
        print(f"Failed to delete folder {folder_path}. Permission denied. Error: {str(e)}")
        # Add permission change here
        os.chmod(folder_path, 0o777)
        print(f"Permission changed to 777 for folder: {folder_path}")
    except Exception as e:
        print(f"Failed to delete folder {folder_path}. Error: {str(e)}")

# Main script
if __name__ == "__main__":
    # Check if the required command line arguments are provided
    if len(sys.argv) != 3:
        print("Error: Please provide the QB_API_URL and CHECK_PATH as command line arguments.")
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
                    print(f"Folders not associated with torrents for category '{category}':")
                    for folder in missing_folders:
                        folder_path = os.path.join(check_path, category, folder)
                        print(folder_path)

                        # Uncomment the following line to delete the folder and its content
                        delete_folder(folder_path)
            else:
                print(f"No subfolders found in path '{os.path.join(check_path, category)}'.")
    else:
        print("Unable to fetch categories from qBittorrent.")
