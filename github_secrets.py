import os
from dotenv import load_dotenv
from ghapi.all import GhApi
from loguru import logger
from base64 import b64encode
from nacl import encoding, public


# Load GIT HUB CREDENTIALS
load_dotenv()
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
GITHUB_REPO_OWNER = os.getenv('GITHUB_REPO_OWNER')
GITHUB_REPO = os.getenv('GITHUB_REPO')
ENVIRONMENT = os.getenv('ENVIRONMENT')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


def encrypt(public_key: str, secret_value: str) -> str:
  """Encrypt a Unicode string using the public key."""
  public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
  sealed_box = public.SealedBox(public_key)
  encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
  return b64encode(encrypted).decode("utf-8")


api = GhApi(owner=GITHUB_REPO_OWNER, repo=GITHUB_REPO, token=GITHUB_ACCESS_TOKEN)

repoId = api.repos.get().id
logger.info(f'Creating/Updating new environment {ENVIRONMENT}')
api.repos.create_or_update_environment(ENVIRONMENT)
logger.info(f'Fetching environment public key for {ENVIRONMENT}')

public_key= api.actions.get_environment_public_key(repoId, ENVIRONMENT)

encrypted_value=encrypt(public_key.key, AWS_ACCESS_KEY_ID)
api.actions.create_or_update_environment_secret(repoId, ENVIRONMENT, 'AWS_ACCESS_KEY_ID', encrypted_value, public_key.key_id)

encrypted_value=encrypt(public_key.key, AWS_SECRET_ACCESS_KEY)
api.actions.create_or_update_environment_secret(repoId, ENVIRONMENT, 'AWS_SECRET_ACCESS_KEY', encrypted_value, public_key.key_id)

