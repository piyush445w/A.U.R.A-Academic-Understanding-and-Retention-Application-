import pickle
from sklearn.linear_model import LogisticRegression
import numpy as np

# Create a simple model
X = np.array([[0, 0], [1, 1]])
y = np.array([0, 1])
model = LogisticRegression()
model.fit(X, y)

# Save the model
with open('models/risk_model_v1.pkl', 'wb') as f:
    pickle.dump(model, f)

print('Model saved to models/risk_model_v1.pkl')