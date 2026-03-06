#!/usr/bin/env python3
import argparse
import asyncio
import sys
from pathlib import Path

# Allow running this file directly from repo root or backend/scripts.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import init_db  # noqa: E402
from models import SuperAdmin, UserRole  # noqa: E402
from routers.auth import get_password_hash  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize or update one superadmin account."
    )
    parser.add_argument("--username", required=True, help="Superadmin username")
    parser.add_argument("--password", required=True, help="Superadmin password")
    parser.add_argument(
        "--name",
        default="System Administrator",
        help="Display name (default: System Administrator)",
    )
    parser.add_argument(
        "--reset-if-exists",
        action="store_true",
        help="If user exists, reset password/name/role fields.",
    )
    return parser.parse_args()


async def run() -> int:
    args = parse_args()

    await init_db()
    existing = await SuperAdmin.find_one({"username": args.username})

    if existing is None:
        admin = SuperAdmin(
            username=args.username,
            password_hash=get_password_hash(args.password),
            name=args.name,
            desc="Super Admin",
            role="Superadmin",
            user_role=UserRole.SUPERADMIN,
            icon="i-carbon-user-admin",
        )
        await admin.insert()
        print(f"[OK] Superadmin created: {args.username}")
        return 0

    if not args.reset_if_exists:
        print(
            f"[SKIP] Superadmin already exists: {args.username}. "
            "Use --reset-if-exists to rotate password and profile fields."
        )
        return 0

    existing.password_hash = get_password_hash(args.password)
    existing.name = args.name
    existing.desc = "Super Admin"
    existing.role = "Superadmin"
    existing.user_role = UserRole.SUPERADMIN
    existing.icon = "i-carbon-user-admin"
    await existing.save()
    print(f"[OK] Superadmin updated: {args.username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
