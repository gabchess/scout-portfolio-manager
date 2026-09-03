# Data and privacy

The MVP reads synthetic JSON fixtures and stores no persistent user data. It does not call Zerion or any execution provider.

Future integrations must minimize retention to portfolio observations, user-approved basis, non-secret transaction references, and verification receipts. Credentials belong in a customer-controlled secret manager and must never enter logs, fixtures, prompts, or receipts.
