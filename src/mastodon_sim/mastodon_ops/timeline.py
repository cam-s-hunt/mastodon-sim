"""Retrieve posts from a user's timeline on Mastodon."""

import argparse

import mastodon
from dotenv import find_dotenv, load_dotenv

from mastodon_sim.logging_config import logger
from mastodon_sim.mastodon_ops.get_client import get_client
from mastodon_sim.mastodon_ops.login import login


def get_public_timeline(limit: None | int = 10) -> mastodon.utility.AttribAccessList | list:
    """Retrieve the public timeline on Mastodon.

    Args:
        login_user (str): The user to log in with.
        limit (int): The number of posts to retrieve. Default is 10.

    Returns
    -------
        list: A list of posts from the public timeline.
    """
    load_dotenv(find_dotenv())  # Load environment variables from .env file

    try:
        mastodon = get_client()

        # Retrieve the public timeline
        timeline = mastodon.timeline_public(limit=limit)
        logger.info(f"Retrieved {len(timeline)} posts from the public timeline.")
        return timeline
    except ValueError as e:
        logger.error(f"Error: {e}")
        return []
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return []


def get_own_timeline(
    login_user: str, limit: None | int = 10
) -> mastodon.utility.AttribAccessList | list:
    """Retrieve posts from the authenticated user's timeline on Mastodon.

    Args:
        login_user (str): The user to log in with.
        limit (int): The number of posts to retrieve. Default is 10.

    Returns
    -------
        list: A list of posts from the authenticated user's timeline.
    """
    load_dotenv(find_dotenv())  # Load environment variables from .env file

    try:
        access_token = login(login_user)

        logger.debug(f"{login_user} attempting to retrieve their own timeline...")
        mastodon = get_client()
        mastodon.access_token = access_token

        # Retrieve the authenticated user's timeline
        timeline = mastodon.timeline_home(limit=limit)
        logger.info(f"{login_user} retrieved {len(timeline)} posts from their own timeline.")
        return timeline
    except ValueError as e:
        logger.error(f"Error: {e}")
        return []
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return []


def get_user_timeline(
    login_user: str, target_user: str, limit: None | int = None
) -> mastodon.utility.AttribAccessList | list:
    """Retrieve posts from a user's timeline on Mastodon.

    Args:
        login_user (str): The user to log in with.
        target_user (str): The target user to retrieve posts from.
        limit (int): The number of posts to retrieve. Default is 10.

    Returns
    -------
        list: A list of posts from the target user's timeline.
    """
    load_dotenv(find_dotenv())  # Load environment variables from .env file

    try:
        access_token = login(login_user)

        logger.debug(f"{login_user} attempting to retrieve posts from {target_user}...")
        mastodon = get_client()
        mastodon.access_token = access_token

        # Search for the user and get their ID
        account = mastodon.account_search(target_user, limit=1)
        if account:
            target_user_id = account[0]["id"]
            timeline = mastodon.account_statuses(target_user_id, limit=limit)
            logger.info(
                f"{login_user} retrieved {len(timeline)} posts from {target_user}'s timeline."
            )
            return timeline
        logger.warning(f"User {target_user} not found.")
        return []
    except ValueError as e:
        logger.error(f"Error: {e}")
        return []
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return []


def print_timeline(timeline) -> None:
    """
    Print the most relevant details from a Mastodon timeline.

    Args:
        timeline (list): A list of dictionaries containing post information.
    """
    if len(timeline):
        print("-" * 40)
    for post in timeline:
        post_id = post.get("id")
        created_at = post.get("created_at")
        username = post.get("account", {}).get("username")
        display_name = post.get("account", {}).get("display_name", username)
        content = post.get("content")
        url = post.get("url")
        favourites_count = post.get("favourites_count")
        reblogs_count = post.get("reblogs_count")

        print(f"Post ID: {post_id}")
        print(f"Created At: {created_at}")
        print(f"User: {display_name} (@{username})")
        print(f"Content: {content}")
        print(f"URL: {url}")
        print(f"Favourites: {favourites_count}, Reblogs: {reblogs_count}")
        print("-" * 40)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retrieve posts from a user's timeline or the public timeline on Mastodon."
    )
    parser.add_argument("login_user", help="The user to log in with.")
    parser.add_argument(
        "--target_user", help="The target user to retrieve posts from (for user timeline)."
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Retrieve the public timeline instead of a user timeline.",
    )
    parser.add_argument(
        "--limit", type=int, default=10, help="The number of posts to retrieve. Default is 10."
    )

    args = parser.parse_args()
    if args.public:
        timeline = get_public_timeline(limit=args.limit)
    else:
        if not args.target_user:
            parser.error("--target_user is required when --public is not specified.")
        timeline = get_user_timeline(args.login_user, args.target_user, limit=args.limit)
    print_timeline(timeline)