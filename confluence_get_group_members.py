#!/usr/bin/python3

# import necessary packages
import requests
import json
import logging

# configure logging
logging.basicConfig(level=logging.INFO)

class ConfluenceAPI:
    def __init__(self, base_url, bearer_token, api_endpoint):
        """
        Initializes a Confluence API instance.

        Args:
        - base_url (str): the base URL of the Confluence Data Center environment.
        - bearer_token (str): the Confluence Admin's Personal Access Token (PAT).
        - api_endpoint (str): the REST API endpoint to call.

        Returns:
        - None
        """
        self.base_url = base_url
        self.bearer_token = bearer_token
        self.api_endpoint = api_endpoint
        self.headers = {'Authorization': 'Bearer ' + self.bearer_token, 'X-Atlassian-Token': 'no-check', 'Content-Type': 'application/json'}

    def get_groups_and_users(self):
        """
        Retrieves all groups in a Confluence Data Center instance and their members.

        Args:
        - None

        Returns:
        - full_data (dict): a dictionary containing all groups in the Confluence Data Center instance and their members.
        """
        # set the initial URL for the group endpoint
        group_api_url = self.base_url + self.api_endpoint
        # create a dictionary to store the group and member data
        full_data = {'groups':{}}

        # loop through all groups
        while True:
            # make a GET request to the group endpoint
            req = requests.get(group_api_url, headers=self.headers)
            # check for errors
            if req.status_code != 200:
                logging.error(f"Error retrieving groups: {req.text}")
                break

            # parse the response data as JSON
            data = json.loads(req.text)

            # loop through all groups returned in the response
            for result in data['results']:
                group = result['name']
                # skip the 'confluence-users' group
                if group == "confluence-users":
                    continue
                logging.info(f"Retrieving members for group {group}")
                # add the group data to the full_data dictionary
                full_data['groups'][group] = {'group-data': result, 'users': {}}
                # set the initial URL for the group's members endpoint
                member_api_url = self.base_url + self.api_endpoint + group + '/member'

                # loop through all pages of group members
                while True:
                    # make a GET request to the group's members endpoint
                    req = requests.get(member_api_url, headers=self.headers, params={'expand':'status'})
                    # check for errors
                    if req.status_code != 200:
                        logging.error(f"Error retrieving members for group {group}: {req.text}")
                        full_data['groups'][group]['error'] = req.text
                        break

                    # parse the response data as JSON
                    data = json.loads(req.text)

                    # loop through all members returned in the response
                    for result in data['results']:
                        user = result['username']
                        logging.info(f"Retrieved member {user} for group {group}")
                        # add the member data to the full_data dictionary
                        full_data['groups'][group]['users'][user] = result

                    # if there are more pages of members, update the URL and continue looping
                    if "next" in data['_links']:
                        member_api_url = self.base_url + data['_links']['next']
                    else:
                        break

            # if there are more pages of groups, update the URL and continue looping
            if "next" in data['_links']:
                group_api_url = self.base_url + data['_links']['next']
            else:
                break

        return full_data

if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)
    
    # instantiate new API class
    api = ConfluenceAPI(config['base_url'], config['bearer_token'], config['api_endpoint'])
    
    # perform group / user data collection
    full_data = api.get_groups_and_users()
    
    # write to data object to file
    with open('group_user_data.json', mode='w+') as f:
        f.write(json.dumps(full_data))
