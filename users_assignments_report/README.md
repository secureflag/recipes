# SecureFlag User Assignments Export Script

## Script Overview

This Python script automates the process of exporting **SecureFlag user assignments** into a structured CSV file.  
It:

1. Retrieves all users from a specified SecureFlag organization (paged results).
2. For each user, fetches all assigned activities (both **Exercises** and **Learning Paths**).
3. Retrieves the human-readable title for each assignment using the relevant API.
4. Outputs the consolidated data into a CSV file (`user_assignments.csv`).

**Workflow:**

- **API 1** (`/organizations/{id}/users/{page}`)  
  Returns paginated lists of users in the organization.
- **API 2** (`/users/{email}/assigned`)  
  Lists assignments for each user.
- **API 3** (`/paths/{uuid}`)  
  Retrieves the name of a learning path (if the assignment is of type `LEARNING_PATH`).
- **API 4** (`/exercises/{uuid}`)  
  Retrieves the title of an exercise (if the assignment is of type `EXERCISE`).

Data from APIs 3 and 4 are merged into the CSV as the **Activity Title**.

## Installation

Python version 3.7 or higher is required.

1. **Save the script** (e.g., as `get-users-and-assignment.py`).
2. **Install dependencies**:

   ```bash
   pip install requests
   ```

3. **Setup Authentication**: The script requires a **Bearer Token** for API authentication

    Refer to our [help center](https://helpcenter.secureflag.com/portal/en/kb/articles/using-apis) for instructions on obtaining your Bearer Token.

## Usage

There are two methods to run the script:

**Option 1: using environment variables** (recommended):

```bash
export ORG_ID=12345
export TOKEN=your_bearer_token_here
python fetch_assignments.py
```

**Option 2: Passing credentials via CLI**:
```bash
python fetch_assignments.py --org-id 12345 --token your_bearer_token_here
```

The script will create `user_assignments.csv` in the current directory.

## API Details

### **API 1: Retrieve Paged Organization Users**
- **Endpoint:**  
  `GET https://api.secureflag.com/rest/management/v2/organizations/{id}/users/{page}`
- **Path Parameters:**
  | Name | Type | Required | Description |
  |------|------|----------|-------------|
  | id   | integer | Yes | Organization ID |
  | page | integer | Yes | Page number starting from `0` |
- **Description:** Retrieves up to 20 users per page for the given organization.
- **Example Request:**
  ```bash
  curl -X GET "https://api.secureflag.com/rest/management/v2/organizations/12345/users/0" \
       -H "Authorization: Bearer <TOKEN>"
  ```
- **Example Response:**
  ```json
  [
    {
      "adminNoTraining": true,
      "alias": "string",
      "bounceCounter": 0,
      "compulsory": [
        "string"
      ],
      "compulsoryPaths": [
        "string"
      ],
      "country": {
        "id": 0,
        "name": "string",
        "shortName": "string"
      },
      "credits": 0,
      "dateLastBounce": "2025-08-13T09:38:37.214Z",
      "dateLastPermissionCleanup": "2025-08-13T09:38:37.214Z",
      "defaultOrganization": {
        "id": 0,
        "name": "string"
      },
      "email": "string",
      "emailVerified": true,
      "exercisesMinutes": 0,
      "exercisesRun": 0,
      "exernalAuthentication": true,
      "externalId": "string",
      "favouriteLanguage": "string",
      "firstName": "string",
      "forceChangePassword": true,
      "idUser": 0,
      "initTrainingPlan": true,
      "instanceLimit": 0,
      "invitationCodeRedeemed": "string",
      "jobType": "FULL_STACK_DEVELOPER",
      "joinedDateTime": "2025-08-13T09:38:37.214Z",
      "kbMinutes": 0,
      "kbRun": 0,
      "keyboard": "string",
      "languages": [
        "string"
      ],
      "lastLogin": "2025-08-13T09:38:37.214Z",
      "lastName": "string",
      "licenseEnd": "2025-08-13T09:38:37.214Z",
      "licenseStart": "2025-08-13T09:38:37.214Z",
      "mlb": true,
      "nickname": "string",
      "recurrentEmails": true,
      "registerInterestSubscriptionInCountry": "2025-08-13T09:38:37.214Z",
      "removedUsed": true,
      "role": 0,
      "score": 0,
      "status": "ACTIVE",
      "stripeCustomerId": "string",
      "stripeSubscriptionAutorenewal": true,
      "stripeSubscriptionId": "string",
      "tags": [
        "string"
      ],
      "team": {
        "idTeam": 0,
        "name": "string"
      },
      "username": "string",
      "uuid": "string"
    }
  ]
  ```

---

### **API 2: Get User Assigned Exercises**
- **Endpoint:**  
  `GET https://api.secureflag.com/rest/management/v2/users/{email}/assigned`
- **Path Parameters:**
  | Name  | Type | Required | Description |
  |-------|------|----------|-------------|
  | email | string | Yes | Username or email of the user |
- **Description:** Retrieves all exercises and learning paths assigned to the specified user.
- **Example Request:**
  ```bash
  curl -X GET "https://api.secureflag.com/rest/management/v2/users/john@example.com/assigned" \
       -H "Authorization: Bearer <TOKEN>"
  ```
- **Example Response:**
  ```json
  [
    {
      "admin": 0,
      "assigned": "2025-08-13T09:38:37.197Z",
      "collation": "string",
      "completed": "2025-08-13T09:38:37.197Z",
      "expire": "2025-08-13T09:38:37.197Z",
      "id": 0,
      "labsRun": [
        "string"
      ],
      "labsSolved": [
        "string"
      ],
      "run": 0,
      "source": "INITIAL",
      "status": "NOT_RUN",
      "trainingIteration": "string",
      "trainingPlan": "string",
      "type": "EXERCISE",
      "user": 0,
      "username": "string",
      "uuid": "string"
    }
  ]
  ```

---

### **API 3: Retrieve Learning Path Details**
- **Endpoint:**  
  `GET https://api.secureflag.com/rest/management/v2/paths/{uuid}`
- **Path Parameters:**
  | Name | Type | Required | Description |
  |------|------|----------|-------------|
  | uuid | string | Yes | Learning Path UUID |
- **Description:** Retrieves the details of a learning path, including its name.
- **Example Request:**
  ```bash
  curl -X GET "https://api.secureflag.com/rest/management/v2/paths/e7a86254-7699-4cbd-8dea-4ec44a9b60dc" \
       -H "Authorization: Bearer <TOKEN>"
  ```
- **Example Response:**
  ```json
    {
    "allowRenewal": true,
    "blackbox": true,
    "description": {
      "id": 0,
      "text": "string"
    },
    "difficulty": "string",
    "exercises": [
      "string"
    ],
    "framework": "string",
    "idPath": 0,
    "lastUpdate": "2025-08-13T09:38:37.177Z",
    "maxCompletionHours": 0,
    "minCompletionPercentage": 0,
    "monthsExpiration": 0,
    "name": "string",
    "privateLP": true,
    "refresherPercentage": 0,
    "requiredLP": "string",
    "resources": [
      {
        "duration": 0,
        "title": "string",
        "type": "KB",
        "uuid": "string"
      }
    ],
    "status": "AVAILABLE",
    "tags": [
      "string"
    ],
    "technology": "string",
    "uuid": "string"
  }
  ```

---

### **API 4: Retrieve Specific Available Exercise**
- **Endpoint:**  
  `GET https://api.secureflag.com/rest/management/v2/exercises/{uuid}`
- **Path Parameters:**
  | Name | Type | Required | Description |
  |------|------|----------|-------------|
  | uuid | string | Yes | Exercise UUID |
- **Description:** Retrieves details of a specific exercise, including its title.
- **Example Request:**
  ```bash
  curl -X GET "https://api.secureflag.com/rest/management/v2/exercises/0a019103-5915-4e70-8225-f8355cf8fcff" \
       -H "Authorization: Bearer <TOKEN>"
  ```
- **Example Response:**
  ```json
    {
    "author": "string",
    "category": "string",
    "description": "string",
    "difficulty": "string",
    "duration": 0,
    "framework": "string",
    "id": 0,
    "labType": "LAB",
    "lastUpdate": "2025-08-13T09:38:37.169Z",
    "privateLab": true,
    "questionsList": [
      {
        "category": "string",
        "flagQuestionList": [
          {
            "hintAvailable": true,
            "id": 0,
            "maxScore": 0,
            "optional": true,
            "selfCheckAvailable": true,
            "trivia": "string",
            "type": "string"
          }
        ],
        "id": 0,
        "kb": {
          "agnostic": true,
          "asvs": "string",
          "category": "string",
          "cwe": "string",
          "duration": 0,
          "fromHub": true,
          "id": 0,
          "kbDetailsMapping": {},
          "lastUpdate": "2025-08-13T09:38:37.169Z",
          "private": true,
          "status": "AVAILABLE",
          "technology": "string",
          "uuid": "string",
          "video": "string",
          "vulnerability": "string"
        },
        "ord": 0,
        "title": "string"
      }
    ],
    "score": 0,
    "stack": {
      "appStart": true,
      "beta": true,
      "framework": "string",
      "fromHub": true,
      "id": 0,
      "lastUpdate": "2025-08-13T09:38:37.169Z",
      "listed": true,
      "restart": true,
      "status": "AVAILABLE",
      "technology": "string",
      "uuid": "string"
    },
    "status": "AVAILABLE",
    "subtitle": "string",
    "tags": [
      "string"
    ],
    "technology": "string",
    "title": "string",
    "triviaCount": 0,
    "triviaType": "RANDOM",
    "trophyName": "string",
    "uuid": "string"
  }
  ```

---

## Example Output

**CSV Output (`user_assignments.csv`):**
| First Name | Last Name | Email              | Joined Date | Activity Title            | Due Date   | Assigned Date | Completed Date | Status    | Type          |
|------------|-----------|--------------------|-------------|---------------------------|------------|---------------|----------------|-----------|---------------|
| John       | Doe       | john@example.com   | 13-08-2025  | Secure Coding Basics      | 15-08-2025 | 13-08-2025    |                | NOT_RUN   | LEARNING_PATH |
| Jane       | Smith     | jane@example.com   | 13-08-2025  | SQL Injection Prevention  | 20-08-2025 | 13-08-2025    | 14-08-2025     | SOLVED | EXERCISE      |


**Field meanings:**
- **First Name / Last Name / Email**:User identity details.
- **Joined Date**: Date user joined the organization.
- **Activity Title**: Name of the assigned exercise or learning path.
- **Due Date**: Assignment expiry date.
- **Assigned Date**: Date the activity was assigned.
- **Completed Date**: Date the user completed the activity.
- **Status**: Current status (`NOT_RUN`, `SOLVED`, etc.).
- **Type**: Whether the activity is an `EXERCISE` or `LEARNING_PATH`.

---

## Troubleshooting & Notes

**Common issues:**
- **Missing ORG_ID/TOKEN**: The script will exit if credentials are not provided.
- **Invalid Token**: Results in `401 Unauthorized`.
- **Organization/User not found**: `404` error from API.
- **Rate limits**: SecureFlag may enforce rate limits; if encountered, implement request delays.

**API considerations:**
- API 1 pagination starts at `0`.
- User emails in API 2 must be URL-encoded.
- Script caches Learning Path and Exercise titles to reduce API calls.