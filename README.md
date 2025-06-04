# Experimental LabStore

## Description
Experimental LabStore is a project that intends to create an efficient and user-friendly laboratory inventory management system. It features tools for tracking inventory items and their usage, automating restocking and reorder routines, and providing an intuitive user interface for lab personnel. Its main goal is to facilitate lab operations and significantly reduce time spent on inventory management, allowing researchers to focus more on their research work.

## Prerequisites
- Python 3.10.11
- pip package manager
- A modern web browser

## Installation
To install Experimental LabStore, follow these steps:
1. Clone the repository: `git clone https://github.com/your_username/Experimental-LabStore.git`
2. Navigate to the project directory: `cd Experimental-LabStore`
3. Install necessary packages: `pip install -r requirements.txt`

## Usage
1. Start the server: `python -m streamlit run .\lab.py`
2. Open your web browser and navigate to `http://localhost:5000` 
3. You can now interact with the system, add inventory items, track usage, and automate restocking routines. For more details, please refer to the user manual included in the project documentation.


### Para solucionar error "Error on ghost text request: FetchError: The pending stream has been canceled (caused by: self signed certificate in certificate chain)" en Github Copilot: 
$env:NODE_TLS_REJECT_UNAUTHORIZED="0"
