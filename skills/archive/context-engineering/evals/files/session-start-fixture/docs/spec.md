# Auth spec

## Login timeout

Web sessions created by `src/auth_service.py` should expire after 15 minutes of inactivity.

## Password reset

Password reset links remain valid for 24 hours.

## Billing exports

Billing exports run nightly at 01:00 UTC.
