@frappe.whitelist()
def approve_leave(name):
    if not frappe.user.has_role('Leave Manager'):
        frappe.throw("Not authorised to approve leave requests.")

    doc = frappe.get_doc("Leave Request", name)

    if doc.status != "Pending":
        frappe.throw("Only Pending requests can be approved.")

    doc.status = "Approved"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    # Notify employee
    notify_employee(doc, "Approved")

    return {"success": True}


@frappe.whitelist()
def reject_leave(name, rejection_reason):
    if not frappe.user.has_role('Leave Manager'):
        frappe.throw("Not authorised to reject leave requests.")

    doc = frappe.get_doc("Leave Request", name)

    if doc.status != "Pending":
        frappe.throw("Only Pending requests can be rejected.")

    doc.status = "Rejected"
    doc.rejection_reason = rejection_reason
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    # Notify employee
    notify_employee(doc, "Rejected")

    return {"success": True}


@frappe.whitelist()
def get_leave_request(name):
    doc = frappe.get_doc("Leave Request", name)
    return doc.as_dict()


@frappe.whitelist()
def get_my_leaves():
    user = frappe.session.user
    leaves = frappe.get_list(
        "Leave Request",
        filters={"owner": user},
        fields=[
            "name",
            "leave_type",
            "from_date",
            "to_date",
            "number_of_days",
            "status",
            "reason"
        ],
        order_by="applied_on desc",
        ignore_permissions=True
    )
    return leaves


def notify_employee(doc, action):
    employee_email = frappe.db.get_value(
        "User", doc.owner, "email"
    )

    if not employee_email:
        return

    is_approved = action == "Approved"
    header_color = "#16a34a" if is_approved else "#dc2626"
    status_bg = "#dcfce7" if is_approved else "#fee2e2"
    status_color = "#15803d" if is_approved else "#dc2626"
    icon = "✅" if is_approved else "❌"
    message = (
        "Your leave request has been approved. Please plan accordingly."
        if is_approved else
        "We regret to inform you that your leave request has been rejected. Please see the reason below."
    )

    rejection_row = ""
    if not is_approved and doc.rejection_reason:
        rejection_row = f"""
          <tr>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px; width:40%; vertical-align:top;">
              Rejection Reason
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#dc2626; font-size:13px; font-weight:500; line-height:1.5;">
              {doc.rejection_reason}
            </td>
          </tr>
        """

    frappe.sendmail(
        recipients=[employee_email],
        subject=f"{icon} Leave Request {action} — {doc.name}",
        message=f"""
<!DOCTYPE html>
<html>
<body style="margin:0; padding:0; background:#f1f5f9; font-family:Arial, sans-serif;">

  <div style="max-width:600px; margin:32px auto; background:white; border-radius:12px; overflow:hidden; border:1px solid #e2e8f0;">

    <!-- Header -->
    <div style="background:{header_color}; padding:28px 32px;">
      <h2 style="margin:0; color:white; font-size:20px; font-weight:600;">
        Leave Request {action}
      </h2>
      <p style="margin:6px 0 0; color:rgba(255,255,255,0.8); font-size:13px;">
        Request ID: {doc.name}
      </p>
    </div>

    <!-- Greeting -->
    <div style="padding:28px 32px 0;">
      <p style="margin:0; color:#1e293b; font-size:15px;">
        Dear <strong>{doc.employee_name}</strong>,
      </p>
      <p style="margin:12px 0 0; color:#64748b; font-size:14px; line-height:1.6;">
        {message}
      </p>
    </div>

    <!-- Status Badge -->
    <div style="padding:20px 32px 0;">
      <span style="background:{status_bg}; color:{status_color}; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600;">
        {icon} {action}
      </span>
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
              Leave Type
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; font-weight:500;">
              {doc.leave_type}
            </td>
          </tr>
          <tr style="background:#fafafa;">
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px;">
              From Date
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; font-weight:500;">
              {doc.from_date}
            </td>
          </tr>
          <tr>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px;">
              To Date
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; font-weight:500;">
              {doc.to_date}
            </td>
          </tr>
          <tr style="background:#fafafa;">
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px;">
              Number of Days
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; font-size:13px;">
              <span style="background:#dbeafe; color:#1d4ed8; padding:3px 10px; border-radius:12px; font-weight:600; font-size:12px;">
                {doc.number_of_days} day{"s" if doc.number_of_days > 1 else ""}
              </span>
            </td>
          </tr>
          <tr>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#64748b; font-size:13px; vertical-align:top;">
              Reason
            </td>
            <td style="padding:12px 16px; border-bottom:1px solid #e2e8f0; color:#1e293b; font-size:13px; line-height:1.5;">
              {doc.reason}
            </td>
          </tr>
          {rejection_row}
        </table>

      </div>
    </div>

    <!-- Action Button -->
    <div style="padding:0 32px 28px; text-align:center;">
      <a href="/app/leave-request/{doc.name}"
         style="display:inline-block; background:#1e293b; color:white; padding:12px 32px; border-radius:8px; text-decoration:none; font-size:14px; font-weight:600;">
        View Request
      </a>
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