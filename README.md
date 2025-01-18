# Synergy Daily Basket

## Overview

This Flask application is designed to fetch daily sales data from the Foodbasket API, generate Excel reports, and send email notifications to designated recipients. The app handles large datasets efficiently by batching API requests and sending vouchers and BIS reports.

## Features

- Fetch sales data in batches from the Foodbasket API for both orders and invoices.
- Filter data by date and payment method.
- Generate Excel reports with detailed sales information.
- Manage email recipients for notifications.
- Designed with error handling for API requests and data processing.

## Technologies Used

- **Flask**: Web framework for Python.
- **OpenPyXL**: Library for working with Excel files.
- **Resend**: API for sending emails.
- **SQLAlchemy**: ORM for database operations.
- **Requests**: HTTP library for making API calls.
- **Docker**: (Planned) for containerizing the application.

## Project Structure

```
project-root/
|-- app/
|   |-- __init__.py
|   |-- models.py
|   |-- routes.py
|-- config/
|   |-- __init__.py
|   |-- config.py
|-- requirements.txt
|-- README.md
|-- run.py
```

### Key Files

- `app/routes.py`: Contains all the application routes for fetching data, generating Excel reports, and managing email recipients.
- `app/models.py`: Defines the database schema for managing email recipients.
- `config/config.py`: Stores configuration variables such as API keys and database URLs.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables: Create a `.env` file in the root directory and add the following variables:

   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   RESEND_API_KEY=<your_resend_api_key>
   DATABASE_URL=<your_database_url>
   FOODBASKET_API_URL=<foodbasket_api_url>
   ```

5. Initialize the database:

   ```bash
   flask db upgrade
   ```

6. Run the application:

   ```bash
   flask run
   ```

## API Endpoints

### Data Retrieval

#### Fetch Orders - Voucher Sales

- **URL**: `/orders-daily-voucher-sales`
- **Method**: `GET`
- **Description**: Fetch daily orders paid with vouchers.

#### Fetch Invoices - Voucher Sales

- **URL**: `/invoices-daily-voucher-sales`
- **Method**: `GET`
- **Description**: Fetch daily invoices paid with vouchers.

#### Fetch Orders - BIS Sales

- **URL**: `/orders-daily-bis-sales`
- **Method**: `GET`
- **Description**: Fetch daily orders paid with BIS.

#### Fetch Invoices - BIS Sales

- **URL**: `/invoices-daily-bis-sales`
- **Method**: `GET`
- **Description**: Fetch daily invoices paid with BIS.

### Email Management

#### Get All Email Recipients

- **URL**: `/email-recipients`
- **Method**: `GET`
- **Description**: Retrieve all registered email recipients.

#### Add a New Email Recipient

- **URL**: `/email-recipients`
- **Method**: `POST`
- **Description**: Add a new recipient to the email list.
- **Payload**:
  ```json
  {
    "email": "example@example.com",
    "name": "John Doe",
    "active": true
  }
  ```

## Error Handling

- Handles connection errors, timeouts, and unexpected server errors when fetching data from the Foodbasket API.
- Validates the presence of expected fields in API responses.
- Ensures no duplicate email entries when adding recipients.

## Planned Enhancements

1. **Dockerization**:

   - Containerize the application for easy deployment.

## Contribution Guidelines

1. Fork the repository and clone it locally.
2. Create a new feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "your descriptive commit message"
   ```
4. Push the branch and create a pull request.
