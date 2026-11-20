"""
One-time setup script: creates the Databricks secret scope and stores the
Currents API key. Run this locally (with the Databricks CLI configured) or
from a notebook - never commit the resulting secret value anywhere.

Usage:
    python setup_secrets.py
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
from databricks.sdk.errors import ResourceAlreadyExists
import getpass

w = WorkspaceClient()

# ----------------------------------------------------
# 1. Conditional Currents API Key Update
# ----------------------------------------------------
update_currents = input("Do you want to update the Currents API key? (yes/no): ").strip().lower()

if update_currents == 'yes':
    try:
        w.secrets.create_scope(scope="news-app")
    except ResourceAlreadyExists:
        pass

    w.secrets.put_secret(
        scope="news-app",
        key="currents-api-key",
        string_value=getpass.getpass("Paste your Currents API key: ")
    )

    w.secrets.put_acl(
        scope="news-app",
        principal="users",
        permission=workspace.AclPermission.READ,
    )
    print("✅ Currents API key updated successfully!")
else:
    print("⏭️ Skipped Currents API update.")

print("🎉 Setup script execution complete.")
