#!/usr/bin/env bash
# create-client.sh
# ================
# Register an OIDC client in the 'kalinalysis' realm for the Malcolm
# OpenSearch Dashboards integration.
#
# Environment variables (with defaults):
#   KC_URL          Keycloak base URL       (default: https://localhost:443/auth)
#   KC_ADMIN        Admin username           (default: admin)
#   KC_ADMIN_PASS   Admin password           (default: changeme)
#   REALM_NAME      Target realm             (default: kalinalysis)
#   CLIENT_ID       OIDC client ID           (default: malcolm)
#   CLIENT_SECRET   OIDC client secret       (default: auto-generated via uuidgen)
#   REDIRECT_URI    Allowed redirect URI     (default: https://localhost:443/*)

set -euo pipefail

KC_URL="${KC_URL:-https://localhost:443/auth}"
KC_ADMIN="${KC_ADMIN:-admin}"
KC_ADMIN_PASS="${KC_ADMIN_PASS:-changeme}"
REALM_NAME="${REALM_NAME:-kalinalysis}"
CLIENT_ID="${CLIENT_ID:-malcolm}"
CLIENT_SECRET="${CLIENT_SECRET:-$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)}"
REDIRECT_URI="${REDIRECT_URI:-https://localhost:443/*}"

KCADM="${KCADM:-kcadm.sh}"

echo "==> Registering OIDC client '${CLIENT_ID}' in realm '${REALM_NAME}'"
echo ""

# Authenticate
echo "[1/3] Authenticating…"
"${KCADM}" config credentials \
  --server   "${KC_URL}" \
  --realm    master \
  --user     "${KC_ADMIN}" \
  --password "${KC_ADMIN_PASS}"

# Create client
echo "[2/3] Creating client '${CLIENT_ID}'…"
"${KCADM}" create clients \
  --realm "${REALM_NAME}" \
  --set "clientId=${CLIENT_ID}" \
  --set "enabled=true" \
  --set "protocol=openid-connect" \
  --set "publicClient=false" \
  --set "secret=${CLIENT_SECRET}" \
  --set "standardFlowEnabled=true" \
  --set "implicitFlowEnabled=false" \
  --set "directAccessGrantsEnabled=false" \
  --set "serviceAccountsEnabled=false" \
  --set "redirectUris=[\"${REDIRECT_URI}\"]" \
  --set "webOrigins=[\"+\"]" \
  --set "fullScopeAllowed=true" || echo "  Client may already exist — continuing."

# Add client scope mapper for groups
echo "[3/3] Adding groups mapper…"
"${KCADM}" create clients/"$("${KCADM}" get clients --realm "${REALM_NAME}" --fields id,clientId 2>/dev/null | python3 -c "
import sys, json
clients = json.load(sys.stdin)
for c in clients:
    if c.get('clientId') == '${CLIENT_ID}':
        print(c['id'])
        break
")"/protocol-mappers/models \
  --realm "${REALM_NAME}" \
  --set "name=groups" \
  --set "protocol=openid-connect" \
  --set "protocolMapper=oidc-group-membership-mapper" \
  --set "config.full.path=false" \
  --set "config.id.token.claim=true" \
  --set "config.access.token.claim=true" \
  --set "config.claim.name=groups" \
  --set "config.userinfo.token.claim=true" || echo "  Mapper may already exist — continuing."

echo ""
echo "==> Client '${CLIENT_ID}' registered."
echo "    Client secret: ${CLIENT_SECRET}"
echo ""
echo "    Add these to your Malcolm .env or auth configuration:"
echo "    OIDC_CLIENT_ID=${CLIENT_ID}"
echo "    OIDC_CLIENT_SECRET=${CLIENT_SECRET}"
echo "    OIDC_ISSUER_URL=${KC_URL}/realms/${REALM_NAME}"
