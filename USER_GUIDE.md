# Personal Development App - User Guide

## Welcome! 🎉

Welcome to the Personal Development App - your companion for building better habits and tracking your personal growth.

---

## Getting Started

### 1. Create Your Account

1. Navigate to the app homepage
2. Click **"Register"**
3. Enter your:
   - Username
   - Email address
   - Password (minimum 8 characters)
4. Click **"Sign Up"**
5. You'll be automatically logged in

### 2. Login

1. Click **"Login"** on the homepage
2. Enter your username and password
3. Click **"Sign In"**

---

## Managing Habits

### Creating a New Habit

1. Click **"Create Habit"** button from the Habits page
2. Fill in the habit details:
   - **Name**: What is the habit? (e.g., "Morning Meditation")
   - **Description**: Optional details about your habit
   - **Category**: Choose from:
     - 🏥 Health
     - 📊 Productivity
     - 💰 Finance
     - 📚 Learning
     - 👥 Relationships
     - 🔧 Other
   - **Frequency**: How often?
     - Daily (every day)
     - Weekly (once per week)
     - Monthly (once per month)
   - **Goal Count**: How many times per period (default: 1)
   - **Start Date**: When do you want to begin?
3. Click **"Create Habit"**

**Example Habits:**
- Name: "Morning Run", Category: Health, Frequency: Daily
- Name: "Read 30 Pages", Category: Learning, Frequency: Daily
- Name: "Budget Review", Category: Finance, Frequency: Weekly

### Viewing Your Habits

1. Go to **"My Habits"** page
2. You'll see:
   - All your active habits
   - Current streak for each habit 🔥
   - Habit category (color-coded)
   - Frequency information

### Logging Habit Completion

**Method 1: From Habit Detail Page**
1. Click on any habit card
2. Click **"Log Today's Completion"**
3. The date is automatically set to today
4. Select "Completed" (Yes/No)
5. Optionally add notes
6. Click **"Log Completion"**
7. See success message and updated streak!

**Pro Tip**: You can log completions for past dates by changing the date field.

### Editing a Habit

1. Click on the habit card
2. Click **"Edit Habit"** button
3. Update any fields
4. Click **"Save Changes"**

### Deleting a Habit

1. From the Habits list, click **"Delete"** on the habit card
2. Confirm deletion
3. ⚠️ Warning: This will delete all logs for this habit!

---

## Understanding Your Streaks

### Current Streak 🔥

Your **current streak** counts consecutive days you've completed a habit:
- Starts at 0 when you begin
- Increases by 1 for each consecutive day completed
- Resets to 0 if you miss a day

**Example:**
- Completed Jan 1, 2, 3, 4 → Streak = 4 days
- Missed Jan 5 → Streak resets to 0
- Completed Jan 6 → Streak = 1 day

### Longest Streak 🏆

Your **longest streak** is the maximum consecutive days you've ever achieved for that habit. This number never decreases - it's your personal record!

---

## Analytics Dashboard

### Accessing Analytics

Click **"Analytics"** in the navigation menu to see your comprehensive dashboard.

### Overview Cards

The top section shows key metrics:
- **Total Habits**: How many habits you're tracking
- **Active Habits**: Habits you're currently working on
- **Completion Rate**: Your success percentage (last 30 days)
- **Current Streak**: Your longest active streak
- **Longest Streak**: Your all-time best streak
- **This Month**: Total completions this month

### Weekly Progress Chart

📈 **Line Chart** showing:
- Daily completion rate (%) over the last 7 days
- Number of completions per day
- Trend visualization

**How to Read It:**
- Higher lines = better performance
- Consistent lines = steady habits
- Gaps or dips = days you missed

### Category Breakdown

🍩 **Doughnut Chart** displaying:
- Distribution of habits by category
- Color-coded categories
- Completion counts per category

**Use Cases:**
- See which life areas you focus on most
- Identify underrepresented categories
- Balance your habit portfolio

### Category Statistics

Detailed list showing:
- Number of habits per category
- Total completions per category
- Visual color indicators

---

## Exporting Your Data

### Why Export?

Export your habit data for:
- Backup purposes
- Sharing with coaches/therapists
- Data analysis in Excel/Google Sheets
- Long-term record keeping

### CSV Export

1. Go to **Analytics** page
2. Click **"Download CSV"** button
3. File downloads with name: `habits_export_YYYYMMDD_HHMMSS.csv`

**CSV Format:**
```csv
Habit Name,Category,Frequency,Goal Count,Start Date,Date Logged,Completed
Morning Run,health,daily,1,2026-01-01,2026-01-01,Yes
Morning Run,health,daily,1,2026-01-01,2026-01-02,Yes
```

**Best For:**
- Excel/Sheets analysis
- Creating custom charts
- Importing to other apps

