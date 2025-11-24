<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradienthttps://capsule-render.vercel.app/api?type=waving&color=5cb85c&height=350&section=header&text=DDFR&fontSize=90&fontColor=FFFFFF&animation=fadeIn" />

</div>



<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FaceRecognition-%23007ACC?style=flat&logo=python&logoColor=white" alt="FaceRecognition"/>
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white" alt="MongoDB"/>
  <img src="https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB" alt="React"/>
  <img src="https://img.shields.io/badge/Uvicorn-2C3E50?style=flat&logo=fastapi&logoColor=white" alt="Uvicorn"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black" alt="JavaScript"/>
</p>


## Table of Contents 

- [Description](#description)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Description

DDFR is not just a computer vision system; it is a digital companion designed to restore confidence to those living with dementia. Thanks to advanced technology, the system recognizes the faces of friends and relatives in real-time, discreetly whispering to the patient who is in front of them and recalling past conversations. DDFR transforms uncertainty into familiarity, helping to keep the most precious bonds alive day after day.

## Technologies

DDFR is built on a modern and modular architecture, designed to ensure real-time responses (crucial for patient assistance) and future scalability towards generative AI.

### Frontend & User Experience
The user interface is developed to be accessible, clear, and immediate.

* **React:** Used to create a reactive and fluid Single Page Application (SPA). The visual component is optimized to ensure readability and ease of use, essential factors for the target audience.
* **npm:** Manages the dependency ecosystem, ensuring a stable and up-to-date development environment.

### Backend & Core Performance
The heart of the system is a robust backend that handles high-speed data flow.

* **Python:** The reference language for data processing and artificial intelligence.
* **FastAPI:** Chosen for its exceptional performance and ability to handle asynchronous operations. It provides the REST APIs that connect the system's eye (the camera) to the brain (the server) and the user interface.
* **Uvicorn:** The "lightning-fast" ASGI server that keeps the system online and responsive, handling multiple requests without perceptible latency.

### Database & Data Storage
The system's long-term memory, essential for flexible data storage.

* **MongoDB:** A document-oriented NoSQL database. It was chosen for its scalability and flexibility in managing complex data structures, such as relative registries, biometric vectors for facial recognition, and future conversation logs.

### Computer Vision (AI)
* **Face Recognition (Python Lib):** The biometric recognition engine. This library, an industry standard for precision and simplicity, maps and identifies known faces (friends and relatives) with a high degree of reliability, ensuring recognition even in variable conditions.

<div align="center">

![In Development](https://img.shields.io/badge/Currently%20in-%20early%20development-red?style=flat&logo=github&logoColor=white)

</div>

## Usage
![Working Progress](https://img.shields.io/badge/status-working%20progress-orange?style=flat&logo=github&logoColor=white)

## Contributing
![Working Progress](https://img.shields.io/badge/status-working%20progress-orange?style=flat&logo=github&logoColor=white)

## License
Distributed under the *GPLv3* license. See `LICENSE` for more information.


### Developer Notes (not for public)
To start the local database server: 

```bash
nohup /Users/flaviodemusso/mongodb-macos-aarch64--8.2.2/bin/mongod --dbpath /Users/flaviodemusso/Desktop/DDFR/database --logpath /Users/flaviodemusso/Desktop/DDFR/database/mongodb.log > mongod.out 2>&1 &