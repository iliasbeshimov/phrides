# Security Guidelines

## 🔒 API Key Management

### NEVER commit API keys to Git
- All API keys must be stored in environment variables
- Use `.env` files for local development (never commit .env files)
- Use `.env.example` as a template for other developers

### Environment Variables Required
```bash
GOOGLE_MAPS_API_KEY=your_key_here
MAPBOX_ACCESS_TOKEN=your_token_here
```

### Safe Usage in Code
```python
from config import Config

# Safe way to use API keys
api_key = Config.get_google_maps_key()  # Raises error if not set
```

## 🛡️ Protection Mechanisms in Place

1. **Enhanced .gitignore** - Prevents accidental commits
2. **Pre-commit hooks** - Scans for API keys before commit
3. **Environment variable system** - Secure key management
4. **Configuration module** - Centralized secure access

## 🚨 If API Keys Are Exposed

1. **Immediately revoke** the exposed keys
2. **Generate new keys** in the respective platforms
3. **Update environment variables** with new keys
4. **Check billing/usage** for unauthorized access

## 📋 Security Checklist

- [ ] All API keys moved to environment variables
- [ ] `.env` file created and added to .gitignore
- [ ] Pre-commit hook installed and working
- [ ] Old exposed keys revoked and replaced
- [ ] Team members trained on secure practices

## 🔗 Key Management Platforms

- **Google Cloud Console**: https://console.cloud.google.com/apis/credentials
- **Mapbox Account**: https://account.mapbox.com/access-tokens/
- **GitHub Settings**: https://github.com/settings/security