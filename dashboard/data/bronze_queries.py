BRONZE_QUERIES = {
    "daily_revenue_summary": """
        SELECT
            CAST(v.visit_date AS DATE)                                 AS revenue_date,
            v.hospital_id,
            h.hospital_name,
            CONCAT(u.first_name, ' ', u.last_name)                    AS doctor_name,
            ROUND(SUM(i.invoice_amount), 2)                           AS total_revenue,
            ROUND(SUM(i.tax_amount), 2)                               AS total_tax,
            ROUND(SUM(i.discount_amount), 2)                          AS total_discount,
            COUNT(DISTINCT i.invoice_id)                              AS invoice_count,
            COUNT(DISTINCT v.visit_id)                                AS visit_count,
            ROUND(SUM(i.invoice_amount) - SUM(i.discount_amount), 2) AS net_revenue
        FROM      {catalog}.{schema}.bronze_visit   v
        LEFT JOIN {catalog}.{schema}.bronze_invoice  i ON v.visit_id    = i.visit_id
        LEFT JOIN {catalog}.{schema}.bronze_hospital h ON v.hospital_id  = h.hospital_id
        LEFT JOIN {catalog}.{schema}.bronze_user     u ON v.doctor_id    = u.user_id
        WHERE i.invoice_amount > 0
        GROUP BY 1, 2, 3, 4
    """,

    "top_treatment_summary": """
        SELECT
            appointment_type                              AS treatment_name,
            appointment_type                              AS treatment_category,
            COUNT(*)                                      AS usage_count,
            COUNT(DISTINCT pet_id)                        AS unique_pets_treated,
            FIRST(diagnosis_code)                         AS most_used_medication,
            ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC)   AS usage_rank,
            CURRENT_DATE()                                AS snapshot_date
        FROM {catalog}.{schema}.bronze_visit
        WHERE appointment_type IS NOT NULL
        GROUP BY appointment_type
        ORDER BY usage_count DESC
    """,

    "repeat_visit_summary": """
        SELECT
            v.pet_id,
            p.pet_name,
            CONCAT(u.first_name, ' ', u.last_name)       AS owner_name,
            COUNT(DISTINCT v.visit_id)                    AS total_visit_count,
            MIN(v.visit_date)                             AS first_visit_date,
            MAX(v.visit_date)                             AS last_visit_date,
            CASE
                WHEN COUNT(DISTINCT v.visit_id) > 1 THEN
                    ROUND(
                        DATEDIFF(MAX(v.visit_date), MIN(v.visit_date))
                        / (COUNT(DISTINCT v.visit_id) - 1),
                    2)
                ELSE 0
            END                                           AS avg_days_between_visits,
            COUNT(DISTINCT v.visit_id) > 1                AS is_repeat_visitor
        FROM      {catalog}.{schema}.bronze_visit v
        LEFT JOIN {catalog}.{schema}.bronze_pet   p ON v.pet_id  = p.pet_id
        LEFT JOIN {catalog}.{schema}.bronze_user  u ON p.user_id = u.user_id
        WHERE v.pet_id IS NOT NULL
        GROUP BY v.pet_id, p.pet_name, u.first_name, u.last_name
    """,

    "active_pet_summary": """
        SELECT
            v.pet_id,
            p.pet_name,
            p.species,
            CONCAT(u.first_name, ' ', u.last_name)               AS owner_name,
            h.hospital_name,
            MAX(v.visit_date)                                     AS last_visit_date,
            DATEDIFF(CURRENT_DATE(), MAX(v.visit_date))          AS days_since_last_visit,
            DATEDIFF(CURRENT_DATE(), MAX(v.visit_date)) <= 90    AS is_active,
            90                                                    AS active_window_days
        FROM      {catalog}.{schema}.bronze_visit   v
        LEFT JOIN {catalog}.{schema}.bronze_pet      p ON v.pet_id      = p.pet_id
        LEFT JOIN {catalog}.{schema}.bronze_user     u ON p.user_id     = u.user_id
        LEFT JOIN {catalog}.{schema}.bronze_hospital h ON v.hospital_id = h.hospital_id
        WHERE v.pet_id IS NOT NULL
        GROUP BY v.pet_id, p.pet_name, p.species, u.first_name, u.last_name, h.hospital_name
    """,
}
