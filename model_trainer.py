from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train(X, y, test_size: float = 0.2, random_state: int = 42):
    """
    Chia du lieu va huan luyen mo hinh RandomForest.
    X           : tap dac trung (features)
    y           : nhan (labels)
    test_size   : ti le tap kiem tra, mac dinh 20%
    random_state: hat giong ngau nhien, de ket qua tai hien duoc
    """
    # Chia du lieu thanh 2 tap: huan luyen va kiem tra
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state
    )

    # Khoi tao va huan luyen mo hinh
    model = RandomForestClassifier(n_estimators=100, random_state=random_state)
    model.fit(X_train, y_train)

    # Danh gia tren tap kiem tra
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"Huan luyen xong. Accuracy tren tap test: {acc:.4f}")
    return model, acc
