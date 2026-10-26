# S.W.A.P. — Smart WhatsApp Application Program

S.W.A.P. is a Python-based web application built with Flask that provides a dashboard for processing contact lists from Excel files and automating WhatsApp Web interactions using Selenium.

## Features

- **Excel Upload:** Import contact numbers and messages from an Excel spreadsheet.
- **WhatsApp Web Integration:** Open WhatsApp Web through Selenium browser automation.
- **Message Processing:** Process contacts from an uploaded spreadsheet.
- **Status Tracking:** Display contact statuses such as pending, completed, invalid, and failed.
- **Start, Stop, and Resume Controls:** Control the processing workflow through the dashboard.
- **Retry Handling:** Retry certain failed operations.
- **Processing History:** Save completed processing records locally.
- **Excel Report Export:** Export processing results as an Excel spreadsheet.
- **Progress Dashboard:** View processing progress and countdown information.

## Technology Stack

- Python
- Flask
- Selenium
- Pandas
- OpenPyXL
- HTML
- CSS
- JavaScript

## Project Structure

```text
SWAP-WhatsApp-Automation/
├── app.py
├── requirements.txt
├── .gitignore
└── templates/
    └── index.html
```

## Prerequisites

- Python installed on your computer
- Google Chrome
- Git
- A WhatsApp account that you are authorized to use

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Wildbuddy/SWAP-WhatsApp-Automation.git
cd SWAP-WhatsApp-Automation
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open the local address displayed in the terminal in your browser.

## Excel Input Format

Prepare an Excel spreadsheet with these column headers:

| Phone | Message |
|---|---|
| 9876543210 | Hello! This is a test message. |

Use dummy data when testing. The application currently normalizes Indian mobile numbers by adding the country code `91` to ten-digit numbers.

## Important Notes

- The application interacts with WhatsApp Web through browser automation.
- WhatsApp Web must be accessible, and the relevant account must be logged in.
- Browser profiles and processing history are stored locally.
- Processing results do not independently verify final message delivery.
- The current implementation uses in-memory contact state, which may be lost when the application process restarts.
- The dashboard's delay input fields are not currently connected to the backend delay settings.

## Responsible Use

Use this project only with appropriate authorization and in accordance with WhatsApp's terms and applicable privacy and messaging laws. Avoid unsolicited bulk messaging and respect recipients' consent and opt-out requests.

## Author

**Rohan Mandal**

Python | Flask | Selenium | Web Development