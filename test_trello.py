import pytest
import requests
import logging
import config
import time


logger = logging.getLogger(__name__)

def test_trello_e2e_scenario(trello_board: dict):
    """
    End-to-End Test Scenario for Trello Board.
    
    Steps:
    1. Create a List on the Board.
    2. Create a Card in that List.
    3. Update the created Card.
    4. Delete the Card.
    
    Args:
        trello_board (dict): The board object created by the conftest fixture.
    """
    

    board_id = trello_board['id']
    base_params = {'key': config.API_KEY, 'token': config.API_TOKEN}
    
    list_url = f"{config.BASE_URL}/lists"
    list_name = "To Do Items"
    
   
    logger.info(f"Step 1: Creating list '{list_name}' on board {board_id}...")
    create_list_params = base_params.copy()
    create_list_params.update({'name': list_name, 'idBoard': board_id})
    
    response_list = requests.post(list_url, params=create_list_params)

    assert response_list.status_code == 200, "Failed to create list"
    list_data = response_list.json()
    assert list_data['name'] == list_name, "List name does not match"
    list_id = list_data['id']
    logger.info(f"List created successfully. ID: {list_id}")


    card_url = f"{config.BASE_URL}/cards"
    card_name = "Complete Project Documentation"

    logger.info(f"Step 2: Creating card '{card_name}' in list {list_id}...")
    create_card_params = base_params.copy()
    create_card_params.update({'name': card_name, 'idList': list_id})
    
    response_card = requests.post(card_url, params=create_card_params)
    

    assert response_card.status_code == 200, "Failed to create card"
    card_data = response_card.json()
    assert card_data['name'] == card_name, "Card name does not match"
    card_id = card_data['id']
    logger.info(f"Card created successfully. ID: {card_id}")



    update_card_url = f"{config.BASE_URL}/cards/{card_id}"
    new_card_name = "Complete Project Documentation (Reviewed)"
    new_desc = "Updated description for the task."
    

    logger.info(f"Step 3: Updating card {card_id} with new details...")
    update_card_params = base_params.copy()
    update_card_params.update({'name': new_card_name, 'desc': new_desc})
    
    response_update = requests.put(update_card_url, params=update_card_params)

    assert response_update.status_code == 200, "Failed to update card"
    updated_card_data = response_update.json()
    assert updated_card_data['name'] == new_card_name, "Updated card name does not match"
    assert updated_card_data['desc'] == new_desc, "Updated card description does not match"
    logger.info("Card updated successfully.")


    delete_card_url = f"{config.BASE_URL}/cards/{card_id}"
    
    logger.info(f"Step 4: Deleting card {card_id}...")
    response_delete = requests.delete(delete_card_url, params=base_params)
    
    assert response_delete.status_code == 200, "Failed to delete card"


    verify_response = requests.get(delete_card_url, params=base_params)
    assert verify_response.status_code == 404, "Card still exists after deletion"
    logger.info("Card deleted and verified successfully.")


def test_move_card_between_lists(trello_board: dict):
    """
    Test Scenario: Move a card from one list to another.
    1. Create two lists (Source and Target).
    2. Create a card in Source.
    3. Move card to Target.
    4. Verify card is in Target list.
    """
    board_id = trello_board['id']
    base_params = {'key': config.API_KEY, 'token': config.API_TOKEN}
    
    # 1. Create Source and Target Lists
    list_url = f"{config.BASE_URL}/lists"
    
    # Create Source List
    resp_source = requests.post(list_url, params={**base_params, 'name': 'Source List', 'idBoard': board_id})
 
    assert resp_source.status_code == 200
    source_list_id = resp_source.json()['id']
    

    resp_target = requests.post(list_url, params={**base_params, 'name': 'Target List', 'idBoard': board_id})
    assert resp_target.status_code == 200
    target_list_id = resp_target.json()['id']
    

    card_url = f"{config.BASE_URL}/cards"
    resp_card = requests.post(card_url, params={**base_params, 'name': 'Moving Card', 'idList': source_list_id})
    assert resp_card.status_code == 200
    card_id = resp_card.json()['id']
    

    logger.info(f"Moving card {card_id} from {source_list_id} to {target_list_id}")
    update_url = f"{config.BASE_URL}/cards/{card_id}"
    resp_move = requests.put(update_url, params={**base_params, 'idList': target_list_id})
    assert resp_move.status_code == 200
    
  
    resp_verify = requests.get(update_url, params=base_params)
    current_list_id = resp_verify.json()['idList']
    assert current_list_id == target_list_id, f"Card did not move to target list. Current: {current_list_id}"
    logger.info("Card moved successfully between lists.")


def test_add_comment_and_label(trello_board: dict):
    """
    Test Scenario: Add a comment and a label to a card.
    1. Create a list and a card.
    2. Add a comment to the card.
    3. Add a label to the card.
    4. Verify comment and label exist.
    """
    board_id = trello_board['id']
    base_params = {'key': config.API_KEY, 'token': config.API_TOKEN}
    
    list_resp = requests.post(f"{config.BASE_URL}/lists", params={**base_params, 'name': 'Discussion List', 'idBoard': board_id})
    list_id = list_resp.json()['id']
    
    card_resp = requests.post(f"{config.BASE_URL}/cards", params={**base_params, 'name': 'Topic Card', 'idList': list_id})
    card_id = card_resp.json()['id']
    
    comment_text = "This is an automated comment."
    comment_url = f"{config.BASE_URL}/cards/{card_id}/actions/comments"
    resp_comment = requests.post(comment_url, params={**base_params, 'text': comment_text})
    assert resp_comment.status_code == 200
    assert resp_comment.json()['data']['text'] == comment_text
    logger.info("Comment added successfully.")
    
  
    label_url = f"{config.BASE_URL}/cards/{card_id}/idLabels"
    

    label_post_url = f"{config.BASE_URL}/cards/{card_id}/labels"
    resp_label = requests.post(label_post_url, params={**base_params, 'color': 'blue', 'name': 'Urgent'})
    assert resp_label.status_code == 200
    logger.info("Label 'Urgent' (blue) added to card.")


