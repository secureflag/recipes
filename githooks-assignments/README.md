# SecureFlag Assignment Completion Pre-Push Hook

The `pre-push-assignments` hook enforces SecureFlag assignment completion requirements before allowing pushes.

## What does it do?

- Verifies that the user has met one of the configurable assignment requirements:
  - **Completed initial assignments**: All onboarding or initial training assignments are complete
  - **Completed pending assignments**: All currently pending assignments are complete
  - **No expired assignments**: The user has no assignments that have passed their deadline
- **Blocks the push** if the user has not met the configured requirement, with clear instructions on what needs to be completed.

## Installation

1. **Copy the hook to your repository's `.git/hooks/` directory:**

   ```sh
   cp pre-push-assignments .git/hooks/pre-push
   chmod +x .git/hooks/pre-push
   ```

2. **Install dependencies:**
   - Ensure [`jq`](https://stedolan.github.io/jq/) is installed and available in your `PATH`.

3. **Set required environment variables:**

   - `SECUREFLAG_API_TOKEN`: SecureFlag API token. Generate at https://www.secureflag.com/management/index.html#/settings
   - **Optionally**, set ONE of the following requirement flags to override the default (only set ONE at a time):
     - `REQUIRE_COMPLETED_INITIAL_ASSIGNMENTS`: Requires the user to have completed initial assignments (**default**)
     - `REQUIRE_COMPLETED_PENDING_ASSIGNMENTS`: Requires the user to have completed all pending assignments
     - `REQUIRE_NOT_EXPIRED_ASSIGNMENTS`: Requires the user to have no expired assignments

   You can export these in your shell profile or set them before pushing:

   ```sh
   export SECUREFLAG_API_TOKEN=sf_xxx
   # The hook defaults to checking initial assignments
   # To use a different requirement, set one of the flags:
   # export REQUIRE_COMPLETED_PENDING_ASSIGNMENTS=true
   ```

## Usage

Once installed, the hook runs automatically on every push. It will:

1. Check which assignment requirement flag is set
2. Verify your assignment status via the SecureFlag API
3. Allow the push if requirements are met, or block it with helpful error messages if not

The hook runs on **every push**, checking requirements before code is pushed to the remote repository.

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECUREFLAG_API_TOKEN` | Yes | SecureFlag API token for assignment verification |
| `REQUIRE_COMPLETED_INITIAL_ASSIGNMENTS` | No (default: true) | Require completion of initial assignments |
| `REQUIRE_COMPLETED_PENDING_ASSIGNMENTS` | No | Require completion of all pending assignments |
| `REQUIRE_NOT_EXPIRED_ASSIGNMENTS` | No | Require no expired assignments |
| `USER_EMAIL` | No | Override the email used for verification (defaults to git config user.email) |
| `SECUREFLAG_API_ENDPOINT` | No | Override the SecureFlag API endpoint (defaults to the assignments endpoint) |

**Important**: By default, the hook checks for completed initial assignments. You can override this by setting exactly ONE of the three requirement flags. Setting more than one will result in an error.

### Choosing the Right Requirement Flag

#### `REQUIRE_COMPLETED_INITIAL_ASSIGNMENTS` (Default)
This is the **default** requirement if no flag is set. Use this for:
- Onboarding new team members
- Ensuring basic security training is complete before contributing
- Initial compliance verification

This is enabled by default. To explicitly disable it and use a different requirement, set one of the other flags.

#### `REQUIRE_COMPLETED_PENDING_ASSIGNMENTS`
Use this for:
- Continuous compliance enforcement
- Ensuring all assigned training is up to date
- Strict training completion policies

Example:
```sh
export REQUIRE_COMPLETED_PENDING_ASSIGNMENTS=true
```

#### `REQUIRE_NOT_EXPIRED_ASSIGNMENTS`
Use this for:
- Preventing work when training has lapsed
- Ensuring timely completion of time-sensitive training
- Deadline enforcement

Example:
```sh
export REQUIRE_NOT_EXPIRED_ASSIGNMENTS=true
```

## How It Works

1. **Flag Validation**: Verifies that exactly one requirement flag is set
2. **Email Detection**: Gets the user email from git config or `USER_EMAIL`
3. **API Request**: Sends a targeted request to SecureFlag API with the specific requirement:
   - For initial assignments: `{"user":"email@example.com","hasCompletedInitialAssignments":true}`
   - For pending assignments: `{"user":"email@example.com","hasCompletedPendingAssignments":true}`
   - For expired assignments: `{"user":"email@example.com","hasNotExpiredAssignments":true}`
4. **Decision**: Blocks the push if the requirement is not met

## Error Handling

The hook handles various error scenarios gracefully:

- **Missing jq**: Displays a warning and allows the push
- **Missing token**: Blocks the push with clear instructions
- **No flag set**: Blocks the push and explains which flags are available
- **Multiple flags set**: Blocks the push and shows which flags are currently set
- **Invalid email**: Warns and allows the push if the email isn't registered in SecureFlag
- **API errors**: Warns and allows the push if the SecureFlag API is unavailable

## Example Output

### Successful Verification
```
[secureflag-assignments] Verifying completed initial assignments for user@example.com
[secureflag-assignments] Assignment verification succeeded: "user@example.com" meets requirement: completed initial assignments
```

### Blocked Push
```
[secureflag-assignments] Verifying completed pending assignments for user@example.com

[secureflag-assignments] ❌ Git push blocked. You must meet the following requirement before pushing:
- completed pending assignments

Visit https://www.secureflag.com/ to view your assignments.
```

### Multiple Flags Error
```
[secureflag-assignments] ERROR: Only one assignment requirement flag can be set at a time.
Currently set flags:
  - REQUIRE_COMPLETED_INITIAL_ASSIGNMENTS
  - REQUIRE_COMPLETED_PENDING_ASSIGNMENTS
```

## Troubleshooting

### "jq is required but not installed"
Install jq using your package manager:
```sh
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq

# Fedora/RHEL
sudo dnf install jq
```

### "SECUREFLAG_API_TOKEN must be set"
Make sure you've exported the token. Check with:
```sh
echo $SECUREFLAG_API_TOKEN
```

### Changing the Default Requirement
By default, the hook checks for completed initial assignments. To use a different requirement:
```sh
# To check for completed pending assignments instead
export REQUIRE_COMPLETED_PENDING_ASSIGNMENTS=true
# OR to check for no expired assignments
export REQUIRE_NOT_EXPIRED_ASSIGNMENTS=true
```

### "Only one assignment requirement flag can be set at a time"
You've set multiple flags. Unset all but one:
```sh
unset REQUIRE_COMPLETED_INITIAL_ASSIGNMENTS
unset REQUIRE_COMPLETED_PENDING_ASSIGNMENTS
# Keep only the one you want
export REQUIRE_NOT_EXPIRED_ASSIGNMENTS=true
```

### "User is not a valid user in SecureFlag"
Your git email must match your SecureFlag account email. Either:
1. Update your git email: `git config user.email "your-secureflag-email@example.com"`
2. Or set `USER_EMAIL` environment variable: `export USER_EMAIL="your-secureflag-email@example.com"`

## Different Requirements for Different Environments

You can use different requirement flags in different environments:

### Development Environment
Allow developers to work freely but require initial training:
```sh
# In ~/.bashrc or ~/.zshrc
export SECUREFLAG_API_TOKEN=sf_xxx
export REQUIRE_COMPLETED_INITIAL_ASSIGNMENTS=true
```

### Staging/Production Branches
Enforce stricter requirements for protected branches using branch-specific configurations:
```sh
# In CI/CD for production branch
export SECUREFLAG_API_TOKEN=sf_xxx
export REQUIRE_COMPLETED_PENDING_ASSIGNMENTS=true
```

## Bypassing the Hook (Not Recommended)

In emergencies, you can bypass the hook with:
```sh
git push --no-verify
```

However, this defeats the purpose of the security compliance check and is not recommended.

## Integration with CI/CD

To use this hook in CI/CD pipelines:

1. Install the hook in your CI environment
2. Set `SECUREFLAG_API_TOKEN` and the appropriate requirement flag as CI secrets
3. Ensure `jq` is available in the CI image
4. The hook will run automatically on pushes

Example GitLab CI configuration:
```yaml
variables:
  SECUREFLAG_API_TOKEN: $SECUREFLAG_TOKEN
  REQUIRE_COMPLETED_PENDING_ASSIGNMENTS: "true"

before_script:
  - apt-get update && apt-get install -y jq
  - cp pre-push-assignments .git/hooks/pre-push
  - chmod +x .git/hooks/pre-push
```

## Combining with Other Hooks

Since Git only allows one `pre-push` hook at a time, you can:

1. **Combine with other pre-push hooks**: Create a wrapper script that runs multiple checks
2. **Use a hook manager**: Tools like [Husky](https://typicode.github.io/husky/) or [pre-commit](https://pre-commit.com/) support multiple hooks
3. **Chain with commit hooks**: Use this pre-push hook alongside commit-msg hooks for comprehensive validation

## Learn More

- [SecureFlag Platform](https://www.secureflag.com/)
- [SecureFlag Management Portal](https://www.secureflag.com/management)
- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
