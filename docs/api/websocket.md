# WebSocket API

WebSocket endpoint for real-time face recognition and person identification.

## Overview

The WebSocket API provides a bidirectional communication channel for real-time face detection and recognition. This is the core functionality of the DDFR application, enabling continuous video frame processing and instant person identification.

## Architecture

The WebSocket implementation uses an asynchronous processing model:

1. **Client Connection**: Client establishes WebSocket connection to `/ws`
2. **Frame Transmission**: Client sends binary image data (JPEG/PNG encoded frames)
3. **Asynchronous Processing**: Server processes frames in a thread pool executor to avoid blocking
4. **Response Transmission**: Server returns JSON results with detected faces and identities
5. **Rate Limiting**: Handled client-side (recommended: 50ms intervals = 20 FPS)

## Performance Considerations

### Thread Pool Configuration

- **Executor**: Single-threaded (`max_workers=1`) to ensure sequential frame processing
- **Rationale**: Prevents race conditions and ensures consistent state during face recognition
- **Note**: NumPy threading is disabled via environment variables to prevent conflicts

### Processing Pipeline

1. **Image Decoding**: Binary bytes → OpenCV BGR frame
2. **Face Detection**: InsightFace model detects faces in frame
3. **Embedding Extraction**: Face features extracted as embedding vectors
4. **Person Identification**: FAISS/Numpy similarity search against database
5. **Response Formatting**: Results serialized as JSON

### Batch Processing

When multiple faces are detected in a single frame:
- All faces are processed in parallel during embedding extraction
- Batch identification is performed using vectorized operations
- Results maintain face-to-identity mapping

## Connection

### Endpoint

```
ws://localhost:8000/ws
```

For HTTPS:
```
wss://your-domain.com/ws
```

### Connection Lifecycle

1. **Connect**: Client initiates WebSocket handshake
2. **Accept**: Server accepts connection (`websocket.accept()`)
3. **Loop**: Continuous frame processing until disconnect
4. **Disconnect**: Graceful handling with `WebSocketDisconnect` exception

## Message Protocol

### Client → Server (Binary)

**Format**: Raw binary image data

**Supported Formats**:
- JPEG encoded images
- PNG encoded images
- Any format supported by OpenCV `imdecode()`

**Example** (JavaScript):
```javascript
const canvas = document.getElementById('video-canvas');
canvas.toBlob((blob) => {
  blob.arrayBuffer().then((buffer) => {
    websocket.send(buffer);
  });
}, 'image/jpeg', 0.8);
```

**Example** (Python):
```python
import cv2
import websockets

frame = cv2.imread('image.jpg')
_, buffer = cv2.imencode('.jpg', frame)
await websocket.send(buffer.tobytes())
```

### Server → Client (JSON)

**Format**: JSON object with status and faces array

**Response Structure**:
```json
{
  "status": "ok",
  "faces": [
    {
      "id": "123_456",
      "top": 100,
      "right": 300,
      "bottom": 400,
      "left": 200,
      "name": "John",
      "surname": "Doe",
      "age": 30,
      "relationship": "amico",
      "role": "guest"
    }
  ]
}
```

**Unknown Person Structure**:
```json
{
  "status": "ok",
  "faces": [
    {
      "id": "123_456",
      "top": 100,
      "right": 300,
      "bottom": 400,
      "left": 200,
      "name": "Unknown",
      "surname": null,
      "age": 0,
      "relationship": null,
      "role": null
    }
  ]
}
```

**Empty Response** (No faces detected):
```json
{
  "status": "ok",
  "faces": []
}
```

**Error Response** (Decoding failure):
Returns `null` (connection remains open, client should skip frame)

## Field Descriptions

### Face Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the face in format `"{top}_{left}"` (pixel coordinates) |
| `top` | integer | Top Y coordinate of bounding box |
| `right` | integer | Right X coordinate of bounding box |
| `bottom` | integer | Bottom Y coordinate of bounding box |
| `left` | integer | Left X coordinate of bounding box |
| `name` | string | Person's first name (or "Unknown" if not identified) |
| `surname` | string | Person's last name (or null if not identified) |
| `age` | integer | Calculated age based on birthday (or 0 if not identified) |
| `relationship` | string | Relationship type enum value (or null if not identified) |
| `role` | string | Person role enum value ("user" or "guest", or null if not identified) |