def test_checklist_functionality(trello_board: dict):
    """
    Test Scenario: Manage a checklist on a card.
    1. Create card.
    2. Create checklist on card.
    3. Add item to checklist.
    4. Mark item as complete.
    """
    board_id = trello_board['id']
    base_params = {'key': config.API_KEY, 'token': config.API_TOKEN}
    
 
    list_resp = requests.post(f"{config.BASE_URL}/lists", params={**base_params, 'name': 'Checklist List', 'idBoard': board_id})
    list_id = list_resp.json()['id']
    card_resp = requests.post(f"{config.BASE_URL}/cards", params={**base_params, 'name': 'Task with Steps', 'idList': list_id})
    card_id = card_resp.json()['id']
    
   
    checklist_url = f"{config.BASE_URL}/checklists"
    resp_cl = requests.post(checklist_url, params={**base_params, 'idCard': card_id, 'name': 'Testing Steps'})
    assert resp_cl.status_code == 200
    checklist_id = resp_cl.json()['id']
    logger.info(f"Checklist created with ID: {checklist_id}")
    
   
    checkitem_url = f"{config.BASE_URL}/checklists/{checklist_id}/checkItems"
    resp_item = requests.post(checkitem_url, params={**base_params, 'name': 'Step 1: Verification'})
    assert resp_item.status_code == 200
    item_id = resp_item.json()['id']
    
    
    update_item_url = f"{config.BASE_URL}/cards/{card_id}/checkItem/{item_id}"
    resp_update = requests.put(update_item_url, params={**base_params, 'state': 'complete'})
    assert resp_update.status_code == 200
    assert resp_update.json()['state'] == 'complete'
    logger.info("Checklist item marked as complete.")


def test_negative_get_nonexistent_card(trello_board: dict):
    """
    Negative Test Scenario: Try to retrieve a card that does not exist.
    Expectation: API returns 404 Not Found.
    """
    base_params = {'key': config.API_KEY, 'token': config.API_TOKEN}
    
    fake_card_id = "000000000000000000000000" 
    
    url = f"{config.BASE_URL}/cards/{fake_card_id}"
    
    logger.info(f"Negative Test: Requesting non-existent card {fake_card_id}...")
    response = requests.get(url, params=base_params)
    
    assert response.status_code == 404, f"Expected 404 for non-existent card, but got {response.status_code}"
    logger.info("Negative test passed: Received 404 as expected.")


def test_add_attachment_to_card(trello_board: dict):
    """
    Test Scenario: Upload an attachment to a card.
    1. Create a card.
    2. Upload a file (dummy_attachment.txt) to the card.
    3. Verify the attachment exists on the card.
    """
    board_id = trello_board['id']
    base_params = {'key': config.API_KEY, 'token': config.API_TOKEN}
    
  
    list_resp = requests.post(f"{config.BASE_URL}/lists", params={**base_params, 'name': 'Attachment List', 'idBoard': board_id})
    list_id = list_resp.json()['id']
    card_resp = requests.post(f"{config.BASE_URL}/cards", params={**base_params, 'name': 'Card with File', 'idList': list_id})
    card_id = card_resp.json()['id']
    

    attachment_url = f"{config.BASE_URL}/cards/{card_id}/attachments"
    
    file_path = "dummy_attachment.txt"
    files = {'file': open(file_path, 'rb')}
    
    logger.info(f"Uploading {file_path} to card {card_id}...")
    resp_att = requests.post(attachment_url, params=base_params, files=files)
    files['file'].close() 
    
    assert resp_att.status_code == 200
    att_data = resp_att.json()
    assert att_data['name'] == "dummy_attachment.txt"
    logger.info("Attachment uploaded successfully.")


def test_update_board_description(trello_board: dict):
    """
    Test Scenario: Update the Board's description.
    1. Get the current board ID.
    2. Update the 'desc' field of the board.
    3. Verify the update.
    """
    board_id = trello_board['id']
    base_params = {'key': config.API_KEY, 'token': config.API_TOKEN}
    
    new_desc = "This board is used for automated API testing."
    logger.info(f"Updating description for board {board_id}...")
    
    url = f"{config.BASE_URL}/boards/{board_id}"
    resp = requests.put(url, params={**base_params, 'desc': new_desc})
    
    assert resp.status_code == 200
    assert resp.json()['desc'] == new_desc
    logger.info("Board description updated successfully.")




def test_negative_create_card_without_list(trello_board: dict):
    """
    Negative Test: Try to create a card without providing a required List ID.
    Expectation: 400 Bad Request.
    """
    base_params = {'key': config.API_KEY, 'token': config.API_TOKEN}
    card_url = f"{config.BASE_URL}/cards"
    
    logger.info("Negative Test: Creating card without 'idList'...")
    # Missing 'idList' which is required
    resp = requests.post(card_url, params={**base_params, 'name': 'Orphan Card'})
    
    assert resp.status_code == 400, f"Expected 400 Bad Request, got {resp.status_code}"
    # Trello usually returns "invalid value for idList" or similar text
    logger.info(f"Negative test passed. API Response: {resp.text}")
