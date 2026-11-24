CREATE TABLE plans (
    plan_id INTEGER PRIMARY KEY,
    plan_name VARCHAR(40) NOT NULL
);

CREATE TABLE subscriptions (
    subscription_id INTEGER PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES plans(plan_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(subscription_id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    status VARCHAR(12) NOT NULL CHECK (status IN ('completed', 'failed', 'pending'))
);

INSERT INTO plans (plan_id, plan_name) VALUES
    (1, 'Annual'),
    (2, 'Monthly'),
    (3, 'Starter'),
    (4, 'Preview');

INSERT INTO subscriptions (subscription_id, plan_id) VALUES
    (101, 1),
    (201, 2),
    (202, 2),
    (301, 3);

INSERT INTO payments (payment_id, subscription_id, amount_cents, status) VALUES
    (1, 101, 9000, 'completed'),
    (2, 201, 1200, 'failed'),
    (3, 201, 1200, 'completed'),
    (4, 201, 1200, 'completed'),
    (5, 202, 1200, 'pending');
