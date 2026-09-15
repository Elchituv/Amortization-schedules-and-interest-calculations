-- טבלת ה"אחד": הלוואות
CREATE TABLE Loans (
    loan_id        INT           PRIMARY KEY,
    borrower       VARCHAR(100)  NOT NULL,
    loan_amount    DECIMAL(10,2) NOT NULL,
    interest_rate  DECIMAL(5,2)  NOT NULL,
    loan_term_months INT         NOT NULL
);

-- טבלת ה"רבים": שורות לוח הסילוקין
CREATE TABLE PaymentSchedule (
    payment_id    INT           PRIMARY KEY,
    loan_id       INT           NOT NULL,          -- ← המפתח הזר
    month_number  INT           NOT NULL,
    payment_date  DATE          NOT NULL,
    total_payment DECIMAL(10,2) NOT NULL,
    principal     DECIMAL(10,2) NOT NULL,
    interest      DECIMAL(10,2) NOT NULL,
    balance       DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (loan_id) REFERENCES Loans(loan_id)
);

-- שתי ההלוואות מהדוגמאות שבנינו יחד
INSERT INTO Loans VALUES
  (1, 'ישראל ישראלי',  100000, 5.00, 48),  -- הלוואה עסקית, שפיצר
  (2, 'שרה כהן',        30000, 0.00, 30);  -- הלוואה ללא ריבית (כמו עוגן)

-- שורות לוח סילוקין — שלוש הראשונות של הלוואה 1
INSERT INTO PaymentSchedule VALUES
  (1, 1, 1, '2024-02-01', 2302.93, 1886.26,  416.67, 98113.74),
  (2, 1, 2, '2024-03-01', 2302.93, 1894.12,  408.81, 96219.62),
  (3, 1, 3, '2024-04-01', 2302.93, 1902.01,  400.92, 94317.60),

-- שלוש הראשונות של הלוואה 2 (ריבית = 0 בכל שורה)
  (4, 2, 1, '2024-03-01', 1000.00, 1000.00,    0.00, 29000.00),
  (5, 2, 2, '2024-04-01', 1000.00, 1000.00,    0.00, 28000.00),
  (6, 2, 3, '2024-05-01', 1000.00, 1000.00,    0.00, 27000.00);

-- כל שורות לוח הסילוקין יחד עם פרטי ההלוואה
SELECT
    l.borrower         AS לווה,
    l.loan_amount      AS קרן_מקורית,
    p.month_number     AS חודש,
    p.total_payment    AS תשלום_חודשי,
    p.interest         AS ריבית,
    p.principal        AS קרן,
    p.balance          AS יתרה
FROM Loans l
JOIN PaymentSchedule p ON l.loan_id = p.loan_id
WHERE l.loan_id = 1
ORDER BY p.month_number;
-- כמה תשלומים לכל הלוואה 
SELECT
    l.borrower         AS לווה,
    l.loan_amount      AS קרן_מקורית,
    p.month_number     AS חודש,
    p.total_payment    AS תשלום_חודשי,
    p.interest         AS ריבית,
    p.principal        AS קרן,
    p.balance          AS יתרה
FROM Loans l
JOIN PaymentSchedule p ON l.loan_id = p.loan_id
WHERE l.loan_id = 1
ORDER BY p.month_number;

-- פרטי הגרייס בטבלת ההלוואה
CREATE TABLE Loans (
    loan_id             INTEGER PRIMARY KEY,
    borrower            TEXT NOT NULL,
    loan_amount         REAL NOT NULL,
    interest_rate       REAL NOT NULL,
    loan_term_months    INTEGER NOT NULL,
    grace_period_months INTEGER NOT NULL DEFAULT 0,    -- כמה חודשי גרייס
    grace_type          TEXT NOT NULL DEFAULT 'none'   -- none / partial / full
);

INSERT INTO Loans VALUES (1,'ישראל ישראלי',100000,5.00,48,6,'partial');

ALTER TABLE PaymentSchedule
ADD COLUMN is_grace_period INTEGER DEFAULT 0;

UPDATE PaymentSchedule
SET is_grace_period = 1
FROM Loans
WHERE PaymentSchedule.loan_id = Loans.loan_id
  AND PaymentSchedule.month_number <= Loans.grace_period_months;

SELECT is_grace_period,
       COUNT(*)        AS num_payments,
       SUM(interest)   AS total_interest,
       SUM(principal)  AS total_principal
FROM PaymentSchedule
WHERE loan_id = 1
GROUP BY is_grace_period;

-- בדיקת טעויות

SELECT month_number, principal
FROM PaymentSchedule
WHERE is_grace_period = 1
  AND principal > 0; 
SELECT month_number,
       principal,
       CASE WHEN principal = 0 THEN 'גרייס' ELSE 'החזר' END AS stage
FROM PaymentSchedule
WHERE loan_id = 1;
