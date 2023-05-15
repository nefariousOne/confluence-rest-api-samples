#!/usr/bin/python3

import os
import json

def process_confluence_group_data(user_data, group_name):
    for group, group_data in user_data['groups'].items():
        if group == group_name:
            for user, user_info in group_data['users'].items():
                if user_info['status'] != 'current':
                    print(user_info['username'] + ' : ' + user_info['status'])


if __name__ == '__main__':
    file_path = os.path.join(os.getcwd(), 'group_user_data.json')

    with open(file_path, 'r') as f:
        user_data = json.load(f)

    group_to_process = 'confluence-users'
    process_confluence_group_data(user_data, group_to_process)
