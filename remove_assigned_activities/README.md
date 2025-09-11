# Bulk Unassignment of Pending Activities

Resolve UUIDs for activities and remove SecureFlag assignments for users via API's.
> Note: if an activity was assigned and it has been solved, it cannot be removed and will be marked as solved.
> Important: Once an activity has been unassigned, it cannot be undone and needs to be reassigned via the management UI or the assignment API's. 

### What it does

1. Fetches **fresh catalogs** every run:

   * `Learning-Path-Data.csv` from `/paths`
   * `Lab-Exercise-Data.csv` from `/exercises` (includes **all** exercise types and an extra `Type` column from `labType`)
2. Resolves/validates UUIDs in your input CSV (strict **exact** match by **Activity + Technology** when UUID is blank).
3. Performs a **preflight** over the entire input:

   * Halts if **any** row is invalid (prints errors and exits `1`).
4. Batches removals **per user** and calls the removal API once per user.
5. Prints a concise, per-user summary and “Completed successfully.” on success.

---

## Requirements

* Python 3.8+
* `requests`

  ```bash
  pip install requests
  ```

---

## Input/Output

### Input CSV (`--csv <path>`, lowercase `.csv` only)

**Headers (exact, in order):**

1. `User` (email)
2. `Activity` (Path name or Lab title)
3. `Technology`
4. `Type` (`Path` or `Lab`)
5. `UUID` (optional; blank allowed)

Accepts both Unix `\n` and Windows `\r\n` line endings.

This data can be obtained from the Track Progress Report in the platform [(see more details here)](https://helpcenter.secureflag.com/portal/en/kb/articles/track-assigned-activities).
When working with the report, use columns 2–5, which share the same headers.

> If you plan to use the report, ensure that you include only activities that do not have the status **“Solved”** or **“Already Solved”**

### Generated files

* `Learning-Path-Data.csv` — columns: `Name of LP,Technology,UUID`
* `Lab-Exercise-Data.csv` — columns: `Name of Lab,Technology,UUID,Type` (`Type` comes from `labType` as returned)
* `<input>-resolved.csv` — the resolved copy of your input; always **overwritten**; `-resolved` is inserted before `.csv`

---

## API Endpoints

* GET `https://api.secureflag.com/rest/management/v2/paths`
* GET `https://api.secureflag.com/rest/management/v2/exercises`
* POST `https://api.secureflag.com/rest/management/v2/users/removeAssignment`

**Headers**

* `Authorization: Bearer <TOKEN>`
* `Accept: application/json`
* `Content-Type: application/json` (POST only)

**Timeout:** 30s per request.

---

## Matching & Validation Rules

* If UUID present → **verify** it exists in the corresponding catalog (Path vs Lab).
* If UUID blank → resolve by **strict exact match** on:

  * `Activity` == `Name of LP` **and** `Technology` (for `Type = Path`)
  * `Activity` == `Name of Lab` **and** `Technology` (for `Type = Lab`)
* Comparisons are **case-sensitive** and **space-sensitive** (no trimming/normalization).
* If zero matches or multiple name+tech matches → **preflight error** and **halt**.
* `Type` must be exactly `Path` or `Lab` → otherwise **halt**.
* Duplicate rows are **not fatal**; removals are **deduplicated per user+type+UUID**.

---

## Removal Batching

One POST per **user** with both arrays when present:

```json
{
  "users": ["user@example.com"],
  "assignedLabs": ["..."],      // omit if empty
  "assignedPaths": ["..."]      // omit if empty
}
```

If a user has neither labs nor paths after deduplication → **preflight error** and **halt**.

If HTTP 200 but response body indicates partial failure → **treat as error** and **halt**.

No retries — fail fast and log the body.

---

## CLI

```bash
python remove_activities.py --token YOUR_TOKEN --csv customer1-to-remove.csv
```

Optional flags:

* `--dry-run` — validate and show intended actions, **no POSTs**
* `--verbose` — detailed logs (resolutions, payloads, bodies)

Examples:

```bash
# Dry-run + verbose
python remove_activities.py --token YOUR_TOKEN --csv customer1-to-remove.csv --dry-run --verbose
```

---

## Exit Codes & Output

* Prints startup banner.
* On success: per-user summaries and **“Completed successfully.”** → exit code `0`.
* On error: prints aggregated reasons (format: `User + UUID + reason`) → exit code `1`.

---

## Sample input header

```
User,Activity,Technology,Type,UUID
```

*(UUID column may be omitted in the input; it will appear in the `-resolved.csv`.)*

---

## Notes

* Catalog filenames are fixed. They’re regenerated **fresh** each run.
* Input file must use **lowercase** `.csv` extension.

---