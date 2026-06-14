import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pickle

# Cargar dataset estáticas
df = pd.read_csv("datos_estaticas_limpio.csv", header=None)

# Separar datos y etiquetas
X = df.iloc[:, 1:]
y = df.iloc[:, 0]

# Dividir entrenamiento/prueba con stratify para distribución balanceada
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Modelo
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42
)

# Entrenar
model.fit(X_train, y_train)

# Precisión global
accuracy = model.score(X_test, y_test)

print(f"Precisión: {accuracy * 100:.2f}%")

# Reporte por clase para detectar señas con bajo rendimiento
y_pred = model.predict(X_test)
print("\n" + classification_report(y_test, y_pred))

# Guardar modelo
with open("modelo_estaticas.pkl", "wb") as f:

    pickle.dump(model, f)

print("Modelo estáticas guardado")