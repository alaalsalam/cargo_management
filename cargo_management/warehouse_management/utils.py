import frappe

@frappe.whitelist(methods='GET')
def get_packages_by_agent_and_transportation(agent: str, transportation: str = None):
    """ Get all packages connected to a specific agent, optionally filtered by transportation type, and with status 'Awaiting Receipt'. """

    VIA_SQL = "CONCAT('Via: ', IF(p.transportation = 'Air', 'Aereo', 'Maritimo'))"

    # Build the dynamic transportation condition
    transportation_condition = ""
    if transportation:
        transportation_condition = "AND p.transportation = %(transportation)s"

    # Fetch only parcels with status 'Awaiting Departure'
    packages = frappe.db.sql(f"""
        SELECT
            p.*,  # Fetch all fields from the Parcel table
            CONCAT(
                IF(COUNT(pc.tracking_number) > 0, CONCAT({VIA_SQL}, '\n\n'), ''),
                GROUP_CONCAT(DISTINCT
                    pc.description,
                    IF(pc.tracking_number > '', CONCAT('\nTracking Number: ', pc.tracking_number), ''),
                    IF(pc.amount > 0, CONCAT('\nDeclared Value: $', FORMAT(pc.amount, 2)), ''),
                    IF(pc.item_code > '', CONCAT('\nCode: ', pc.item_code), ''),
                    IF(pc.import_rate > 0, CONCAT('\nRate: $', FORMAT(pc.import_rate, 2)), '')
                    ORDER BY pc.idx SEPARATOR '\n\n'
                ),
                IF(COUNT(pc.tracking_number) = 0, CONCAT('\n\n', {VIA_SQL}), ''),
                IF(p.name != p.tracking_number, CONCAT(IF(COUNT(pc.tracking_number) > 0, '\n', ''), '\nFinal Tracking Number: ', p.tracking_number), '')
            ) AS customer_description
        FROM `tabParcel` p
            LEFT JOIN `tabParcel Content` pc ON pc.parent = p.name
        WHERE p.agent = %(agent)s
            AND p.status = 'Awaiting Receipt' 
            {transportation_condition}  # Apply the condition if it exists
        GROUP BY p.name
        ORDER BY p.tracking_number
    """, {
        'agent': agent,
        'transportation': transportation
    }, as_dict=True)

    return {
        'packages': packages
    }
