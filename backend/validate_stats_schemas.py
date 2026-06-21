'''
统计模块 Schema 字段一致性校验脚本
====================================

脚本用途
--------
本脚本用于验证后端统计模块的 6 个 API 接口实际返回的 JSON 字段集合，
与 app/schemas/stats.py 中对应 Pydantic Schema 类的字段集合完全一致。
通过对称差集比对自动识别：
  - API 返回了 Schema 中未定义的多余字段
  - Schema 定义了但 API 未返回的缺失字段
  - 嵌套对象（StatsResponse）字段也会递归校验

依赖库
------
- requests     发送 HTTP 请求调用后端 API
- pydantic     读取 Schema 类的 model_fields 定义
- FastAPI app  通过 app.schemas.stats 模块导入各 Schema 类

登录配置
--------
脚本内置管理员账号登录，登录成功后获取 Bearer Token 用于后续接口鉴权：
  - 登录地址 : http://localhost:8000/api/v1/auth/login
  - 用户名   : admin@example.com
  - 密码     : admin123
  - 传参方式 : application/x-www-form-urlencoded

运行命令
--------
  cd backend
  python3 validate_stats_schemas.py

注意：执行前请确保后端 uvicorn 服务已启动并监听 8000 端口。

退出码含义
----------
  0   全部接口与 Schema 字段完全一致，校验通过
  1   至少存在一处字段不匹配或接口请求失败，校验不通过

接口与 Schema 类映射关系表
--------------------------
  接口路径                  Schema 类名         校验内容
  ------------------------  ------------------  --------------------------------
  /stats/dashboard          DashboardStats       顶层 8 个统计字段
  /stats/activities         ActivityStats        顶层 6 个活动状态计数
  /stats/users              UserStats            顶层 9 个用户角色/状态统计
  /stats/monthly            MonthlyStats         顶层 8 个月环比字段
  /stats/trend/6            TrendData            顶层 4 个趋势数组字段
  /stats/all                StatsResponse        顶层 4 个嵌套对象 + 递归校验
                                                   - dashboard (DashboardStats)
                                                   - activities (ActivityStats)
                                                   - users (UserStats)
                                                   - monthly (MonthlyStats)
'''

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
