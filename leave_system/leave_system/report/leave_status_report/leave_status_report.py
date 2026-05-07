import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Request ID",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Leave Request",
            "width": 140
        },
        {
            "label": "Employee",
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Leave Type",
            "fieldname": "leave_type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "From Date",
            "fieldname": "from_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "To Date",
            "fieldname": "to_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Days",
            "fieldname": "number_of_days",
            "fieldtype": "Int",
            "width": 80
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Applied On",
            "fieldname": "applied_on",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Reason",
            "fieldname": "reason",
            "fieldtype": "Data",
            "width": 200
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    return frappe.db.sql("""
        SELECT
            name,
            employee_name,
            leave_type,
            from_date,
            to_date,
            number_of_days,
            status,
            applied_on,
            reason
        FROM
            `tabLeave Request`
        WHERE
            1=1 {conditions}
        ORDER BY
            applied_on DESC
    """.format(conditions=conditions), filters, as_dict=True)


def get_conditions(filters):
    conditions = ""

    if not filters:
        return conditions

    if filters.get("from_date"):
        conditions += " AND from_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND to_date <= %(to_date)s"

    if filters.get("status"):
        conditions += " AND status = %(status)s"

    if filters.get("leave_type"):
        conditions += " AND leave_type = %(leave_type)s"

    if filters.get("employee_name"):
        conditions += " AND employee_name LIKE %(employee_name)s"

    return conditions