# Bulk Unassignment of Pending Activities

## Script Overview
This Python script **resolves activity UUIDs** and **removes SecureFlag user assignments** through APIs.
*Note: if an activity was assigned and it has been solved, it cannot be removed and will be marked as solved.*
*Important: Once an activity has been unassigned, it cannot be undone and needs to be reassigned via the management UI or the assignment APIs.*

### What it does

1. Fetches **fresh catalogs** every run:
   - `Learning-Path-Data.csv` from `/paths`
   - `Lab-Exercise-Data.csv` from `/exercises` (includes **all** exercise types and an extra `Type` column from `labType`)
2. Resolves/validates UUIDs in your input CSV (strict **exact** match by **Activity + Technology** when UUID is blank).
3. Performs a **preflight** over the entire input:
   - Halts if **any** row is invalid (prints errors and exits `1`).
4. Batch removals **per user**, performing one API request for each user.
5. Prints a concise, per-user summary and **"Completed successfully."** on success.

## Installation

Python version 3.8 or higher is required.

1. **Save the script** (e.g., as `remove_activities.py`).
2. **Install dependencies**:

   ```bash
   pip install requests
   ```

3. **Setup Authentication**: The script requires a **Bearer Token** for API authentication

    Refer to our [help center](https://helpcenter.secureflag.com/portal/en/kb/articles/using-apis) for instructions on obtaining your Bearer Token.

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

*If you plan to use the report, ensure that you include only activities that do not have the status **“Solved”** or **“Already Solved”***

### Generated Files

- **`Learning-Path-Data.csv`**  
  Columns: `Name of LP`, `Technology`, `UUID`

- **`Lab-Exercise-Data.csv`**  
  Columns: `Name of Lab`, `Technology`, `UUID`, `Type`  
  (`Type` comes from `labType` as returned)

- **`<input>-resolved.csv`**  
  A resolved copy of your input CSV. Always **overwritten**. `-resolved` is inserted before `.csv`

---

## API Endpoints

- `GET https://api.secureflag.com/rest/management/v2/paths`
- `GET https://api.secureflag.com/rest/management/v2/exercises`
- `POST https://api.secureflag.com/rest/management/v2/users/removeAssignment`

**Headers:**
- `Authorization: Bearer <TOKEN>`
- `Accept: application/json`
- `Content-Type: application/json` (POST only)

**Timeout:** `30s` per request.

---

## Matching & Validation Rules

- Verifies the UUID exists in the corresponding catalog (if UUID is present). Path vs Lab catalogs apply.
- Resolves using a **strict exact match** (If UUID is blank):
  - `Activity` == `Name of LP` **and** `Technology` (for `Type = Path`)
  - `Activity` == `Name of Lab` **and** `Technology` (for `Type = Lab`)
- Comparisons are **case-sensitive** and **space-sensitive** (no trimming/normalization).
- Fails with a **preflight error** and **halts** execution (if zero or multiple **name + tech** matches are found).
- `Type` must be exactly `Path` or `Lab` (otherwise **halts** execution).
- Duplicate rows are **not fatal**; removals are **deduplicated by: user + type + UUID**.

---

## Removal Batching

Processes one POST request per user, including both arrays if present:

```json
{
  "users": ["user@example.com"],
  "assignedLabs": ["..."],      // omit if empty
  "assignedPaths": ["..."]      // omit if empty
}
```

**Common issues:**
- Fails with a **preflight error** and **halts** execution (if a user has neither labs nor paths after deduplication).
- Fails with a **preflight error** and **halts** execution (if HTTP 200 is returned but the response body indicates a partial failure).
- **Fails fast** and logs the body (no retries).

---

## CLI Usage

```bash
python remove_activities.py --token YOUR_TOKEN --csv customer1-to-remove.csv
```

**Optional Flags:**

- `--dry-run` — validate and show intended actions, **no POSTs**
- `--verbose` — detailed logs (resolutions, payloads, bodies)

**Examples:**

```bash
# dry-run + verbose
python remove_activities.py --token YOUR_TOKEN --csv customer1-to-remove.csv --dry-run --verbose
```

---

## Exit Codes & Output

- Prints startup banner.
- **On success**: per-user summaries and **"Completed successfully."** → exit code `0`.
- **On error**: prints aggregated reasons (format: `User + UUID + reason`) → exit code `1`.

---

## Example Input Header

```
User,Activity,Technology,Type,UUID
```

*(UUID column may be omitted in the input; it will appear in the `-resolved.csv`.)*

---

## Notes

- Catalog filenames are fixed. They're regenerated **fresh** each run.
- Input file must use **lowercase** `.csv` extension.