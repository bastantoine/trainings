from sqlalchemy import text


def test_db(app):
    with app.db.connect() as conn:
        # Prepare the DB and data
        conn.execute(
            text(
                """CREATE TABLE client
(
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    prenom VARCHAR(100),
    nom VARCHAR(100),
    ville VARCHAR(255),
    age INT
)"""
            )
        )
        conn.execute(
            text(
                """INSERT INTO client (prenom, nom, ville, age) VALUES
 ('Rébecca', 'Armand', 'Saint-Didier-des-Bois', 24),
 ('Aimée', 'Hebert', 'Marigny-le-Châtel', 36),
 ('Marielle', 'Ribeiro', 'Maillères', 27),
 ('Hilaire', 'Savary', 'Conie-Molitard', 58)"""
            )
        )

        # Search for any data
        result = conn.execute(text("""SELECT * FROM client"""))
        result = [row._asdict() for row in result.fetchall()]

    expected = [
        {"prenom": "Rébecca", "nom":"Armand", "vill": "Saint-Didier-des-Bois", "age": 24},
        {"prenom": "Aimée", "nom":"Hebert", "vill": "Marigny-le-Châtel", "age": 36},
        {"prenom": "Marielle", "nom":"Ribeiro", "vill": "Maillères", "age": 27},
        {"prenom": "Hilaire", "nom":"Savary", "vill": "Conie-Molitard", "age": 58},
    ]
    assert result == expected
