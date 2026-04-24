# TODO: Implement "Add All" Bulk Import and Enhance History Charts

## Status: [ ] In Progress

### Step-by-step Plan (Approved)

**1. Backend - Add /add_all route in app.py (Bulk CSV import)**
   - [ ] Add route @app.route('/add_all', methods=['GET', 'POST'])
   - [ ] GET: Render templates/add_all.html (upload form)
   - [ ] POST: Parse CSV with pandas, loop database.add_student() + predictions
   - [ ] Handle errors, flash success with count
   - [ ] Test with data/student_data.csv

**2. New Template - templates/add_all.html**
   - [ ] Create bulk upload form (file input, submit)
   - [ ] Style matching app (form-card, btn-submit)

**3. Update Templates - Add "Add All" buttons**
   - [ ] base.html: Navbar link to add_all
   - [ ] dashboard.html: Quick action card
   - [ ] students.html: Button next to "Add Student"

**4. Enhance prediction_history.html - Add Charts**
   - [ ] Risk distribution doughnut chart
   - [ ] GPA distribution bar chart
   - [ ] Filter/search JS already there, enhance
   - [ ] Stats cards (total predictions, avg GPA, etc.)

**5. Database/Verification**
   - [ ] Bulk adds generate predictions, show in history/charts
   - [ ] Test: run.bat, upload CSV, check students/history/analytics

**6. Completion**
   - [ ] attempt_completion

Next step: Implement /add_all route and templates/add_all.html

