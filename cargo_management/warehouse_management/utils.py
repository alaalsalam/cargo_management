import frappe

@frappe.whitelist(methods='GET')
def get_packages_by_agent_and_transportation(agent: str, transportation: str = None):
    """ Get all packages connected to a specific agent, optionally filtered by transportation type. """

    VIA_SQL = "CONCAT('Via: ', IF(p.transportation = 'Air', 'Aereo', 'Maritimo'))"

    # بناء الشرط الديناميكي لـ transportation
    transportation_condition = ""
    if transportation:
        transportation_condition = "AND p.transportation = %(transportation)s"

    packages = frappe.db.sql(f"""
        SELECT
            p.*,  -- جلب جميع الحقول من جدول Parcel
            CONCAT(
                IF(COUNT(pc.tracking_number) > 0, CONCAT({VIA_SQL}, '\n\n'), ''),
                GROUP_CONCAT(DISTINCT
                    pc.description,
                    IF(pc.tracking_number > '', CONCAT('\nNumero de Rastreo: ', pc.tracking_number), ''),
                    IF(pc.amount > 0, CONCAT('\nValor Declarado: $', FORMAT(pc.amount, 2)), ''),
                    IF(pc.item_code > '', CONCAT('\nCodigo: ', pc.item_code), ''),
                    IF(pc.import_rate > 0, CONCAT('\nTarifa: $', FORMAT(pc.import_rate, 2)), '')
                    ORDER BY pc.idx SEPARATOR '\n\n'
                ),
                IF(COUNT(pc.tracking_number) = 0, CONCAT('\n\n', {VIA_SQL}), ''),
                IF(p.name != p.tracking_number, CONCAT(IF(COUNT(pc.tracking_number) > 0, '\n', ''), '\nNumero de Rastreo FINAL: ', p.tracking_number), '')
            ) AS customer_description
        FROM tabParcel p
            LEFT JOIN `tabParcel Content` pc ON pc.parent = p.name
        WHERE p.agent = %(agent)s {transportation_condition}  -- تطبيق الشرط إذا كان موجودًا
        GROUP BY p.name
        ORDER BY p.customer_name
    """, {
        'agent': agent,
        'transportation': transportation
    }, as_dict=True)

    return {
        'packages': packages
    }
