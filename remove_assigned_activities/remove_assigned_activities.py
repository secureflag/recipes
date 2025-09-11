#!/usr/bin/env python3
import argparse
import csv
import os
import sys
import requests
import json

API_PATHS = "https://api.secureflag.com/rest/management/v2/paths"
API_EXERCISES = "https://api.secureflag.com/rest/management/v2/exercises"
API_REMOVE = "https://api.secureflag.com/rest/management/v2/users/removeAssignment"

CATALOG_PATHS = "Learning-Path-Data.csv"
CATALOG_LABS = "Lab-Exercise-Data.csv"

TIMEOUT = 30


def banner():
    print("=== SecureFlag Assignment Removal Script ===")


def fetch_catalogs(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Fetch Learning Paths
    resp = requests.get(API_PATHS, headers=headers, timeout=TIMEOUT)
    if resp.status_code != 200:
        sys.exit(f"Error fetching Learning Paths: {resp.status_code} {resp.text}")
    paths = resp.json()
    with open(CATALOG_PATHS, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name of LP", "Technology", "UUID"])
        for p in paths:
            writer.writerow([p["name"], p["technology"], p["uuid"]])

    # Fetch ALL Exercises (no filtering) and include labType as "Type"
    resp = requests.get(API_EXERCISES, headers=headers, timeout=TIMEOUT)
    if resp.status_code != 200:
        sys.exit(f"Error fetching Exercises: {resp.status_code} {resp.text}")
    exercises = resp.json()

    with open(CATALOG_LABS, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name of Lab", "Technology", "UUID", "Type"])
        for ex in exercises:
            writer.writerow([
                ex["title"],
                ex["technology"],
                ex["uuid"],
                ex.get("labType", "")
            ])

    return CATALOG_PATHS, CATALOG_LABS


def load_catalog(filename, name_field):
    catalog = {}
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row[name_field], row["Technology"])
            catalog.setdefault(key, []).append(row["UUID"])
    return catalog


def resolve_csv(input_file, paths_catalog, labs_catalog, verbose=False):
    base, ext = os.path.splitext(input_file)
    if ext != ".csv":
        sys.exit("Error: input file must have lowercase .csv extension")
    resolved_file = base + "-resolved.csv"

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)

        # Normalize headers: strip spaces and remove UTF-8 BOM if present
        raw_headers = reader.fieldnames or []
        norm_headers = [(h or "").strip().lstrip("\ufeff") for h in raw_headers]
        header_map = {nh: rh for nh, rh in zip(norm_headers, raw_headers)}

        # Required columns (UUID optional)
        required = ["User", "Activity", "Technology", "Type"]
        missing = [h for h in required if h not in header_map]
        if missing:
            sys.exit(f"Error: required column(s) missing: {', '.join(missing)}")

        rows = list(reader)

    errors = []
    for row in rows:
        user = row.get(header_map["User"], "")
        activity = row.get(header_map["Activity"], "")
        tech = row.get(header_map["Technology"], "")
        typ = row.get(header_map["Type"], "")
        uuid = row.get(header_map.get("UUID", "UUID"), "").strip()

        if typ not in ("Path", "Lab"):
            errors.append((user, uuid, f"Invalid Type: {typ}"))
            continue

        catalog = paths_catalog if typ == "Path" else labs_catalog

        if uuid:
            # Verify UUID exists in the chosen catalog
            found = any(uuid in uuids for uuids in catalog.values())
            if not found:
                errors.append((user, uuid, "UUID not found in catalog"))
        else:
            key = (activity, tech)
            if key not in catalog:
                errors.append((user, uuid, f"No match for {activity}+{tech}"))
            elif len(catalog[key]) > 1:
                errors.append((user, uuid, f"Multiple UUIDs for {activity}+{tech}"))
            else:
                resolved_uuid = catalog[key][0]
                row["UUID"] = resolved_uuid
                if verbose:
                    print(f"Resolved {typ} {activity}+{tech} -> {resolved_uuid}")

    if errors:
        print("Preflight validation failed:")
        for e in errors:
            print(f" User: {e[0]}, UUID: {e[1]}, Reason: {e[2]}")
        sys.exit(1)

    # Always write normalized output columns (ensure UUID exists)
    out_headers = ["User", "Activity", "Technology", "Type", "UUID"]
    with open(resolved_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_headers)
        writer.writeheader()
        for row in rows:
            out = {
                "User": row.get(header_map["User"], ""),
                "Activity": row.get(header_map["Activity"], ""),
                "Technology": row.get(header_map["Technology"], ""),
                "Type": row.get(header_map["Type"], ""),
                "UUID": row.get("UUID", row.get(header_map.get("UUID", "UUID"), "")),
            }
            writer.writerow(out)

    return resolved_file


def call_remove_api(token, resolved_file, dry_run=False, verbose=False):
    users = {}
    with open(resolved_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = row["User"]
            typ = row["Type"]
            uuid = row["UUID"]
            if not uuid:
                continue
            users.setdefault(user, {"Labs": set(), "Paths": set()})
            if typ == "Lab":
                users[user]["Labs"].add(uuid)
            elif typ == "Path":
                users[user]["Paths"].add(uuid)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    for user, data in users.items():
        assigned_labs = list(data["Labs"])
        assigned_paths = list(data["Paths"])

        if not assigned_labs and not assigned_paths:
            print(f"Preflight error: user {user} has no Labs or Paths after deduplication")
            sys.exit(1)

        payload = {"users": [user]}
        if assigned_labs:
            payload["assignedLabs"] = assigned_labs
        if assigned_paths:
            payload["assignedPaths"] = assigned_paths

        if dry_run:
            print(f"[Dry-run] Would remove for {user}: {json.dumps(payload)}")
            continue

        resp = requests.post(API_REMOVE, headers=headers, json=payload, timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"Error removing for {user}: {resp.status_code} {resp.text}")
            sys.exit(1)

        # Treat partial failures in body as errors
        try:
            body = resp.json()
        except Exception:
            body = {}

        if isinstance(body, dict) and any(k in body for k in ("error", "failed", "errors", "failures")):
            print(f"API reported error for {user}: {body}")
            sys.exit(1)

        print(f"Removed {len(assigned_paths)} Paths and {len(assigned_labs)} Labs for {user} [HTTP {resp.status_code}]")
        if verbose:
            print(f" Payload: {json.dumps(payload)}")
            print(f" Response: {resp.text}")


def main():
    parser = argparse.ArgumentParser(description="SecureFlag Assignment Removal Script")
    parser.add_argument("--token", required=True, help="API token for authentication")
    parser.add_argument("--csv", required=True, help="Input CSV file (lowercase .csv only)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without API calls")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug output")
    args = parser.parse_args()

    banner()

    paths_file, labs_file = fetch_catalogs(args.token)
    paths_catalog = load_catalog(paths_file, "Name of LP")
    labs_catalog = load_catalog(labs_file, "Name of Lab")

    resolved_file = resolve_csv(args.csv, paths_catalog, labs_catalog, args.verbose)

    call_remove_api(args.token, resolved_file, dry_run=args.dry_run, verbose=args.verbose)

    print("Completed successfully.")


if __name__ == "__main__":
    main()
