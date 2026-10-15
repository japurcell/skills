# Conditional Skill Installer

We need the ability to conditionally install skills based on specific criteria or context.

1. Create 2 subdirectories in [skills](../../../skills/):
   - `forest-service`: for skills specific to the Forest Service
   - `default`: for skills that should always be installed
2. Update `scripts/install.{sh,ps1}` to only install skills from `skills/forest-service` if a cli flag or environment variable is set. Skills in `skills/default` should always be installed. Ask me to decide the cli flag name and environment variable name with your recommendation.
3. Ensure that all CLI best practices from within `.agents/sources/` are followed now that the install scripts will accept flags.
