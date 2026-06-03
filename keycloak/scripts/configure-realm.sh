#!/usr/bin/env bash
# configure-realm.sh
# ==================
# Bootstrap the 'kalinalysis' Keycloak realm for local lab use.
# Requires the Keycloak admin CLI (kcadm.sh) to be in PATH, or
# the KCADM environment variable pointing to it.
#
# Environment variables (with defaults):
#   KC_URL        Keycloak base URL      (default: https://localhost:443/auth)
#   KC_ADMIN      Admin username          (default: admin)
#   KC_ADMIN_PASS Admin password          (default: changeme)
#   REALM_NAME    Realm to create         (default: kalinalysis)

set -euo pipefail

KC_URL="${KC_URL:-https://localhost:443/auth}"
KC_ADMIN="${KC_ADMIN:-admin}"
KC_ADMIN_PASS="${KC_ADMIN_PASS:-changeme}"
REALM_NAME="${REALM_NAME:-kalinalysis}"

KCADM="${KCADM:-kcadm.sh}"

echo "==> Configuring Keycloak realm: ${REALM_NAME}"
echo "    URL  : ${KC_URL}"
echo "    Admin: ${KC_ADMIN}"
echo ""

# Authenticate
echo "[1/5] Authenticating to Keycloak…"
"${KCADM}" config credentials \
  --server  "${KC_URL}" \
  --realm   master \
  --user    "${KC_ADMIN}" \
  --password "${KC_ADMIN_PASS}"

# Create realm
echo "[2/5] Creating realm '${REALM_NAME}'…"
"${KCADM}" create realms \
  --set "realm=${REALM_NAME}" \
  --set "enabled=true" \
  --set "displayName=KALINALYSIS Lab" \
  --set "sslRequired=external" \
  --set "registrationAllowed=false" \
  --set "loginWithEmailAllowed=true" \
  --set "duplicateEmailsAllowed=false" \
  --set "resetPasswordAllowed=true" \
  --set "editUsernameAllowed=false" \
  --set "bruteForceProtected=true" || echo "  Realm may already exist — continuing."

# Create admin group
echo "[3/5] Creating 'admins' group…"
"${KCADM}" create groups \
  --realm "${REALM_NAME}" \
  --set "name=admins" || echo "  Group may already exist — continuing."

# Create analyst group
echo "[4/5] Creating 'analysts' group…"
"${KCADM}" create groups \
  --realm "${REALM_NAME}" \
  --set "name=analysts" || echo "  Group may already exist — continuing."

# Create default demo user
echo "[5/5] Creating demo user 'analyst1'…"
"${KCADM}" create users \
  --realm "${REALM_NAME}" \
  --set "username=analyst1" \
  --set "email=analyst1@kalinalysis.local" \
  --set "enabled=true" \
  --set "firstName=Demo" \
  --set "lastName=Analyst" || echo "  User may already exist — continuing."

"${KCADM}" set-password \
  --realm "${REALM_NAME}" \
  --username analyst1 \
  --new-password "KaliDemo2024!" \
  --temporary

echo ""
echo "==> Realm '${REALM_NAME}' configured successfully."
echo "    Demo user: analyst1 / KaliDemo2024!  (temporary — must change on first login)"
