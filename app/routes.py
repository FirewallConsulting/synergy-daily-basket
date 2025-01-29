from flask import jsonify, request, abort
from app.models import EmailRecipient
from config import Config
import requests
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, Timeout, RequestException
from openpyxl import Workbook
import resend
import os
from app import db
from celery import current_app as celery_app
from celery.exceptions import MaxRetriesExceededError

resend.api_key = Config.RESEND_API_KEY


def register_routes(app):

    def generate_excel_file(entity, data, filename):
        """
        Generate an Excel file from the provided data and save it locally.

        Args:
            entity (str): The type of data ("orders" or "invoices").
            data (list): A list of dictionaries containing the data to be added to the Excel file.
            filename (str): The name of the file to save locally.

        Returns:
            str: The path to the saved Excel file.
        """

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = f"{entity.capitalize()} Data"

        if not data:
            sheet.append(["No data available"])
        else:
            if type(data) == dict:
                sheet.append([data["details"]])
            else:
                if data[0]:
                    # Extract headers from the keys of the first record
                    headers = list(data[0].keys())
                    sheet.append(headers)

                    # Populate rows with data
                    for record in data:
                        row = [record.get(header, "") for header in headers]
                        sheet.append(row)
                else:
                    sheet.append(["No data available"])

        # Save the workbook to a file
        file_path = os.path.join(os.getcwd(), filename)
        workbook.save(file_path)
        return file_path

    def fetch_data_in_batches(entity, batch_size, fields=None, filters=None):
        """
        Fetch data in batches from the Foodbasket API.

        Args:
            entity (str): The type of data to fetch ("orders" or "invoices").
            batch_size (int): Number of records to fetch per batch.
            fields (str, optional): Comma-separated fields to fetch.
            filters (dict, optional): Additional filters (e.g., {"date": "2025-01-15"}).

        Returns:
            list: A list of all fetched data.
            dict: A JSON object with error details if something goes wrong.
        """
        base_url = f"{Config.FOODBASKET_API_URL}/foodbasket/{entity}"
        count_endpoint = f"{base_url}/count"

        filter_query = ""
        # Add filters to the count endpoint
        if filters:
            filter_query += "&".join(f"{key}={value}" for key, value in filters.items())
            count_endpoint += f"?{filter_query}"

        # Get the total count
        try:
            count_response = requests.get(count_endpoint)
            count_response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        except ConnectionError:
            return {
                "error": f"Failed to connect to the server while fetching {entity} count",
                "details": "The server might be unavailable or the connection was refused.",
            }
        except Timeout:
            return {
                "error": f"Request timed out while fetching {entity} count",
                "details": "The server did not respond in time. Please try again later.",
            }
        except RequestException as e:
            return {
                "error": f"An error occurred while fetching {entity} count",
                "details": str(e),
            }

        # Check for missing 'data' in the count response
        count_data = count_response.json()
        if "data" not in count_data:
            return {
                "error": f"Response for {entity} count is missing 'data'",
                "response": count_data,
            }
        total_records = count_data.get("data", 0)

        print(f"{total_records} {entity} records for yesterday")
	# Fetch data in batches
        all_data = []
        for offset in range(0, total_records, batch_size):
            data_endpoint = f"{base_url}?maxAllowed={batch_size}&offset={offset}"
            if fields:
                data_endpoint += f"&{filter_query}&fields={fields}"
            else:
                data_endpoint += f"&{filter_query}"

            try:
                response = requests.get(data_endpoint)
                response.raise_for_status()
            except ConnectionError:
                return {
                    "error": f"Failed to connect to the server while fetching {entity} data",
                    "details": "The server might be unavailable or the connection was refused.",
                }
            except Timeout:
                return {
                    "error": f"Request timed out while fetching {entity} data",
                    "details": "The server did not respond in time. Please try again later.",
                }
            except RequestException as e:
                return {
                    "error": f"An error occurred while fetching {entity} data",
                    "details": str(e),
                }

            # Check for missing 'data' in the data response
            response_json = response.json()
            if "data" not in response_json:
                return {
                    "error": f"Response for {entity} data is missing 'data'",
                    "response": response_json,
                }
            data_batch = response_json["data"].get(entity.capitalize(), [])
            all_data.extend(data_batch)

        return all_data

    @app.route("/orders-daily-voucher-sales", methods=["GET"])
    def get_orders_daily_voucher_sales():
        current_date = datetime.now().strftime("%Y-%m-%d")
        batch_size = 50
        fields = ",".join(
            [
                "DocDate",
                "DocNum",
                "DocEntry",
                "CardCode",
                "DocTotal",
                "U_voucher_id",
                "U_total_voucher",
                "U_total_cash",
                "U_total_debit",
                "U_receipt_id",
            ]
        )
        filters = {
            "startDate": current_date,
            "endDate": current_date,
            "paymentMethods": "voucher",
        }
        all_orders = fetch_data_in_batches("orders", batch_size, fields, filters)
        return jsonify(all_orders)

    @app.route("/invoices-daily-voucher-sales", methods=["GET"])
    def get_invoices_daily_voucher_sales():
        current_date = datetime.now().strftime("%Y-%m-%d")
        batch_size = 50
        fields = ",".join(
            [
                "DocDate",
                "DocNum",
                "DocEntry",
                "CardCode",
                "DocTotal",
                "U_voucher_id",
                "U_total_voucher",
                "U_total_cash",
                "U_total_debit",
                "U_receipt_id",
            ]
        )
        filters = {
            "startDate": current_date,
            "endDate": current_date,
            "paymentMethods": "voucher",
        }
        all_invoices = fetch_data_in_batches("invoices", batch_size, fields, filters)
        return jsonify(all_invoices)

    @app.route("/orders-daily-bis-sales", methods=["GET"])
    def get_orders_daily_bis_sales():
        current_date = datetime.now().strftime("%Y-%m-%d")
        batch_size = 50
        fields = ",".join(
            [
                "DocDate",
                "DocNum",
                "DocEntry",
                "CardCode",
                "DocTotal",
                "U_num_at_card",
                "U_total_bis",
                "U_total_cash",
                "U_total_debit",
                "U_receipt_id",
            ]
        )
        filters = {
            "startDate": current_date,
            "endDate": current_date,
            "paymentMethods": "bis",
        }
        all_orders = fetch_data_in_batches("orders", batch_size, fields, filters)
        return jsonify(all_orders)

    @app.route("/invoices-daily-bis-sales", methods=["GET"])
    def get_invoices_daily_bis_sales():
        current_date = datetime.now().strftime("%Y-%m-%d")
        batch_size = 50
        fields = ",".join(
            [
                "DocDate",
                "DocNum",
                "DocEntry",
                "CardCode",
                "DocTotal",
                "U_num_at_card",
                "U_total_bis",
                "U_total_cash",
                "U_total_debit",
                "U_receipt_id",
            ]
        )
        filters = {
            "startDate": current_date,
            "endDate": current_date,
            "paymentMethods": "bis",
        }
        all_invoices = fetch_data_in_batches("invoices", batch_size, fields, filters)
        return jsonify(all_invoices)

    @app.route("/email-recipients", methods=["GET"])
    def get_email_recipients():
        recipients = EmailRecipient.query.all()
        return jsonify(
            [
                {
                    "id": recipient.id,
                    "email": recipient.email,
                    "name": recipient.name,
                    "active": recipient.active,
                }
                for recipient in recipients
            ]
        )

    @app.route("/email-recipients", methods=["POST"])
    def add_email_recipient():
        data = request.json
        if not data or "email" not in data:
            abort(400, description="Missing 'email' field in request data.")

        email = data["email"]
        name = data.get("name")
        active = data.get("active", True)

        # Check for duplicate email
        if EmailRecipient.query.filter_by(email=email).first():
            abort(400, description="Email already exists.")

        new_recipient = EmailRecipient(email=email, name=name, active=active)
        db.session.add(new_recipient)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Recipient added successfully.",
                    "recipient": {
                        "id": new_recipient.id,
                        "email": new_recipient.email,
                        "name": new_recipient.name,
                        "active": new_recipient.active,
                    },
                }
            ),
            201,
        )

    @app.route("/email-recipients/<int:recipient_id>", methods=["PUT"])
    def update_email_recipient(recipient_id):
        recipient = EmailRecipient.query.get_or_404(recipient_id)
        data = request.json

        recipient.email = data.get("email", recipient.email)
        recipient.name = data.get("name", recipient.name)
        recipient.active = data.get("active", recipient.active)

        # Validate email if updated
        if (
            "email" in data
            and EmailRecipient.query.filter_by(email=recipient.email).first()
        ):
            abort(400, description="Email already exists.")

        db.session.commit()

        return jsonify(
            {
                "message": "Recipient updated successfully.",
                "recipient": {
                    "id": recipient.id,
                    "email": recipient.email,
                    "name": recipient.name,
                    "active": recipient.active,
                },
            }
        )

    @app.route("/email-recipients/<int:recipient_id>", methods=["DELETE"])
    def delete_email_recipient(recipient_id):
        recipient = EmailRecipient.query.get_or_404(recipient_id)

        db.session.delete(recipient)
        db.session.commit()

        return jsonify({"message": "Recipient deleted successfully."})

    @celery_app.task(bind=True, max_retries=2, default_retry_delay=60 * 30)
    @app.route("/send-email", methods=["POST"])
    def send_email(self):
        try:
            current_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            batch_size = 50
            entity = "orders"

            order_fields = ",".join(
                [
                    "DocDate",
                    "DocTime",
                    "CreationDate",
                    "DocNum",
                    "DocEntry",
                    "CardCode",
                    "DocTotal",
                    "U_total_cash",
                    "U_total_debit",
                    "U_receipt_id",
                ]
            )

            # Fetch orders (BIS data)
            bis_orders = fetch_data_in_batches(
                entity,
                batch_size,
                f"{order_fields},U_num_at_card,U_total_bis",
                {
                    "startDate": current_date,
                    "endDate": current_date,
                    "paymentMethods": "bis",
                },
            )

            # Fetch orders (Voucher data)
            voucher_orders = fetch_data_in_batches(
                entity,
                batch_size,
                f"{order_fields},U_voucher_id,U_total_voucher",
                {
                    "startDate": current_date,
                    "endDate": current_date,
                    "paymentMethods": "voucher",
                },
            )

            orders_fetch_failed = (
                bool(bis_orders["error"]) or bool(voucher_orders["error"])
                if type(bis_orders) == dict or type(voucher_orders) == dict
                else False
            )

            if orders_fetch_failed:
                raise Exception(bis_orders["error"])

            # Generate Excel files for bis data and vouchers data
            bis_orders_excel_filename = f"BIS_{entity}_{current_date}.xlsx"
            voucher_orders_excel_filename = f"Voucher_{entity}_{current_date}.xlsx"

            bis_orders_excel_path = generate_excel_file(
                entity, bis_orders, bis_orders_excel_filename
            )
            voucher_orders_excel_path = generate_excel_file(
                "vouchers", voucher_orders, voucher_orders_excel_filename
            )

            # Read files and prepare attachments
            with open(bis_orders_excel_path, "rb") as f:
                bis_orders_excel_content = list(f.read())
            with open(voucher_orders_excel_path, "rb") as f:
                voucher_orders_excel_content = list(f.read())

            orders_attachment = {
                "content": bis_orders_excel_content,
                "filename": bis_orders_excel_filename,
            }
            vouchers_attachment = {
                "content": voucher_orders_excel_content,
                "filename": voucher_orders_excel_filename,
            }

            # Fetch email recipients for the CC field
            recipients = db.session.execute(
                db.select(EmailRecipient.email).filter_by(active=True)
            ).all()

            cc_recipients = [row[0] for row in recipients]

            # Email Body (HTML and Plain Text)
            total_orders = 0 if orders_fetch_failed else len(bis_orders)
            total_vouchers = 0 if orders_fetch_failed else len(voucher_orders)

            html_body = f"""
            <p>Goodmorning,</p>
            <p>Please find the attached reports for yesterday.</p>
            <p><strong>Summary:</strong></p>
            <ul>
                <li>BIS Data Records: {total_orders}</li>
                <li>Voucher Data Records: {total_vouchers}</li>
                <li>Fetch Status: {'FAILED' if orders_fetch_failed else 'SUCCESS'}</li>
            </ul>
            <p>Kind regards,<br>SynergyDailyBasket</p>
            """

            plain_text_body = (
                "Goodmorning,\n\n"
                "Please find the attached reports for yesterday.\n\n"
                "Summary:\n"
                f"- BIS Data Records: {total_orders}\n"
                f"- Voucher Data Records: {total_vouchers}\n"
                f"- Fetch Status: {'FAILED' if orders_fetch_failed else 'SUCCESS'}\n\n"
                "Kind regards,\nSynergyDailyBasket"
            )

            params: resend.Emails.SendParams = {
                "from": f"SynergyDailyBasket <{Config.FROM_EMAIL}>",
                "to": [Config.TO_EMAIL],
                "cc": cc_recipients,
                "subject": f"BIS and Voucher Reports - {current_date}",
                "html": html_body,
                "text": plain_text_body,
                "attachments": [orders_attachment, vouchers_attachment],
            }

            # Send the email
            r = resend.Emails.send(params)

            # Delete the files after sending the email
            os.remove(bis_orders_excel_path)
            os.remove(voucher_orders_excel_path)

            return jsonify(r)
        except Exception as exc:
            try:
                self.retry(exc=exc)
            except MaxRetriesExceededError:
                print("Max retries exceeded. Send email task failed permanently.")

    @app.route("/", methods=["GET"])
    def index():
        return "<h1>Synergy Daily Basket</h1>"
