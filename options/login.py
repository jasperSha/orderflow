from td.client import TDClient
from config.config import CLIENT_ID, REDIRECT_URI, CREDENTIALS_PATH


def login():
    # Create a new session, credentials path is required.
    session = TDClient(
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        credentials_path=CREDENTIALS_PATH
    )

    session.login()
    return session
