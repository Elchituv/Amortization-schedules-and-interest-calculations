# טבלאות לוח סילוקין וחישובי ריבית | Amortization Schedules & Interest Calculations

## תיאור הפרויקט
פרויקט זה כולל טבלאות SQL לניהול הלוואות ויצירת לוח סילוקין מפורט עם:
- חישוב תשלומים חודשיים
- הפרדה בין קרן וריבית
- תמיכה בתקופות גרייס (חודשי החלפה)
- דוגמאות עם הלוואות בריבית ובלי ריבית

---

## מבנה הטבלאות

### 1. טבלת `Loans` (ההלוואות)
| עמודה | סוג | תיאור |
|------|-----|-------|
| `loan_id` | INT | מזהה ייחודי של ההלוואה |
| `borrower` | VARCHAR | שם הלווה |
| `loan_amount` | DECIMAL | קרן המקורית |
| `interest_rate` | DECIMAL | שיעור הריבית השנתית (%) |
| `loan_term_months` | INT | אורך ההלוואה בחודשים |
| `grace_period_months` | INT | מספר חודשי גרייס |
| `grace_type` | TEXT | סוג הגרייס: none / partial / full |

### 2. טבלת `PaymentSchedule` (לוח הסילוקין)
| עמודה | סוג | תיאור |
|------|-----|-------|
| `payment_id` | INT | מזהה תשלום |
| `loan_id` | INT | קישור להלוואה (מפתח זר) |
| `month_number` | INT | מספר החודש |
| `payment_date` | DATE | תאריך התשלום |
| `total_payment` | DECIMAL | סך התשלום החודשי |
| `principal` | DECIMAL | החלק של הקרן |
| `interest` | DECIMAL | החלק של הריבית |
| `balance` | DECIMAL | היתרה הנותרת |
| `is_grace_period` | INT | האם חודש גרייס? (0/1) |

---

## דוגמאות

### דוגמה 1: הלוואה עסקית עם ריבית
```sql
INSERT INTO Loans VALUES
  (1, 'ישראל ישראלי', 100000, 5.00, 48, 6, 'partial');
```

**תוצאות החודשים הראשונים:**

| לווה | קרן מקורית | חודש | תשלום חודשי | ריבית | קרן | יתרה |
|------|-----------|------|-----------|-------|-----|------|
| ישראל ישראלי | 100,000 | 1 | 2,302.93 | 416.67 | 1,886.26 | 98,113.74 |
| ישראל ישראלי | 100,000 | 2 | 2,302.93 | 408.81 | 1,894.12 | 96,219.62 |
| ישראל ישראלי | 100,000 | 3 | 2,302.93 | 400.92 | 1,902.01 | 94,317.60 |

### דוגמה 2: הלוואה ללא ריבית
```sql
INSERT INTO Loans VALUES
  (2, 'שרה כהן', 30000, 0.00, 30);
```

**תוצאות (כל הקרן בכל תשלום):**

| לווה | קרן מקורית | חודש | תשלום חודשי | ריבית | קרן | יתרה |
|------|-----------|------|-----------|-------|-----|------|
| שרה כהן | 30,000 | 1 | 1,000.00 | 0.00 | 1,000.00 | 29,000.00 |
| שרה כהן | 30,000 | 2 | 1,000.00 | 0.00 | 1,000.00 | 28,000.00 |
| שרה כהן | 30,000 | 3 | 1,000.00 | 0.00 | 1,000.00 | 27,000.00 |

---

## Queries שימושיים

### הצג את לוח הסילוקין של הלוואה מסוימת
```sql
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
```

### סה"כ ריבית וקרן לפי סוג חודש (גרייס או החזר)
```sql
SELECT 
    is_grace_period,
    COUNT(*) AS num_payments,
    SUM(interest) AS total_interest,
    SUM(principal) AS total_principal
FROM PaymentSchedule
WHERE loan_id = 1
GROUP BY is_grace_period;
```

---

## SQL CREATE STATEMENTS

```sql
-- טבלת ה"אחד": הלוואות
CREATE TABLE Loans (
    loan_id             INTEGER PRIMARY KEY,
    borrower            TEXT NOT NULL,
    loan_amount         REAL NOT NULL,
    interest_rate       REAL NOT NULL,
    loan_term_months    INTEGER NOT NULL,
    grace_period_months INTEGER NOT NULL DEFAULT 0,
    grace_type          TEXT NOT NULL DEFAULT 'none'
);

-- טבלת ה"רבים": שורות לוח הסילוקין
CREATE TABLE PaymentSchedule (
    payment_id    INTEGER PRIMARY KEY,
    loan_id       INTEGER NOT NULL,
    month_number  INTEGER NOT NULL,
    payment_date  DATE NOT NULL,
    total_payment REAL NOT NULL,
    principal     REAL NOT NULL,
    interest      REAL NOT NULL,
    balance       REAL NOT NULL,
    is_grace_period INTEGER DEFAULT 0,
    
    FOREIGN KEY (loan_id) REFERENCES Loans(loan_id)
);
```

---

**כתוב על ידי:** Elchituv  
**תאריך עדכון:** 2026-09-15
