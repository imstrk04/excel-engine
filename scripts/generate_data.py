import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============================================
# STRUCTURED DATA GENERATION (1000 rows, 10 columns)
# ============================================

print("Generating structured data...")

# Generate 1000 rows of structured data
n_rows = 1000

structured_data = {
    'EmployeeID': range(1001, 1001 + n_rows),
    'Name': [f"Employee_{i}" for i in range(1, n_rows + 1)],
    'Department': np.random.choice(['Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Operations'], n_rows),
    'Age': np.random.randint(22, 65, n_rows),
    'Salary': np.random.randint(30000, 150000, n_rows),
    'JoiningDate': [datetime(2015, 1, 1) + timedelta(days=random.randint(0, 3650)) for _ in range(n_rows)],
    'Performance_Score': np.random.uniform(1.0, 5.0, n_rows).round(2),
    'Years_Experience': np.random.randint(0, 25, n_rows),
    'Location': np.random.choice(['Chennai', 'Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Pune'], n_rows),
    'Status': np.random.choice(['Active', 'Inactive', 'On Leave'], n_rows, p=[0.85, 0.10, 0.05])
}

df_structured = pd.DataFrame(structured_data)

# ============================================
# UNSTRUCTURED DATA GENERATION (1000 rows, 5 columns)
# ============================================

print("Generating unstructured data...")

# Predefined text templates for realistic data
feedback_templates = [
    "The product quality is excellent and exceeded my expectations.",
    "Very disappointed with the service. Would not recommend.",
    "Average experience. Nothing special but gets the job done.",
    "Outstanding customer support! They resolved my issue quickly.",
    "The delivery was delayed by 2 weeks. Very frustrating experience.",
    "Great value for money. Highly satisfied with the purchase.",
    "The interface is confusing and needs improvement.",
    "Fantastic product! Will definitely buy again.",
    "Poor packaging resulted in damaged goods.",
    "Excellent communication throughout the process.",
    "Not worth the price. Expected better quality.",
    "Good product but shipping costs are too high.",
    "The team was very professional and helpful.",
    "Received defective item. Return process was smooth though.",
    "Impressive features and easy to use."
]

issue_descriptions = [
    "Login credentials not working after password reset.",
    "Payment gateway timeout during checkout process.",
    "Unable to download invoice from customer portal.",
    "Mobile app crashes when uploading images.",
    "Email notifications not being received.",
    "Dashboard shows incorrect sales figures.",
    "Search functionality returns irrelevant results.",
    "Export to PDF feature not functioning properly.",
    "Profile picture upload fails with error message.",
    "Two-factor authentication code not received.",
    "Subscription renewal failed despite valid card.",
    "Reports generation takes too long to process.",
    "Integration with third-party tool disconnected.",
    "Customer data sync issue between platforms.",
    "Checkout cart items disappearing randomly."
]

product_reviews = [
    "This product transformed my workflow completely. Highly recommended for professionals.",
    "Build quality could be better. Feels cheap for the price point.",
    "Exactly what I needed. Setup was straightforward and quick.",
    "Customer service is non-responsive. Been waiting for reply for days.",
    "Good features but the learning curve is steep for beginners.",
    "Best purchase I made this year. Worth every penny.",
    "Software has too many bugs. Needs several updates to fix issues.",
    "Sleek design and intuitive interface. Very user-friendly.",
    "Overpriced compared to competitors offering similar features.",
    "Reliability issues. System crashes frequently during peak usage.",
    "Great for small teams but lacks enterprise-level features.",
    "Documentation is comprehensive and helpful for new users.",
    "The latest update broke several key functionalities.",
    "Responsive design works perfectly across all devices.",
    "Limited customization options. Too rigid for our needs."
]

