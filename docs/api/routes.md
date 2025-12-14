# REST API Routes

REST API endpoints for the DDFR face recognition application.

## Overview

The REST API provides standard HTTP endpoints for application interaction. Currently, the API includes a simple health check endpoint. Additional endpoints for person management and face recognition operations may be added in future versions.

## Base URL

All API endpoints are prefixed with the application base URL:
- Development: `http://localhost:8000`
- Production: Configure via `APP_HOST` and `APP_PORT` environment variables

## CORS Configuration

The API is configured with CORS middleware that allows:
- All origins (`*`)
- All methods (`*`)
- All headers (`*`)
- Credentials enabled

This configuration is suitable for development. For production, consider restricting allowed origins.

## Endpoints

### Health Check

#### `GET /`

Returns a simple greeting message indicating the server is active.

**Request:**
```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "message": "Hello World"
}
```

**Status Codes:**
- `200 OK`: Server is running and responding

**Use Cases:**
- Health check for monitoring systems
- Verify API server availability
- Simple connectivity test

## API Reference

::: app.routers.route.router

::: app.routers.route.home

