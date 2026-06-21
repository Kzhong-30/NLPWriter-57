import sys
import requests
from app.schemas.stats import (
    DashboardStats,
    ActivityStats,
    UserStats,
    MonthlyStats,
    TrendData,
    StatsResponse,
)
BASE_URL = "http://localhost:8000/api/v1"

endpoints = [
    ("/stats/dashboard", DashboardStats),
    ("/stats/activities", ActivityStats),
    ("/stats/users", UserStats),
    ("/stats/monthly", MonthlyStats),
    ("/stats/trend/6", TrendData),
    ("/stats/all", StatsResponse),
]


def get_access_token():
    login_url = f"{BASE_URL}/auth/login"
    data = {
        "username": "admin@example.com",
        "password": "admin123",
    }
    response = requests.post(login_url, data=data)
    response.raise_for_status()
    token_data = response.json()
    return token_data["access_token"]


def check_nested_schema(data, schema_class, path=""):
    all_passed = True
    schema_fields = set(schema_class.model_fields.keys())
    data_keys = set(data.keys())

    diff = data_keys.symmetric_difference(schema_fields)
    if diff:
        print(f"  FAIL Nested {path}{schema_class.__name__}: diff = {sorted(diff)}")
        all_passed = False
    else:
        print(f"  PASS Nested {path}{schema_class.__name__}")

    for field_name, field_info in schema_class.model_fields.items():
        annotation = field_info.annotation
        if hasattr(annotation, "__origin__"):
            continue
        if isinstance(annotation, type) and hasattr(annotation, "model_fields"):
            if field_name in data and isinstance(data[field_name], dict):
                nested_passed = check_nested_schema(
                    data[field_name], annotation, f"{path}{field_name}."
                )
                if not nested_passed:
                    all_passed = False

    return all_passed


def main():
    all_passed = True

    try:
        access_token = get_access_token()
    except Exception as e:
        print(f"ERROR: Failed to get access token: {e}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {access_token}"}

    for endpoint_path, schema_class in endpoints:
        full_url = f"{BASE_URL}{endpoint_path}"
        print()
        print(f"Checking {endpoint_path} against {schema_class.__name__}...")

        try:
            response = requests.get(full_url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  FAIL: Request error: {e}")
            all_passed = False
            continue

        schema_fields = set(schema_class.model_fields.keys())
        data_keys = set(data.keys())

        diff = data_keys.symmetric_difference(schema_fields)
        if diff:
            print(f"  FAIL Top-level: diff = {sorted(diff)}")
            print(f"    Response keys: {sorted(data_keys)}")
            print(f"    Schema fields: {sorted(schema_fields)}")
            all_passed = False
        else:
            print(f"  PASS Top-level")

        if schema_class == StatsResponse:
            nested_passed = check_nested_schema(data, schema_class)
            if not nested_passed:
                all_passed = False

    print()
    print("=" * 50)
    if all_passed:
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
