import configparser
import os
import platform


class Credentials:
    def __init__(self, *,
            key=None,
            secret=None,
            token=None,
            credentials_path=None,
            profile=None):
        if key is not None and secret is None:
            raise Exception('Provide both key AND secret, or neither')
        elif key is None and secret is not None:
            raise Exception('Provide both key AND secret, or neither')

        if key is None:
            key, secret, token = Credentials._get_creds_from_environment()
        if key is None:
            key, secret, token = Credentials._get_creds_from_file(credentials_path, profile)
        if key is None:
            key, secret, token = Credentials._get_creds_from_profile_url()
        if key is None:
            raise Exception('Couldn\'t find credentials')

        self.key=key
        self.secret=secret
        self.token=token
    
    @staticmethod
    def _get_creds_from_environment():
        if 'AWS_ACCESS_KEY_ID' not in os.environ or \
                'AWS_SECRET_ACCESS_KEY' not in os.environ:
                    return None, None, None

        key = os.environ['AWS_ACCESS_KEY_ID']
        secret = os.environ['AWS_SECRET_ACCESS_KEY']
        token = os.environ.get('AWS_SESSION_TOKEN')
        return key, secret, token


    @staticmethod
    def _get_creds_from_file(credentials_path, profile):
        if credentials_path is None:
            credentials_path = os.path.expanduser('~/.aws/credentials')
        if profile is None:
            profile = 'default'

        config = configparser.ConfigParser()
        config.read([credentials_path])
        if profile not in config or \
                'aws_access_key_id' not in config[profile] or \
                'aws_secret_access_key' not in config[profile]:
                    return None, None, None

        key = config[profile]['aws_access_key_id']
        secret = config[profile]['aws_secret_access_key']
        token = config[profile]['aws_session_token'] if 'aws_session_token' in config[profile] else None
        return key, secret, token


    @staticmethod
    def _get_creds_from_profile_url():
        pass