account_summaries = [
    "Long-standing customer with consistent monthly orders. High engagement with loyalty program.",
    "New account created last month. Single purchase made. Subscribed to newsletter.",
    "Premium member since 2020. Frequent purchases across multiple categories. Zero complaints.",
    "Account flagged for suspicious activity. Investigation pending. Transactions temporarily frozen.",
    "Inactive account. Last login 6 months ago. Multiple failed re-engagement campaigns.",
    "High-value customer. Average order value $500+. Prefers express shipping. VIP support tier.",
    "Seasonal buyer. Active during holiday periods. Dormant rest of the year.",
    "Recent downgrade from premium to basic plan. Cited budget constraints.",
    "Corporate account with multiple sub-users. Bulk ordering patterns. Net-30 payment terms.",
    "Trial account nearing expiration. Limited feature usage. No conversion signals.",
    "Frequent returns but not fraudulent. Picky about product specifications.",
    "Loyal customer with regular referrals. Brand advocate on social media.",
    "Payment issues. Multiple declined transactions. Updated billing info required.",
    "Cross-platform user. Shops via mobile app and website equally.",
    "Recently filed complaint about delivery delays. Compensation provided."
]

project_notes = [
    "Project on track. All milestones met. Team morale is high. Budget utilization at 65%.",
    "Critical delays due to resource constraints. Need immediate attention. Escalated to management.",
    "Successfully completed ahead of schedule. Client extremely satisfied. Potential for expansion.",
    "Scope creep identified. Multiple change requests from stakeholder. Timeline revision needed.",
    "Technical debt accumulating. Refactoring required. Performance issues reported.",
    "Strong collaboration between teams. Regular sync meetings proving effective.",
    "Budget overrun by 15%. Cost optimization strategies being implemented.",
    "Quality assurance concerns. Multiple defects found in recent sprint. Additional testing required.",
    "Innovative solution implemented. Patent application in progress. Competitive advantage gained.",
    "Stakeholder communication breakdown. Misaligned expectations. Urgent meeting scheduled.",
    "Pilot phase successful. Moving to production rollout next quarter.",
    "Team member resigned. Knowledge transfer incomplete. Hiring replacement urgently.",
    "Integration challenges with legacy system. Exploring alternative approaches.",
    "Positive feedback from user acceptance testing. Minor UI tweaks requested.",
    "Risk mitigation strategies in place. Contingency budget allocated. All good so far."
]

unstructured_data = {
    'RecordID': range(2001, 2001 + n_rows),
    'CustomerFeedback': [random.choice(feedback_templates) for _ in range(n_rows)],
    'IssueDescription': [random.choice(issue_descriptions) for _ in range(n_rows)],
    'ProductReview': [random.choice(product_reviews) for _ in range(n_rows)],
    'AccountSummary': [random.choice(account_summaries) for _ in range(n_rows)]
}

# Add some variation to make it more realistic
for i in range(n_rows):
    if random.random() < 0.3:
        unstructured_data['CustomerFeedback'][i] += f" Order ID: {random.randint(10000, 99999)}."
    if random.random() < 0.2:
        unstructured_data['IssueDescription'][i] += f" Ticket #{random.randint(1000, 9999)}."
    if random.random() < 0.25:
        unstructured_data['ProductReview'][i] += f" Rating: {random.randint(1, 5)}/5."

df_unstructured = pd.DataFrame(unstructured_data)

# ============================================
# SAVE TO EXCEL FILE (Multiple Sheets)
# ============================================

print("Saving data to Excel file...")

# Create Excel writer object
excel_filename = 'data/synthetic_data.xlsx'

with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
    df_structured.to_excel(writer, sheet_name='Structured_Data', index=False)
    df_unstructured.to_excel(writer, sheet_name='Unstructured_Data', index=False)

print(f"\n✓ Successfully created '{excel_filename}' with 2 sheets:")
print(f"  - Sheet 1 'Structured_Data': {len(df_structured)} rows × {len(df_structured.columns)} columns")
print(f"  - Sheet 2 'Unstructured_Data': {len(df_unstructured)} rows × {len(df_unstructured.columns)} columns")

# Display sample data
print("\n" + "="*80)
print("STRUCTURED DATA SAMPLE (First 5 rows):")
print("="*80)
print(df_structured.head())

print("\n" + "="*80)
print("UNSTRUCTURED DATA SAMPLE (First 5 rows):")
print("="*80)
print(df_unstructured.head())

print("\n" + "="*80)
print("STRUCTURED DATA INFO:")
print("="*80)
print(df_structured.info())

print("\n" + "="*80)
print("STRUCTURED DATA STATISTICS:")
print("="*80)
print(df_structured.describe())

print("\n✓ Data generation completed successfully!")
print(f"✓ File saved as: {excel_filename}")