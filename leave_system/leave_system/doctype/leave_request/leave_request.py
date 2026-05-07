# Copyright (c) 2026, paul and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.utils import today, date_diff, getdate


class LeaveRequest(Document):

    def before_insert(self):
        self.applied_on = today()
        self.status = "Draft"

    def validate(self):
        self.validate_dates()
        self.calculate_days()
        self.set_employee_details()
        self.sync_status()

    def sync_status(self):
        if self.workflow_state and self.status != self.workflow_state:
            self.status = self.workflow_state

    def validate_dates(self):
        if self.from_date and self.to_date:
            # Convert both to date objects for comparison
            from_date = getdate(self.from_date)
            to_date = getdate(self.to_date)
            today_date = getdate(today())

            if from_date > to_date:
                frappe.throw("From Date cannot be after To Date")

            if from_date < today_date:
                frappe.throw("From Date cannot be in the past")

    def calculate_days(self):
        if self.from_date and self.to_date:
            self.number_of_days = date_diff(
                self.to_date,
                self.from_date
            ) + 1

    def set_employee_details(self):
        if not self.employee_name:
            user = frappe.get_doc("User", frappe.session.user)
            self.employee_name = user.full_name

    def on_submit(self):
        self.status = "Pending"
        self.db_set("status", "Pending")
        self.notify_manager()

    def on_cancel(self):
        self.status = "Cancelled"
        self.db_set("status", "Cancelled")

    def notify_manager(self):
        if self.manager:
            manager_email = frappe.db.get_value(
                "User", self.manager, "email"
            )
            manager_name = frappe.db.get_value(
                "User", self.manager, "full_name"
            ) or "Manager"

            if manager_email:
                frappe.sendmail(
                    recipients=[manager_email],
                    subject=f"🔔 Leave Request Pending Approval — {self.name}",
                    message=f"""
<!DOCTYPE html>
<html>
<body style="margin:0; padding:0; background:#f1f5f9; font-family: Arial, sans-serif;">

  <div style="max-width:600px; margin:32px auto; background:white; border-radius:12px; overflow:hidden; border:1px solid #e2e8f0;">

    <!-- Header -->
    <div style="background:#2563eb; padding:28px 32px;">
      <h2 style="margin:0; color:white; font-size:20px; font-weight:600;">
        Leave Request Pending Approval
      </h2>
      <p style="margin:6px 0 0; color:#bfdbfe; font-size:13px;">
        Request ID: {self.name}
      </p>
    </div>

    <!-- Greeting -->
    <div style="padding:28px 32px 0;">
      <p style="margin:0; color:#1e293b; font-size:15px;">
        Dear <strong>{manager_name}</strong>,
      </p>
      <p style="margin:12px 0 0; color:#64748b; font-size:14px; line-height:1.6;">
        A new leave request has been submitted and requires your approval. 
        Please review the details below and take action at your earliest convenience.
      </p>
    </div>

    <!-- Details Card -->
    <div style="padding:24px 32px;">
      <div style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0; overflow:hidden;">

        <div style="background:#1e293b; padding:12px 16px;">
          <p style="margin:0; color:white; font-size:13px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase;">
            Request Details
          </p>
        </div>

        <table style="width:100%; border-collapse:collapse;">
          <tr>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px; width:40%;">
              Employee
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; font-weight:500;">
              {self.employee_name}
            </td>
          </tr>
          <tr style="background:#fafafa;">
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px;">
              Leave Type
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; font-weight:500;">
              {self.leave_type}
            </td>
          </tr>
          <tr>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px;">
              From Date
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; font-weight:500;">
              {self.from_date}
            </td>
          </tr>
          <tr style="background:#fafafa;">
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px;">
              To Date
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; font-weight:500;">
              {self.to_date}
            </td>
          </tr>
          <tr>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px;">
              Number of Days
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; font-size:13px;">
              <span style="background:#dbeafe; color:#1d4ed8; padding:3px 10px; border-radius:12px; font-weight:600; font-size:12px;">
                {self.number_of_days} day{"s" if self.number_of_days > 1 else ""}
              </span>
            </td>
          </tr>
          <tr style="background:#fafafa;">
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px;">
              Applied On
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; font-weight:500;">
              {self.applied_on}
            </td>
          </tr>
          <tr>
            <td style="padding:12px 16px; color:#64748b; font-size:13px; vertical-align:top;">
              Reason
            </td>
            <td style="padding:12px 16px; color:#1e293b; font-size:13px; font-weight:500; line-height:1.5;">
              {self.reason}
            </td>
          </tr>
        </table>

      </div>
    </div>

    <!-- Action Button -->
    <div style="padding:0 32px 28px; text-align:center;">
      <a href="/app/leave-request/{self.name}"
         style="display:inline-block; background:#2563eb; color:white; padding:12px 32px; border-radius:8px; text-decoration:none; font-size:14px; font-weight:600;">
        Review Request
      </a>
      <p style="margin:12px 0 0; color:#94a3b8; font-size:12px;">
        Click the button above to approve or reject this request
      </p>
    </div>

    <!-- Status Banner -->
    <div style="margin:0 32px 28px; background:#fef9c3; border:1px solid #fde047; border-radius:8px; padding:12px 16px; display:flex; align-items:center;">
      <span style="color:#854d0e; font-size:13px;">
        ⏳ &nbsp; This request is awaiting your approval.
        Please respond as soon as possible.
      </span>
    </div>

    <!-- Footer -->
    <div style="background:#f8fafc; padding:16px 32px; border-top:1px solid #e2e8f0; text-align:center;">
      <p style="margin:0; color:#94a3b8; font-size:12px;">
        This is an automated notification from the Leave Management System.
        Please do not reply to this email.
      </p>
    </div>

  </div>

</body>
</html>
                """
            )