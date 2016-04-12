NON_ACTIVE_USERS = """
SELECT 
  u.email AS email, o.name as name, o.crm_id as Id, o.vertical as vertical, to_char(u.last_sign_in_at, 'MM/DD/YY') as sign_in, SUM(ap.price) as price
FROM 
  users u INNER JOIN organizations o on u.organization_id=o.id INNER JOIN accounts a on a.organization_id=o.id INNER JOIN account_plans ap on ap.account_id=a.id 
WHERE 
  u.current_sign_in_at >= CURRENT_TIMESTAMP - INTERVAL '60 days' 
  AND u.current_sign_in_at < CURRENT_TIMESTAMP - INTERVAL '30 days' 
  AND a.status = 'ACTIVATED' AND o.demo = false AND o.fraudulent = false AND a.subscription_id IS NOT NULL 
  AND name NOT LIKE '%Hireology%' AND a.churn_date IS NULL AND u.email NOT LIKE '%@hireology.com%'
GROUP BY
 u.email, o.name, o.crm_id, o.vertical, sign_in;
"""

NON_ACTIVE_USERS1 = """
SELECT o.crm_id as Id, o.name as name
    FROM organizations o INNER JOIN accounts a on a.organization_id=o.id,
        (SELECT
          DISTINCT(organization_id)
        FROM
          users
        WHERE
          email NOT LIKE '%@hireology.com' AND
          current_sign_in_at >= CURRENT_TIMESTAMP - INTERVAL '60 days' AND current_sign_in_at < CURRENT_TIMESTAMP - INTERVAL '30 days'
        GROUP BY
          organization_id, email) u 
WHERE 
  o.id=u.organization_id AND o.crm_id IS NOT NULL AND o.demo = false AND o.fraudulent = false
  AND a.subscription_id IS NOT NULL AND a.status = 'ACTIVATED' AND a.churn_date IS NULL AND a.standby_date IS NULL
EXCEPT
SELECT o.crm_id as Id, o.name as name
    FROM organizations o INNER JOIN accounts a on a.organization_id=o.id,
        (SELECT
          DISTINCT(organization_id)
        FROM
          users
        WHERE
          email NOT LIKE '%@hireology.com' AND
          current_sign_in_at >= CURRENT_TIMESTAMP - INTERVAL '30 days' 
        GROUP BY
          organization_id, email) u 
WHERE 
  o.id=u.organization_id AND o.crm_id IS NOT NULL AND o.demo = false AND o.fraudulent = false
  AND a.subscription_id IS NOT NULL AND a.status = 'ACTIVATED' AND a.churn_date IS NULL AND a.standby_date IS NULL;
"""