### JSON Export

1. Go to **Analytics** page
2. Click **"Download JSON"** button
3. File downloads with name: `habits_export_YYYYMMDD_HHMMSS.json`

**JSON Structure:**
```json
{
  "user": "john_doe",
  "export_date": "2026-02-02T14:32:10",
  "habits": [
    {
      "name": "Morning Run",
      "category": "health",
      "frequency": "daily",
      "streak_count": 5,
      "longest_streak": 10,
      "logs": [
        {"date": "2026-01-01", "completed": true},
        {"date": "2026-01-02", "completed": true}
      ]
    }
  ]
}
```

**Best For:**
- Developers/programmers
- Technical analysis
- Database imports
- API integrations

---

## Tips for Success

### 1. Start Small
- Begin with 1-3 habits
- Choose easy wins to build momentum
- Gradually add more habits

### 2. Be Consistent
- Log completions daily
- Set reminders if needed
- Make it part of your routine

### 3. Track What Matters
- Focus on meaningful habits
- Align with your goals
- Review and adjust monthly

### 4. Use Categories Wisely
- Balance different life areas
- Don't over-index on one category
- Review category breakdown monthly

### 5. Celebrate Streaks
- Acknowledge milestones (7, 30, 100 days)
- Share achievements with friends
- Reward yourself for consistency

### 6. Don't Fear Breaking Streaks
- Missing a day happens
- Restart immediately
- Focus on long-term trends, not perfection

### 7. Review Analytics Weekly
- Check weekly progress chart
- Identify patterns
- Adjust habits if needed

---

## Common Questions

### Can I log past dates?
Yes! When logging a completion, change the date field to any date in the past.

### Can I log the same habit multiple times per day?
No, each habit can only be logged once per day (unique constraint). Use "Goal Count" for habits requiring multiple repetitions.

### What happens if I delete a habit?
All logs associated with that habit are permanently deleted. Export your data first if you want to keep records.

### Can I change a habit's frequency?
Yes, edit the habit and update the frequency. Note: This doesn't affect past logs or streak calculations.

### How is completion rate calculated?
```
Completion Rate = (Completed Days / Total Days Since Start) × 100
```
For analytics dashboard, it's calculated for the last 30 days.

### Do I need to log a habit every single day?
For **daily habits**, yes - to maintain your streak.
For **weekly/monthly habits**, log once per period.

### Can I have multiple users/accounts?
Yes, but each account is completely separate. Habits and data don't transfer between accounts.

### Is my data private?
Yes! Your habits and logs are only visible to your account. No other users can see your data.

---

## Keyboard Shortcuts

(Future feature - coming soon!)

- `N` - Create new habit
- `A` - Go to Analytics
- `H` - Go to Habits
- `L` - Log today's completion (when viewing habit)

---

## Mobile Usage

The app is fully responsive and works on:
- 📱 Smartphones (iOS/Android)
- 📱 Tablets (iPad, Android tablets)
- 💻 Desktop computers

**Mobile Tips:**
- Add to home screen for app-like experience
- Use in portrait mode for best experience
- Swipe navigation works smoothly

---

## Troubleshooting

### Can't log in?
- Check username spelling (case-sensitive)
- Verify password
- Try "Forgot Password" (if implemented)
- Clear browser cache

### Don't see my habits?
- Ensure you're logged in
- Refresh the page
- Check internet connection
- Verify you created habits for this account

### Analytics not loading?
- Check internet connection
- Refresh the page
- Create at least one habit with logs

### Export buttons not working?
- Ensure you have at least one habit
- Check browser allows downloads
- Try different browser
- Disable ad blockers

### Charts not displaying?
- Ensure you have logged completions
- Refresh the page
- Try different browser
- Check browser console for errors

---

## Feature Roadmap

Coming soon:
- [ ] Push notifications/reminders
- [ ] Habit templates
- [ ] Social sharing
- [ ] Challenges & badges
- [ ] AI-powered insights
- [ ] Dark mode
- [ ] Mobile apps (iOS/Android)
- [ ] Habit stacking suggestions

---

## Support & Feedback

### Need Help?
- Email: support@personaldevelopment.app
- Submit feedback form (coming soon)
- Report bugs via GitHub issues

### Stay Updated
- Follow development on GitHub
- Join our community (Discord/Slack coming soon)
- Subscribe to newsletter

---

## Privacy & Security

- Your password is encrypted
- Data is stored securely
- HTTPS encryption for all traffic
- No data selling/sharing
- Export your data anytime
- Delete account option available

---

## Credits

Built with:
- Django REST Framework (Backend)
- React + Vite (Frontend)
- Chart.js (Analytics)
- PostgreSQL (Database)

---

**Last Updated**: February 2, 2026  
**Version**: 1.0.0 (MVP)
