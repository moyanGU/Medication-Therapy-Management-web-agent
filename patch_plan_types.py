with open("src/pages/MtmPlanFormPage.vue", "r") as f:
    content = f.read()

# Update buildPayload type casting
content = content.replace(
    "priority: form.priority,",
    "priority: form.priority as 'low' | 'medium' | 'high' | 'urgent',"
)
content = content.replace(
    "patient_confirmation_status: form.patient_confirmation_status,",
    "patient_confirmation_status: form.patient_confirmation_status as 'pending' | 'confirmed' | 'declined',"
)

with open("src/pages/MtmPlanFormPage.vue", "w") as f:
    f.write(content)
