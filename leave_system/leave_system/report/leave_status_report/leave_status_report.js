frappe.query_reports["Leave Status Report"] = {
  filters: [
      {
          fieldname: "from_date",
          label: __("From Date"),
          fieldtype: "Date",
          default: frappe.datetime.month_start()
      },
      {
          fieldname: "to_date",
          label: __("To Date"),
          fieldtype: "Date",
          default: frappe.datetime.month_end()
      },
      {
          fieldname: "status",
          label: __("Status"),
          fieldtype: "Select",
          options: "\nDraft\nPending\nApproved\nRejected\nCancelled"
      },
      {
          fieldname: "leave_type",
          label: __("Leave Type"),
          fieldtype: "Select",
          options: "\nAnnual Leave\nSick Leave\nCasual Leave\nMaternity Leave\nPaternity Leave\nUnpaid Leave"
      },
      {
          fieldname: "employee_name",
          label: __("Employee Name"),
          fieldtype: "Data"
      }
  ]
}