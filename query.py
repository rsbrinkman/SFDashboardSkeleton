NON_ACTIVE_USERS = """
SELECT 
  u.email AS email, o.name as name, o.crm_id as Id, o.vertical as vertical, to_char(u.last_sign_in_at, 'MM/DD/YY') as sign_in, SUM(ap.price) as price
FROM 
  users u INNER JOIN organizations o on u.organization_id=o.id INNER JOIN accounts a on a.organization_id=o.id INNER JOIN account_plans ap on ap.account_id=a.id 
WHERE 
  u.last_sign_in_at >= CURRENT_TIMESTAMP - INTERVAL '60 days' AND u.current_sign_in_at >= CURRENT_TIMESTAMP - INTERVAL '60 days' 
  AND u.last_sign_in_at < CURRENT_TIMESTAMP - INTERVAL '30 days' AND u.current_sign_in_at < CURRENT_TIMESTAMP - INTERVAL '30 days' 
  AND a.status = 'ACTIVATED' AND o.demo = false AND o.fraudulent = false AND a.subscription_id IS NOT NULL 
  AND name NOT LIKE '%Hireology%' AND a.churn_date IS NULL AND u.email NOT LIKE '%@hireology.com%'
GROUP BY
 u.email, o.name, o.crm_id, o.vertical, sign_in;
"""
