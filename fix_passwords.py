#!/usr/bin/env python3
"""
Fix Users with Empty or Invalid Password Hashes
Intelligent Student Risk Monitoring & Decision Support System
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash


def fix_empty_passwords(app):
    """Find and fix users with empty or invalid password hashes."""
    with app.app_context():
        users = User.query.all()
        fixed = []
        invalid = []

        for user in users:
            needs_fix = False
            reason = ""

            if not user.password_hash or not user.password_hash.strip():
                needs_fix = True
                reason = "empty password_hash"
            elif not user.password_hash.startswith("pbkdf2:") and not user.password_hash.startswith("scrypt:") and not user.password_hash.startswith("argon2:"):
                needs_fix = True
                reason = f"invalid hash format (starts with: {user.password_hash[:20]})"

            if needs_fix:
                default_password = f"{user.role}123"
                user.password_hash = generate_password_hash(default_password)
                fixed.append({
                    "username": user.username,
                    "role": user.role,
                    "reason": reason,
                    "new_password": default_password
                })
                print(f"  FIXED: {user.username} ({user.role}) - {reason} -> password set to '{default_password}'")

        if fixed:
            db.session.commit()
            print(f"\nFixed {len(fixed)} user(s).")
        else:
            print("\nNo users with empty or invalid password hashes found.")

        return fixed


def list_all_users(app):
    """List all users and their password hash status."""
    with app.app_context():
        users = User.query.all()
        print(f"\nTotal users: {len(users)}\n")
        print(f"{'ID':<5} {'Username':<20} {'Role':<12} {'Hash Status':<20}")
        print("-" * 60)

        for user in users:
            if not user.password_hash or not user.password_hash.strip():
                status = "EMPTY"
            elif not user.password_hash.startswith("pbkdf2:") and not user.password_hash.startswith("scrypt:") and not user.password_hash.startswith("argon2:"):
                status = "INVALID FORMAT"
            else:
                status = "OK"

            print(f"{user.id:<5} {user.username:<20} {user.role:<12} {status:<20}")


def main():
    print("\n" + "=" * 60)
    print("Fix Empty/Invalid Password Hashes")
    print("=" * 60)

    app = create_app("development")

    print("\n[1] Listing all users...")
    list_all_users(app)

    print("\n[2] Fixing users with empty/invalid password hashes...")
    fixed = fix_empty_passwords(app)

    print("\n[3] Final user list...")
    list_all_users(app)

    if fixed:
        print("\n" + "=" * 60)
        print("DEFAULT PASSWORDS FOR FIXED USERS:")
        print("=" * 60)
        for f in fixed:
            print(f"  {f['username']} ({f['role']}): {f['new_password']}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
