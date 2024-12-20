"""Create Mastodon app and get credentials

This script will create a new Mastodon app and save the credentials to a file.

Warning: this is not intended to be used multiple times! This should only be run once after the Mastodon instance is created.
"""

from mastodon import Mastodon

domain_name = "mastodon.genexergy.org"

Mastodon.create_app("masto-sim", api_base_url=f"https://{domain_name}", to_file="clientcred.secret")
