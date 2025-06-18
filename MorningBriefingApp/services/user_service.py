from auth import google_auth
from database.session import SessionLocal
from models import User


def upsert_user_from_google_profile():
    user_profile = google_auth.fetch_google_userinfo()

    email = user_profile['email']
    name = user_profile['name']

    with SessionLocal() as db:
        existing_user = db.query(User).filter_by(email=email).first()
        print(f"existing_user: {existing_user}")

        if existing_user:
            existing_user.email = email
            existing_user.name = name
        else:
            new_user = User(
                email=email,
                name=name
            )
            db.add(new_user)

        db.commit()