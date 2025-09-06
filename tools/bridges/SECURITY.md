# ThreadVault Bridge Security Guide

## Token Management

### API Token
- **Purpose:** Standard API access for read/write operations
- **Environment:** `API_TOKEN=your-secure-token`
- **Rotation:** Recommended every 30 days
- **Generate:** `openssl rand -hex 32`

### Admin Token
- **Purpose:** Administrative operations like `/sync` endpoint
- **Environment:** `ADMIN_TOKEN=your-admin-token` 
- **Rotation:** Recommended every 14 days
- **Generate:** `openssl rand -hex 32`
- **Note:** If not set, admin endpoints return 503 Service Unavailable

## Token Rotation Procedure

1. **Generate new tokens:**
   ```bash
   export NEW_API_TOKEN=$(openssl rand -hex 32)
   export NEW_ADMIN_TOKEN=$(openssl rand -hex 32)
   ```

2. **Update environment variables in deployment**

3. **Test connectivity with new tokens**

4. **Update mobile shortcuts/automations with new API token**

5. **Secure old tokens:**
   ```bash
   unset OLD_API_TOKEN OLD_ADMIN_TOKEN
   ```

## Security Headers

- **CORS:** Restricted to `https://chat.openai.com` and `https://chatgpt.com`
- **Bearer Auth:** Required for all endpoints except `/health`
- **Admin Auth:** Separate token required for destructive operations

## Deployment Security

- Never store tokens in files - use environment variables only
- Use short-lived tokens (30 days max) with rotation
- Monitor access logs for unusual patterns
- Disable admin endpoints in public deployments if not needed

## Cloudflared Binary Management

- Binary excluded from Git to prevent supply chain attacks
- Download and pin specific version at runtime
- Verify checksums before execution
- Store in temporary cache directory outside repository