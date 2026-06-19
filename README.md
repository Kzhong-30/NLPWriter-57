# 志愿者服务管理平台

基于 Vue 3 + Element Plus + FastAPI + PostgreSQL 的全栈志愿者服务管理系统。

## 功能特性

### 组织端
- 活动发布：填写活动名称、时间地点、需求人数、服务内容、报名条件
- 志愿者资料审核
- 活动管理
- 签到统计
- 证书发放

### 志愿者端
- 浏览活动列表
- 提交报名申请
- 等待审核通过
- 现场签到签退（扫码/GPS定位）
- 自动记录服务时长
- 时长认证生成电子证书
- 导出 PDF 证书
- 服务时长兑换积分
- 积分兑换公益周边

### 社区功能
- 分享志愿故事
- 活动照片墙
- 优秀志愿者展示

### 数据统计
- 活动参与人数统计
- 服务总时长统计
- 覆盖区域地图

## 技术栈

- **前端**: Vue 3 + Element Plus + Vue Router + Pinia + Axios
- **后端**: FastAPI + SQLAlchemy + Pydantic + Alembic
- **数据库**: PostgreSQL
- **其他**: Docker, JWT, ReportLab(PDF)

## 快速开始

### 1. 启动数据库

```bash
docker-compose up -d
```

### 2. 启动后端服务

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

后端 API 文档: http://localhost:8000/docs

### 3. 启动前端服务

```bash
cd frontend
npm install
npm run dev
```

前端地址: http://localhost:5173
