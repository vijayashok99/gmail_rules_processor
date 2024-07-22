# Gmail Rules Processor

This Python script integrates with the Gmail API to fetch emails and process them based on user-defined rules.

## Features

- Authenticate with Gmail API using OAuth
- Fetch emails from your inbox
- Store emails in a relational database
- Process emails based on customizable rules
- Perform actions like marking emails as read/unread and moving them to different labels

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/gmail-rules-processor.git
   cd gmail-rules-processor
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up OAuth 2.0 credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API for your project
   - Create OAuth 2.0 credentials (Desktop app) and download the `credentials.json` file
   - Place the `credentials.json` file in the project root directory

## Configuration

2. Update `config/rules.json` file with your desired rules. Supported actions are Read, Unread, move to INBOX, SPAM & TRASH

## Usage

Run the main script:

```
python -m src.main
```

https://github.com/user-attachments/assets/81b93e04-e8b1-48db-9297-f56db66d2696


The script will authenticate with the Gmail API, fetch emails, store them in the database, and process them according to the defined rules.

## Running Tests

To run the tests, use the following command:

```
pytest tests/
```

