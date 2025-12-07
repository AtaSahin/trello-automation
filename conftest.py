import pytest
import requests
import logging
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def trello_board():
    """
    Fixture that creates a new Trello board before the test runs
    and deletes it after the test finishes (Setup & Teardown).
    
    Returns:
        dict: The created board object containing details like id, name, etc.
    """

    create_url = f"{config.BASE_URL}/boards/"
    query_params = {
        'key': config.API_KEY,
        'token': config.API_TOKEN,
        'name': config.DEFAULT_BOARD_NAME
    }
    
    logger.info(f"Setting up: Creating a new Trello board named '{config.DEFAULT_BOARD_NAME}'...")
    response = requests.post(create_url, params=query_params)
    
    if response.status_code != 200:
        logger.error(f"Failed to create board during setup. Status: {response.status_code}, Response: {response.text}")
        pytest.fail("Could not create Trello board in fixture setup.")
        
    board_data = response.json()
    board_id = board_data['id']
    logger.info(f"Board created successfully. ID: {board_id}")
    
    # Yield the board data to the test function
    yield board_data

    logger.info(f"Tearing down: Deleting board with ID: {board_id}...")
    delete_url = f"{config.BASE_URL}/boards/{board_id}"
    delete_response = requests.delete(delete_url, params={'key': config.API_KEY, 'token': config.API_TOKEN})
    
    if delete_response.status_code == 200:
        logger.info("Board deleted successfully.")
    else:
        logger.warning(f"Failed to delete board during teardown. Status: {delete_response.status_code}")