### Face ID Format

The `id` field uses pixel coordinates: `"{top}_{left}"` (e.g., `"100_200"`). This provides:
- Uniqueness within a frame
- Traceability for debugging
- Client-side face tracking capabilities

## Identification Process

### Threshold Configuration

The identification uses a similarity threshold of **0.4** (hardcoded in `process_image_sync`). This is more lenient than the default `APP_TOLLERANCE` setting to improve recognition accuracy.

**Similarity Score Range**:
- `0.0` - `1.0` (1.0 = identical match)
- Threshold `0.4` means matches above 40% similarity are accepted

### Database States

1. **Database Active** (`feature_matrix is not None`):
   - Full identification pipeline active
   - FAISS or NumPy similarity search performed
   - Matched persons returned with data

2. **Database Empty** (`feature_matrix is None`):
   - Fallback mode: detection only
   - Faces detected but no identification attempted
   - All faces marked as "Unknown"
   - Error logged for monitoring

### Batch Processing

When multiple faces are detected:
- All embeddings extracted simultaneously
- Single batch identification call for efficiency
- Results maintain order: `identities[i]` corresponds to `faces[i]`

## Error Handling

### Image Decoding Errors

- **Cause**: Invalid image format or corrupted data
- **Behavior**: Function returns `None`, error logged
- **Client Action**: Skip frame, continue with next

### Database Errors

- **Cause**: `feature_matrix` unavailable or empty
- **Behavior**: Fallback to detection-only mode, error logged
- **Client Action**: Receive faces with "Unknown" identity

### WebSocket Disconnection

- **Cause**: Client closes connection or network interruption
- **Behavior**: `WebSocketDisconnect` exception caught, connection cleaned up
- **Logging**: Info-level message recorded

### Processing Errors

- **Cause**: Unexpected exceptions during processing
- **Behavior**: Error logged, connection remains open
- **Client Action**: May receive null response, should handle gracefully

## Rate Limiting

**Client-Side Responsibility**: Rate limiting is handled on the frontend to maintain responsive UI.

**Recommended Rate**: 50ms intervals (20 FPS)

**Example Implementation**:
```javascript
let lastSend = 0;
const interval = 50; // ms

function sendFrame() {
  const now = Date.now();
  if (now - lastSend >= interval) {
    websocket.send(frameData);
    lastSend = now;
  }
}
```

## Example Usage

### JavaScript/WebSocket API

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('WebSocket connected');
  
  // Start sending frames from video
  setInterval(() => {
    const canvas = document.getElementById('canvas');
    canvas.toBlob((blob) => {
      blob.arrayBuffer().then((buffer) => {
        ws.send(buffer);
      });
    }, 'image/jpeg', 0.8);
  }, 50); // 20 FPS
};

ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('Detected faces:', result.faces);
  
  result.faces.forEach(face => {
    if (face.name !== 'Unknown') {
      console.log(`Identified: ${face.name} ${face.surname}`);
    }
  });
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

### Python Example

```python
import asyncio
import websockets
import cv2

async def send_frames():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                # Send binary data
                await websocket.send(buffer.tobytes())
                
                # Receive response
                response = await websocket.recv()
                result = json.loads(response)
                
                print(f"Faces detected: {len(result['faces'])}")
                
                # Rate limiting: ~20 FPS
                await asyncio.sleep(0.05)
                
        finally:
            cap.release()

asyncio.run(send_frames())
```

## Implementation Details

### Thread Pool Executor

The synchronous `process_image_sync` function is executed in a thread pool to avoid blocking the event loop:

```python
result = await loop.run_in_executor(executor, process_image_sync, data)
```

**Benefits**:
- Non-blocking I/O for WebSocket operations
- CPU-intensive processing in separate thread
- Maintains async architecture

### NumPy Threading Disabled

Environment variables are set to prevent NumPy threading conflicts:
```python
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
# ... etc
```

**Reason**: Prevents GIL contention and ensures consistent behavior.

## API Reference

::: app.routers.websocket.router

::: app.routers.websocket.websocket_endpoint

::: app.routers.websocket.process_image_sync

