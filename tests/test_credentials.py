import os
import sys
import uuid
sys.path.append('./aioaws')

import credentials


KEY = uuid.uuid4().hex
SECRET = uuid.uuid4().hex
TOKEN = uuid.uuid4().hex

def test_creds_from_environment():
    os.environ['AWS_ACCESS_KEY_ID'] = KEY
    os.environ['AWS_SECRET_ACCESS_KEY'] = SECRET
    os.environ['AWS_SESSION_TOKEN'] = TOKEN

    key, secret, token = credentials.Credentials._get_creds_from_environment()
    assert key == KEY
    assert secret == SECRET
    assert token == TOKEN


def test_creds_from_default_profile():
    credentials_file_text = '[default]\n' + \
            f'aws_access_key_id={KEY}\n' + \
            f'aws_secret_access_key={SECRET}\n' + \
            f'aws_session_token={TOKEN}\n'
    credentials_path = '/tmp/' + uuid.uuid4().hex
    with open(credentials_path, 'w') as f:
        f.write(credentials_file_text)

    key, secret, token = credentials.Credentials._get_creds_from_file(credentials_path, None)
    os.remove(credentials_path)

    assert key == KEY
    assert secret == SECRET
    assert token == TOKEN


def test_creds_from_named_profile():
    profile = uuid.uuid4().hex
    credentials_file_text = f'[{profile}]\n' + \
            f'aws_access_key_id={KEY}\n' + \
            f'aws_secret_access_key={SECRET}\n' + \
            f'aws_session_token={TOKEN}\n'
    credentials_path = '/tmp/' + uuid.uuid4().hex
    with open(credentials_path, 'w') as f:
        f.write(credentials_file_text)

    key, secret, token = credentials.Credentials._get_creds_from_file(credentials_path, profile)
    os.remove(credentials_path)

    assert key == KEY
    assert secret == SECRET
    assert token == TOKEN


