[README-2.md](https://github.com/user-attachments/files/29160589/README-2.md)
# התראות בורסה + ביתר ירושלים → טלגרם

שני בוטים עצמאיים שרצים על GitHub Actions ושולחים הודעת טלגרם:

**1. שעות מסחר (Wall Street / Nasdaq)** — שעון ניו יורק, מתעדכן אוטומטית בין קיץ/חורף:
- פתיחת מסחר מוקדם — 04:00
- פתיחת מסחר רגיל — 09:30
- סגירת מסחר רגיל — 16:00
- סגירת מסחר מאוחר — 20:00

לא נשלחות הודעות בסופ"ש ובחגים שבהם הבורסה סגורה.

**2. ביתר ירושלים** — כל בוקר בסביבות 08:00 שעון ישראל, בדיקה האם יש משחק היום (מקור: TheSportsDB, חינמי), ואם כן — הודעה עם היריבה והשעה.

## הקמה

**1. יצירת בוט בטלגרם**
1. פתח שיחה עם @BotFather בטלגרם, שלח `/newbot`, תן שם ו-username.
2. תקבל token — מחרוזת ארוכה, קבועה ולא פגה.
3. שלח הודעה כלשהי לבוט החדש שיצרת (כדי שהוא "יכיר" אותך).

**2. קבלת ה-chat ID שלך**
שלח הודעה לבוט @userinfobot בטלגרם — הוא יחזיר לך מספר. זה ה-chat ID שלך.

**3. יצירת ריפו ב-GitHub**
1. צור ריפו חדש (Public מומלץ — כך ה-Actions חינמיים ללא הגבלה).
2. העלה את כל הקבצים מהתיקייה הזו, כולל המבנה `.github/workflows/`.

**4. הגדרת Secrets**
ב-Settings, בתפריט הצד Secrets and variables, ואז Actions, לחץ New repository secret והוסף:
- `TELEGRAM_BOT_TOKEN` — ה-token משלב 1
- `TELEGRAM_CHAT_ID` — המספר משלב 2

**5. הרשאות כתיבה**
ב-Settings, בתפריט הצד Actions, ואז General, גלול ל-Workflow permissions, בחר Read and write permissions, ושמור.

**6. בדיקה**
עבור לטאב Actions למעלה בריפו. לכל workflow (Market Alerts / Beitar Jerusalem Match Day Alert) יש כפתור Run workflow להרצה ידנית מיידית לבדיקה.

## הערות
- כדי לשנות שעות באירועי הבורסה, ערוך את `EVENTS` בקובץ `market_alert.py`.
- כדי לעדכן את רשימת חגי הבורסה לשנה הבאה, ערוך את `MARKET_HOLIDAYS` באותו קובץ.
- כדי לעקוב אחרי קבוצה אחרת, שנה את `TEAM_ID` ב-`football_alert.py` (אפשר למצוא ID בכתובת של הקבוצה ב-thesportsdb.com).
