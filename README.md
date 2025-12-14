<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradienthttps://capsule-render.vercel.app/api?type=waving&color=5cb85c&height=350&section=header&text=DDFR&fontSize=90&fontColor=FFFFFF&animation=fadeIn" />

</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/InsightFace-%23007ACC?style=for-the-badge&logo=python&logoColor=white" alt="InsightFace"/>
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB"/>
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/>
  <img src="https://img.shields.io/badge/Uvicorn-2C3E50?style=for-the-badge&logo=fastapi&logoColor=white" alt="Uvicorn"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"/>
</p>

## Table of Contents 

- [Description](#description)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Description

Memory is the quiet thread that weaves the tapestry of our identity. When that thread begins to fray, the world can become a fragmented, uncertain place. DDFR is not merely a computer vision system; it is a digital anchor designed to restore confidence and dignity to those living with dementia.

Leveraging a sophisticated modular architecture, DDFR acts as an external memory extension. It perceives the environment in real-time, identifying the faces of loved ones—friends, family, caregivers—and discreetly bridges the cognitive gap. Currently, the system provides immediate visual identification, transforming the anxiety of the unknown into the comfort of familiarity. It is technology stepping back to let humanity come forward, helping to keep the most precious bonds alive.

## Technologies

DDFR is built on a modern and modular architecture, designed to ensure real-time responses (crucial for patient assistance) and future scalability towards generative AI.

### Frontend & User Experience
The user interface is developed to be accessible, clear, and immediate.

* **React:** Used to create a reactive and fluid Single Page Application (SPA). The visual component is optimized to ensure readability and ease of use.
* **npm:** Manages the dependency ecosystem, ensuring a stable and up-to-date development environment.

### Backend & Core Performance
The heart of the system is a robust backend that handles high-speed data flow.

* **Python:** The reference language for data processing and artificial intelligence.
* **FastAPI:** Chosen for its exceptional performance. It provides the REST APIs that connect the system's eye (the camera) to the brain (the server).
* **Uvicorn:** The ASGI server that keeps the system online and responsive, handling multiple requests without perceptible latency.

### Database & Data Storage
The system's long-term memory, essential for flexible data storage.

* **MongoDB:** A document-oriented NoSQL database chosen for its scalability in managing complex data structures, such as relative registries and biometric vectors.

### Computer Vision (AI)
* **InsightFace:** Advanced face recognition framework providing state-of-the-art face detection and embedding extraction. The system uses InsightFace's pre-trained models to map and identify known faces with high accuracy and reliability. The engine supports GPU acceleration (CUDA, CoreML, DML) when available, with automatic fallback to CPU execution.

## Installation

Setting up DDFR involves preparing the environment where the digital memory will reside. The process is automated to ensure all dependencies—from the visual cortex to the database connection—are correctly aligned.

### 1. Prerequisite Automation
We have prepared automated scripts to handle the installation of the necessary libraries and system requirements.

* **Windows:** Execute `setup.bat`
* **Linux/MacOS:** Execute `setup.sh`

### 2. Configuration
Before the system can breathe, it requires configuration. DDFR relies on specific environment variables to manage secure connections and database access.

**Backend Configuration**
Please refer to the technical documentation for the Python environment setup: [Config Documentation](https://fdemusso.github.io/DDFR/config/config/)

**Frontend Configuration**
Create a `.env.development.local` file in the frontend directory. This establishes the secure link (HTTPS) required for webcam access and defines the WebSocket protocol for real-time communication.

```env
HTTPS=true
SSL_KEY_FILE=<path_to_your_key.pem>
SSL_CRT_FILE=<path_to_your_cert.pem>
HOST=ddfr.local
PORT=3000
REACT_APP_WS_HOST=ddfr.local
REACT_APP_WS_PORT=8000
REACT_APP_WS_PROTOCOL=wss
```

*Note: Ensure your SSL certificates are generated and placed correctly to allow the browser to trust the local camera stream.*

## Usage

Once the environment is prepared, the system must be awakened manually. The architecture requires the simultaneous operation of the brain (backend) and the eyes (frontend).

### Awakening the System

1. **Start the Database:** Ensure your MongoDB instance is running locally.
2. **Start the Brain:** In your terminal, navigate to the backend directory and launch the secure server:
```bash
python main.py https
```


3. **Open the Eyes:** In a separate terminal, launch the user interface:
```bash
npm start
```



### The Experience

Upon launching, the browser will request permission to access the webcam. This is the moment the system begins to observe. Currently, the recognition data—the faces of relatives and friends—must be manually curated in the database (admin phase).

When a known face appears before the camera, DDFR processes the biometric data and provides immediate text-based feedback on the screen, identifying the person. This text is the precursor to the upcoming "human-like" text-to-speech engine.

## Contributing

We are currently in the phase of solidifying the foundation. The core logic for recognition is complete, and we are not looking for new feature implementations at this moment.

Our primary need is for **Testers** and **Code Reviewers**.

* **Code Review:** We need architects to review the codebase for cleanliness, order, and adherence to best practices.
* **Testing:** Verification of the installation scripts and the stability of the WebSocket connections across different environments.

If you wish to help polish this digital companion, please verify the code structure and report any inconsistencies.

## License

Distributed under the *GPLv3* license. See `LICENSE` for more information.