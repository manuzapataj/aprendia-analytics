WITH subscription_totals AS (
    SELECT plan_id, COUNT(*) AS subscription_count
    FROM subscriptions
    GROUP BY plan_id
), payment_totals AS (
    SELECT
        s.plan_id,
        COUNT(*) AS payment_attempts,
        SUM(CASE WHEN p.status = 'completed' THEN 1 ELSE 0 END) AS completed_payments,
        SUM(CASE WHEN p.status = 'completed' THEN p.amount_cents ELSE 0 END) AS collected_cents
    FROM subscriptions AS s
    JOIN payments AS p ON p.subscription_id = s.subscription_id
    GROUP BY s.plan_id
)
SELECT
    p.plan_name,
    COALESCE(s.subscription_count, 0) AS subscriptions,
    COALESCE(t.payment_attempts, 0) AS payment_attempts,
    COALESCE(t.completed_payments, 0) AS completed_payments,
    COALESCE(t.collected_cents, 0) AS collected_cents,
    ROUND(100.0 * t.completed_payments / NULLIF(t.payment_attempts, 0), 2) AS completed_share_pct
FROM plans AS p
LEFT JOIN subscription_totals AS s ON s.plan_id = p.plan_id
LEFT JOIN payment_totals AS t ON t.plan_id = p.plan_id
ORDER BY collected_cents DESC, p.plan_id;
