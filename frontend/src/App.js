import React from 'react';

function App() {
  return (
    <div className="App">
      <div className="camera">
        {/* Video MJPEG stream dal backend FastAPI */}
        <img src="http://localhost:8000/video_feed" alt="Video Feed" />
        <button>SNAP!</button>
      </div>
    </div>
  );
}

export default App;
