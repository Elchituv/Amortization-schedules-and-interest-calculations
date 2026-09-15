import sqlite3
from datetime import datetime, timedelta

class AmortizationCalculator:
    """מחשבון לוח סילוקין אוטומטי"""
    
    def __init__(self, db_path='loans.db'):
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.create_tables()
    
    def create_tables(self):
        """יוצר את הטבלאות"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Loans (
                loan_id             INTEGER PRIMARY KEY,
                borrower            TEXT NOT NULL,
                loan_amount         REAL NOT NULL,
                interest_rate       REAL NOT NULL,
                loan_term_months    INTEGER NOT NULL,
                grace_period_months INTEGER NOT NULL DEFAULT 0,
                grace_type          TEXT NOT NULL DEFAULT 'none'
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS PaymentSchedule (
                payment_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_id       INTEGER NOT NULL,
                month_number  INTEGER NOT NULL,
                payment_date  DATE NOT NULL,
                total_payment REAL NOT NULL,
                principal     REAL NOT NULL,
                interest      REAL NOT NULL,
                balance       REAL NOT NULL,
                is_grace_period INTEGER DEFAULT 0,
                
                FOREIGN KEY (loan_id) REFERENCES Loans(loan_id)
            )
        ''')
        
        self.db.commit()
    
    def add_loan(self, loan_id, borrower, loan_amount, interest_rate, 
                 loan_term_months, grace_period_months=0, grace_type='none'):
        """הוספת הלוואה חדשה"""
        self.cursor.execute('''
            INSERT INTO Loans 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (loan_id, borrower, loan_amount, interest_rate, 
              loan_term_months, grace_period_months, grace_type))
        self.db.commit()
        print(f"✅ הלוואה #{loan_id} של {borrower} נוספה בהצלחה!")
    
    def calculate_monthly_payment(self, principal, annual_rate, months):
        """
        חישוב התשלום החודשי באמצעות נוסחת אמורטיזציה
        
        נוסחה: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        כאשר:
        - P = קרן
        - r = שיעור ריבית חודשי
        - n = מספר חודשים
        """
        if annual_rate == 0:
            # אם אין ריבית - חלק את הקרן שווה בשווה
            return principal / months
        
        monthly_rate = annual_rate / 100 / 12
        numerator = monthly_rate * (1 + monthly_rate) ** months
        denominator = (1 + monthly_rate) ** months - 1
        
        return principal * (numerator / denominator)
    
    def generate_payment_schedule(self, loan_id):
        """יוצר לוח סילוקין מלא להלוואה"""
        
        # קריאת פרטי ההלוואה
        self.cursor.execute('SELECT * FROM Loans WHERE loan_id = ?', (loan_id,))
        loan = self.cursor.fetchone()
        
        if not loan:
            print(f"❌ לא נמצאה הלוואה #{loan_id}")
            return
        
        borrower = loan['borrower']
        principal = loan['loan_amount']
        annual_rate = loan['interest_rate']
        total_months = loan['loan_term_months']
        grace_months = loan['grace_period_months']
        grace_type = loan['grace_type']
        
        # חישוב התשלום החודשי
        payment_amount = self.calculate_monthly_payment(
            principal, annual_rate, total_months - grace_months
        )
        
        # תאריך התחלת התשלומים
        start_date = datetime.now()
        
        # יתרה נוכחית
        balance = principal
        payment_id = 1
        
        print(f"\n{'='*80}")
        print(f"📋 לוח סילוקין ל-{borrower}")
        print(f"{'='*80}")
        print(f"קרן מקורית: ₪{principal:,.2f}")
        print(f"שיעור ריבית שנתי: {annual_rate}%")
        print(f"תקופה: {total_months} חודשים (כולל {grace_months} חודשי גרייס)")
        print(f"תשלום חודשי: ₪{payment_amount:,.2f}")
        print(f"{'='*80}\n")
        
        # טבלה - כותרות
        print(f"{'חודש':<6} {'תאריך':<12} {'תשלום':<12} {'ריבית':<12} {'קרן':<12} {'יתרה':<12} {'גרייס':<8}")
        print("-" * 80)
        
        for month in range(1, total_months + 1):
            payment_date = start_date + timedelta(days=30 * month)
            is_grace = 1 if month <= grace_months else 0
            
            if is_grace:
                # בתקופת גרייס
                if grace_type == 'full':
                    # גרייס מלא - ללא תשלומים
                    monthly_interest = 0
                    monthly_principal = 0
                    monthly_payment = 0
                elif grace_type == 'partial':
                    # גרייס חלקי - ריבית בלבד
                    monthly_interest = balance * (annual_rate / 100 / 12)
                    monthly_principal = 0
                    monthly_payment = monthly_interest
                else:
                    monthly_interest = 0
                    monthly_principal = 0
                    monthly_payment = 0
            else:
                # חודש רגיל - תשלום מלא
                monthly_interest = balance * (annual_rate / 100 / 12)
                monthly_principal = payment_amount - monthly_interest
                monthly_payment = payment_amount
            
            # עדכון היתרה
            balance -= monthly_principal
            balance = max(0, balance)  # הימנע מערכים שליליים
            
            # הוספה לבסיס נתונים
            self.cursor.execute('''
                INSERT INTO PaymentSchedule 
                (loan_id, month_number, payment_date, total_payment, principal, interest, balance, is_grace_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (loan_id, month, payment_date.date(), monthly_payment, 
                  monthly_principal, monthly_interest, balance, is_grace))
            
            # הדפסה
            grace_text = "✓" if is_grace else "-"
            print(f"{month:<6} {payment_date.date():<12} ₪{monthly_payment:>10,.2f} ₪{monthly_interest:>10,.2f} ₪{monthly_principal:>10,.2f} ₪{balance:>10,.2f} {grace_text:<8}")
        
        self.db.commit()
        print(f"\n✅ לוח סילוקין של {borrower} חושב בהצלחה!")
    
    def show_summary(self, loan_id):
        """הצגת סיכום ההלוואה"""
        self.cursor.execute('''
            SELECT 
                l.borrower,
                l.loan_amount,
                l.interest_rate,
                COUNT(p.payment_id) as total_payments,
                SUM(p.interest) as total_interest,
                SUM(p.principal) as total_principal
            FROM Loans l
            LEFT JOIN PaymentSchedule p ON l.loan_id = p.loan_id
            WHERE l.loan_id = ?
            GROUP BY l.loan_id
        ''', (loan_id,))
        
        result = self.cursor.fetchone()
        
        if result:
            print(f"\n{'='*60}")
            print(f"📊 סיכום הלוואה")
            print(f"{'='*60}")
            print(f"שם הלווה: {result['borrower']}")
            print(f"קרן: ₪{result['loan_amount']:,.2f}")
            print(f"ריבית שנתית: {result['interest_rate']}%")
            print(f"סך תשלומים: {result['total_payments']}")
            print(f"סך הריבית ששולמה: ₪{result['total_interest'] or 0:,.2f}")
            print(f"סך הקרן ששולמה: ₪{result['total_principal'] or 0:,.2f}")
            print(f"{'='*60}\n")

# 🎬 דוגמה לשימוש
if __name__ == '__main__':
    calculator = AmortizationCalculator('loans.db')
    
    # דוגמה 1: הלוואה עם ריבית
    print("\n🔧 דוגמה 1️⃣: הלוואה עסקית עם ריבית")
    calculator.add_loan(
        loan_id=1,
        borrower='ישראל ישראלי',
        loan_amount=100000,
        interest_rate=5.00,
        loan_term_months=48,
        grace_period_months=6,
        grace_type='partial'
    )
    calculator.generate_payment_schedule(1)
    calculator.show_summary(1)
    
    # דוגמה 2: הלוואה ללא ריבית
    print("\n🔧 דוגמה 2️⃣: הלוואה ללא ריבית")
    calculator.add_loan(
        loan_id=2,
        borrower='שרה כהן',
        loan_amount=30000,
        interest_rate=0.00,
        loan_term_months=30,
        grace_period_months=0,
        grace_type='none'
    )
    calculator.generate_payment_schedule(2)
    calculator.show_summary(2)
