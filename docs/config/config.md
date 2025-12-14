# Configuration

Configuration module for application settings.

## Environment Variables (.env)

The application configuration is managed through environment variables loaded from a `.env` file located in the `backend/app/` directory.

### Configuration File Structure

Create a `.env` file in `backend/app/` with the following structure:

```env
# --- Database Section (Prefix: DB_) ---
DB_URL=mongodb://localhost:27017/
DB_NAME=ddfr_db
DB_COLLECTION=people
DB_HASH="300a31fbdc6f3ff4fb27625c2ed49fdc"

# --- Logging Section (Prefix: LOG_) ---
LOG_LOGFOLDER=logs

# --- API Section (Prefix: APP_) ---
APP_NAME=DDFR API
APP_VERSION=1.0.0
APP_DESCRIPTION=API for face recognition and person management
APP_TOLLERANCE=0.5
APP_DEBUG=false
APP_HOST=0.0.0.0
APP_PORT=8000
APP_USE_HTTPS=false
APP_KEYPATH=
APP_CERTPATH=
```

### Variable Descriptions

#### Database Settings (Prefix: `DB_`)

- **`DB_URL`** (string): MongoDB connection URL. 
  - Default: `"mongodb://localhost:27017/"`
  - Example: `"mongodb+srv://user:password@cluster.mongodb.net/"`

- **`DB_NAME`** (string): Database name.
  - Default: `"ddfr_db"`

- **`DB_COLLECTION`** (string): MongoDB collection name for storing person data.
  - Default: `"people"`

- **`DB_HASH`** (string): Legacy hash value (currently not actively used, kept for backward compatibility).
  - Value: `"300a31fbdc6f3ff4fb27625c2ed49fdc"`

#### Logging Settings (Prefix: `LOG_`)

- **`LOG_LOGFOLDER`** (string): Directory path for log files. If not specified, defaults to `logs-{timestamp}` in the backend directory.
  - Example: `"logs"` or `"C:/logs/ddfr"`

#### API Settings (Prefix: `APP_`)

- **`APP_NAME`** (string): Application name displayed in API documentation.
  - Default: `"DDFR API"`

- **`APP_VERSION`** (string): Application version.
  - Default: `"1.0.0"`

- **`APP_DESCRIPTION`** (string): Application description displayed in API documentation.
  - Default: `"API for face recognition and person management"`

- **`APP_TOLLERANCE`** (float): Face recognition similarity threshold (0.0-1.0). Lower values are more strict.
  - Default: `0.5`
  - Recommended range: `0.4-0.6`
  - **⚠️ Deprecated**: This setting is being phased out and used less frequently. Consider using hardcoded thresholds in the recognition service instead.

- **`APP_DEBUG`** (boolean): Enable debug mode. When enabled, provides more verbose logging.
  - Default: `false`
  - Values: `true` or `false`

- **`APP_HOST`** (string): Server host address to bind to.
  - Default: `"0.0.0.0"` (listens on all interfaces)
  - For localhost only: `"127.0.0.1"`

- **`APP_PORT`** (integer): Server port number.
  - Default: `8000`

- **`APP_USE_HTTPS`** (boolean): Enable HTTPS support.
  - Default: `false`
  - Values: `true` or `false`

- **`APP_KEYPATH`** (string, optional): Path to SSL private key file (required if `APP_USE_HTTPS=true`).
  - Default: `None` (empty)
  - Example: `"C:/path/to/key.pem"` (Windows) or `"/path/to/key.pem"` (Mac/Linux)

- **`APP_CERTPATH`** (string, optional): Path to SSL certificate file (required if `APP_USE_HTTPS=true`).
  - Default: `None` (empty)
  - Example: `"C:/path/to/cert.pem"` (Windows) or `"/path/to/cert.pem"` (Mac/Linux)

### Creating SSL Certificates

To enable HTTPS, you need to generate SSL certificates. Here are some common approaches:

#### Using mkcert (Recommended for Development)

[mkcert](https://github.com/FiloSottile/mkcert) is a simple tool for making locally-trusted development certificates:

1. **Install mkcert**:
   - Windows: `choco install mkcert` or download from [GitHub releases](https://github.com/FiloSottile/mkcert/releases)
   - macOS: `brew install mkcert`
   - Linux: See [installation instructions](https://github.com/FiloSottile/mkcert#linux)

2. **Install the local CA**:
   ```bash
   mkcert -install
   ```

3. **Generate certificate for your domain**:
   ```bash
   mkcert ddfr.local localhost 127.0.0.1 ::1
   ```
   This creates `ddfr.local+2.pem` (certificate) and `ddfr.local+2-key.pem` (private key)

4. **Update your .env file**:
   ```env
   APP_USE_HTTPS=true
   APP_KEYPATH=/path/to/ddfr.local+2-key.pem
   APP_CERTPATH=/path/to/ddfr.local+2.pem
   ```

#### Using OpenSSL (Manual)

For manual certificate generation using OpenSSL:

1. **Generate a private key**:
   ```bash
   openssl genrsa -out key.pem 2048
   ```

2. **Create a certificate signing request (CSR)**:
   ```bash
   openssl req -new -key key.pem -out csr.pem
   ```

3. **Generate a self-signed certificate**:
   ```bash
   openssl x509 -req -days 365 -in csr.pem -signkey key.pem -out cert.pem
   ```

**Note**: Self-signed certificates will show security warnings in browsers. For production, use certificates from a trusted Certificate Authority (CA).

#### Production Certificates

For production environments, consider:
- **Let's Encrypt**: Free, automated SSL certificates - [https://letsencrypt.org/](https://letsencrypt.org/)
- **Cloudflare**: Provides free SSL certificates for proxied domains
- **Commercial CAs**: Various providers offer SSL certificates (DigiCert, GlobalSign, etc.)

#### Additional Resources

- [mkcert Documentation](https://github.com/FiloSottile/mkcert)
- [OpenSSL Certificate Authority](https://www.openssl.org/docs/manpages.html)
- [FastAPI HTTPS Documentation](https://fastapi.tiangolo.com/deployment/https/)

### Configuration Classes

## DatabaseSettings

::: app.config.DatabaseSettings

## PathSettings

::: app.config.PathSettings

## APISettings

::: app.config.APISettings

