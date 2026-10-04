import pandas as pd
import joblib

# ── Load saved model & metadata ───────────────────────────
model           = joblib.load('severity_model.joblib')
feature_columns = joblib.load('feature_columns.joblib')
severity_labels = joblib.load('severity_labels.joblib')

print("✅ Model loaded successfully")

# ── Example: predict for a new student complaint ──────────
new_complaint = pd.DataFrame([{
    'Age'   : 20,
    'Gpa'   : 2.5,
    'Year'  : 2,
    'Gender': 0,          # 0=M, 1=F
    'Genre' : 'Technology and IT Support'
}])

# Apply same encoding as training
new_complaint = pd.get_dummies(new_complaint, columns=['Genre'])

# Align columns — fills missing genre columns with 0
new_complaint = new_complaint.reindex(columns=feature_columns, fill_value=0)

# Predict
pred_index = model.predict(new_complaint)[0]
pred_label = severity_labels[pred_index]
probabilities = model.predict_proba(new_complaint)[0]

print(f"\n🎯 Predicted Severity : {pred_label}")
print("\n📊 Confidence per class:")
for label, prob in zip(severity_labels, probabilities):
    print(f"   {label:10s} → {prob*100:.1f}%")