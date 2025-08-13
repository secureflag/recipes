#!/usr/bin/env python3

import argparse
import csv
import logging
import os
from datetime import datetime
from urllib.parse import quote

import requests


# --- Parse CLI arguments ---
parser = argparse.ArgumentParser(description="Fetch SecureFlag user assignments.")
parser.add_argument("--org-id", help="Organization ID (overrides ORG_ID env var)")
parser.add_argument("--token", help="API token (overrides TOKEN env var)")
args = parser.parse_args()

# --- Config (env vars with CLI overrides) ---
ORG_ID = args.org_id or os.getenv("ORG_ID")
TOKEN = args.token or os.getenv("TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def format_date(date_str):
    if not date_str:
        return ""
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%m-%Y")
    except ValueError:
        return date_str


def get_users(org_id, token):
    """API1: Fetch *all* users for the org by paging until the API returns an empty list.
    Note: Some pages may legitimately contain < 20 users, so we do NOT stop on len(page) < 20.
    """
    page = 0  # If your API starts at 1, change this to 1
    users_list = []
    headers = {"Authorization": f"Bearer {token}"}

    while True:
        url = f"https://api.secureflag.com/rest/management/v2/organizations/{org_id}/users/{page}"
        try:
            resp = requests.get(url, headers=headers, timeout=30)
        except requests.RequestException as e:
            logging.error("Failed to fetch users on page %s: %s", page, e)
            break

        if resp.status_code != 200:
            logging.error("Failed to fetch users on page %s (status %s)", page, resp.status_code)
            break

        batch = resp.json() or []
        if not batch:
            # No more users
            break

        for user in batch:
            users_list.append({
                "First Name": user.get("firstName", ""),
                "Last Name": user.get("lastName", ""),
                "Email": user.get("email", ""),
                "Joined Date": format_date(user.get("joinedDateTime"))
            })

        # Always go to the next page regardless of how many were returned
        page += 1

    return users_list


def get_user_assignments(email, token):
    """API2: Fetch all assignments for the given email."""
    safe_email = quote(email, safe="")  # URL encode the email for the API path
    url = f"https://api.secureflag.com/rest/management/v2/users/{safe_email}/assigned"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        logging.warning("Failed to fetch assignments for %s: %s", email, e)
        return []

    if resp.status_code != 200:
        logging.warning("Failed to fetch assignments for %s (status %s)", email, resp.status_code)
        return []

    assignments = resp.json() or []
    cleaned = []
    for item in assignments:
        cleaned.append({
            "Due Date": format_date(item.get("expire")),
            "Assigned Date": format_date(item.get("assigned")),
            "Completed Date": format_date(item.get("completed")),
            "Status": item.get("status", ""),
            "Type": item.get("type", ""),
            "uuid": item.get("uuid")
        })
    return cleaned


def get_learning_path_name(uuid, token):
    """API3: Return the learning path name for UUID, or None. Logs non-200 for visibility."""
    if not uuid:
        return None
    url = f"https://api.secureflag.com/rest/management/v2/paths/{uuid}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            logging.warning("API3 failed for UUID %s (status %s)", uuid, resp.status_code)
            return None
        data = resp.json()
        return data.get("name") if isinstance(data, dict) else None
    except requests.RequestException as e:
        logging.warning("API3 request error for UUID %s: %s", uuid, e)
        return None


def get_exercise_title(uuid, token):
    """API4: Return the exercise title for UUID, or None. Logs non-200 for visibility."""
    if not uuid:
        return None
    url = f"https://api.secureflag.com/rest/management/v2/exercises/{uuid}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            logging.warning("API4 failed for UUID %s (status %s)", uuid, resp.status_code)
            return None
        data = resp.json()
        return data.get("title") if isinstance(data, dict) else None
    except requests.RequestException as e:
        logging.warning("API4 request error for UUID %s: %s", uuid, e)
        return None


def write_to_csv(data, filename="user_assignments.csv"):
    if not data:
        logging.info("No data to write.")
        return
    fieldnames = [
        "First Name", "Last Name", "Email", "Joined Date",
        "Activity Title", "Due Date", "Assigned Date", "Completed Date", "Status", "Type"
    ]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    logging.info("CSV file created: %s", os.path.abspath(filename))


def main():
    if not ORG_ID or not TOKEN:
        raise SystemExit("Missing ORG_ID/TOKEN. Set env vars or pass --org-id/--token.")
    logging.info("Fetching user details...")
    users = get_users(ORG_ID, TOKEN)
    logging.info("Found %d users", len(users))
    final_data = []
    lp_cache = {}
    ex_cache = {}
    for user in users:
        assignments = get_user_assignments(user["Email"], TOKEN)
        for assignment in assignments:
            title_value = ""
            # Normalise type to handle variants like "Learning Path" vs "LEARNING_PATH"
            type_raw = assignment.get("Type", "")
            type_val = str(type_raw).upper().replace(" ", "_")
            uuid = assignment.get("uuid")

            # Decide which API to call based on Type
            if type_val == "LEARNING_PATH":
                if uuid:
                    if uuid in lp_cache and lp_cache[uuid]:
                        title_value = lp_cache[uuid]
                    else:
                        lp_name = get_learning_path_name(uuid, TOKEN)
                        if lp_name:  # only cache truthy names
                            lp_cache[uuid] = lp_name
                            title_value = lp_name
                        else:
                            logging.info("No Activity Title for LEARNING_PATH UUID %s", uuid)
            elif type_val == "EXERCISE":
                if uuid:
                    if uuid in ex_cache and ex_cache[uuid]:
                        title_value = ex_cache[uuid]
                    else:
                        ex_title = get_exercise_title(uuid, TOKEN)
                        if ex_title:  # only cache truthy titles
                            ex_cache[uuid] = ex_title
                            title_value = ex_title
                        else:
                            logging.info("No Activity Title for EXERCISE UUID %s", uuid)

            # Build the CSV row
            row = {
                "First Name": user["First Name"],
                "Last Name": user["Last Name"],
                "Email": user["Email"],
                "Joined Date": user["Joined Date"],
                "Activity Title": title_value,
                "Due Date": assignment["Due Date"],
                "Assigned Date": assignment["Assigned Date"],
                "Completed Date": assignment["Completed Date"],
                "Status": assignment["Status"],
                "Type": assignment["Type"]
            }
            final_data.append(row)
    logging.info("Writing %d rows to CSV file...", len(final_data))
    write_to_csv(final_data)


if __name__ == "__main__":
    main()
