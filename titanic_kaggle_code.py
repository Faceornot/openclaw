import pandas as pd
import numpy as np

from sklearn.model_selection import cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression


def extract_title(name: str) -> str:
    title = name.split(',')[1].split('.')[0].strip()
    rare_titles = {
        'Lady', 'Countess', 'Capt', 'Col', 'Don', 'Dr', 'Major',
        'Rev', 'Sir', 'Jonkheer', 'Dona'
    }
    if title in rare_titles:
        return 'Rare'
    if title in ['Mlle', 'Ms']:
        return 'Miss'
    if title == 'Mme':
        return 'Mrs'
    return title


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df['Title'] = df['Name'].apply(extract_title)
    df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
    df['CabinKnown'] = df['Cabin'].notna().astype(int)
    df['CabinLetter'] = df['Cabin'].fillna('U').astype(str).str[0]

    df['Age'] = df.groupby(['Title', 'Pclass'])['Age'].transform(
        lambda x: x.fillna(x.median())
    )
    df['Age'] = df['Age'].fillna(df['Age'].median())

    df['Fare'] = df.groupby('Pclass')['Fare'].transform(
        lambda x: x.fillna(x.median())
    )
    df['Fare'] = df['Fare'].fillna(df['Fare'].median())

    df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])

    return df


def main():
    train_path = '/kaggle/input/titanic/train.csv'
    test_path = '/kaggle/input/titanic/test.csv'

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)

    full = pd.concat([train.drop(columns=['Survived']), test], axis=0, ignore_index=True)
    full = build_features(full)

    features = [
        'Pclass', 'Sex', 'Age', 'Fare', 'Embarked',
        'FamilySize', 'IsAlone', 'Title', 'CabinKnown', 'CabinLetter'
    ]

    X_full = full[features]
    X_train = X_full.iloc[:len(train)]
    X_test = X_full.iloc[len(train):]
    y_train = train['Survived']

    numeric_features = ['Age', 'Fare', 'FamilySize']
    categorical_features = ['Pclass', 'Sex', 'Embarked', 'IsAlone', 'Title', 'CabinKnown', 'CabinLetter']

    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer([
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

    models = {
        'LogisticRegression': LogisticRegression(max_iter=2000, random_state=42),
        'RandomForest': RandomForestClassifier(
            n_estimators=300,
            max_depth=6,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=42
        )
    }

    best_name = None
    best_score = -1
    best_pipeline = None

    print('===== Cross Validation Results =====')
    for name, model in models.items():
        clf = Pipeline([
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        scores = cross_val_score(clf, X_train, y_train, cv=5, scoring='accuracy')
        mean_score = scores.mean()
        print(f'{name}: {mean_score:.5f}')

        if mean_score > best_score:
            best_score = mean_score
            best_name = name
            best_pipeline = clf

    print('\nBest model:', best_name)
    print('Best CV accuracy:', round(best_score, 5))

    best_pipeline.fit(X_train, y_train)
    predictions = best_pipeline.predict(X_test)

    submission = pd.DataFrame({
        'PassengerId': test['PassengerId'],
        'Survived': predictions.astype(int)
    })
    submission.to_csv('submission.csv', index=False)

    print('\nsubmission.csv 已生成，可直接用于 Kaggle 提交。')


if __name__ == '__main__':
    main()
