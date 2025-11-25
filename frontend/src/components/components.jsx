import React from 'react';

const CameraComponent = () => {
  return (
    <div className="camera">
      {/* Video MJPEG stream dal backend FastAPI */}
      <img src="http://localhost:8000/video_feed" alt="Video Feed" />
      <button>SNAP!</button>
    </div>
  );
};

const ChatContainer = () => {
  return (
    <div className="ChatContainer">
      <h2>Chat</h2>
      <label className="ChatLabel">Ciccio</label>
      <button className="SendButton" /*onClick={/*funzione al click}*/>Send</button>


    </div>
  );
};
export { ChatContainer, CameraComponent };