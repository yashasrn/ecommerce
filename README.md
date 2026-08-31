# E-Commerce Platform

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red)
![AI](https://img.shields.io/badge/AI-Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)

**A modern e-commerce platform with seller management system, and comprehensive order tracking.**

Built with React, TypeScript, Python(Flask), PostgreSQL .

---

## 📚 Table of Contents

- [☁️ Enterprise Cloud Infrastructure & DevOps](#️-enterprise-cloud-infrastructure--devops)
- [✨ Features](#-features)
- [📸 Screenshots](#-screenshots)
- [🛠️ Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Getting Started](#-getting-started)
- [🏗️ Infrastructure Provisioning (Terraform)](#-infrastructure-provisioning-terraform)
- [🔄 CI/CD Pipelines (GitHub Actions)](#-cicd-pipelines-github-actions)
- [📊 Monitoring & Observability](#-monitoring--observability)
- [🔐 Security & Secret Management](#-security--secret-management)
- [API Endpoints](#-api-endpoints)
- [Database Schema](#-database-schema)
- [Admin Tools](#-admin-tools)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Contact](#-contact)

---

## Cloud Infrastructure,DevOps & Architecture Overview

This repository includes a production-grade, highly available AWS cloud architecture provisioned with Terraform , automated with GitHub Actions (CI/CD), and monitored via  CloudWatch & Amazon SNS.

* Comprehensive Approach & Architecture Guide (./ecommerce/docs/APPROACH.md) : Deep dive into architectural design decisions, multi-tier network topology, compute strategy (Fargate vs EKS), and cost optimization.
* Challenges Faced & Resolutions (./ecommerce/docs/CHALLENGES_AND_RESOLUTIONS.md): In-depth breakdown of realistic engineering challenges faced during the development process (CloudFront OAC SPA routing, private subnet ECR pulling, dynamic secret injection, dual-origin CORS, and OIDC CI/CD).
* Monitoring, Logging & Observability (./ecommerce/docs/MONITORING_AND_OBSERVABILITY.md)**: Centralized logging setup, metric filters, operational alarms, and CloudWatch dashboards.

```
                           Internet (Clients)
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │    Amazon CloudFront (CDN)      │
                  │   (Global Edge Caching & WAF)   │
                  └────────┬───────────────┬────────┘
                           │               │
          Default Static   │               │ Dynamic API Routes
          Assets (/*)      │               │ (/api/*, /health, /signup...)
                           ▼               ▼
                 ┌──────────────────┐  ┌─────────────────────────────┐
                 │  Amazon S3 Bucket │  │  Application Load Balancer  │
                 │ (Origin Access   │  │   (Public Subnets / ALB)    │
                 │   Control - OAC) │  └──────────────┬──────────────┘
                 └──────────────────┘                 │
                                                      ▼
                                       ┌─────────────────────────────┐
                                       │   AWS VPC (10.0.0.0/16)     │
                                       │                             │
                                       │  ┌───────────────────────┐  │
                                       │  │ Private App Subnets   │  │
                                       │  │ (ECS Fargate Service) │  │
                                       │  │  ┌─────────────────┐  │  │
                                       │  │  │ Flask App (API) │  │  │
                                       │  │  │ Non-root user   │  │  │
                                       │  │  └────────┬────────┘  │  │
                                       │  └───────────┼───────────┘  │
                                       │              │              │
                                       │  ┌───────────▼───────────┐  │
                                       │  │ Private DB Subnets    │  │
                                       │  │ (RDS PostgreSQL 16)   │  │
                                       │  │ Multi-AZ / Encrypted  │  │
                                       │  └───────────────────────┘  │
                                       └─────────────────────────────┘
```

---

## Features

### 🛒 Customer Features
- 🔐 **User Authentication** - Signup/Login with OTP verification via Resend API
- 🛍️ **Shopping Cart** - Add, remove, and manage cart items
- 💳 **Secure Checkout** - Complete order with address details
- 📦 **Order Tracking** - View order history and status
- 🤖 **AI Chatbot** - Product search and customer support (Hugging Face Mistral-7B)
- 📧 **Email Notifications** - Order confirmations via Resend API
- 🔍 **Product Filtering** - Browse by categories

### 👨‍💼 Seller Features
- 📝 **Seller Registration** - Apply to become a seller with approval workflow
- ➕ **Product Management** - Add, edit, delete products
- ✅ **Draft/Publish System** - Control product visibility
- 📊 **Activity Logging** - Track all product changes with audit trail
- 📧 **Email Notifications** - Get notified on approval/rejection
- 📈 **Seller Dashboard** - Manage inventory and view analytics

### 🔧 Admin Features
- ✔️ **Seller Approval System** - Approve/reject seller applications via admin script
- 📩 **Contact Management** - Handle customer inquiries
- 📊 **System Monitoring** - Overview of platform activity
- 🛠️ **Database Management** - Auto-create tables with setup script
- 📧 **Email Queue** - Automated email notifications

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Flask** | Python web framework |
| **PostgreSQL** | AWS(RDS)  |
| **psycopg2** | PostgreSQL adapter for Python |
| **bcrypt** | Password hashing |
| **Resend API** | Email service for OTP & notifications |
| **Flask-CORS** | Cross-origin requests |
| **python-dotenv** | Environment variables |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React** | UI library |
| **TypeScript** | Type safety |
| **Vite** | Build tool |
| **Axios** | HTTP client |
| **CSS3** | Styling |

### 3rd Party Services
- **Resend** - Transactional email API
---

### Installation

```env
RESEND_API_KEY=re_your_key_here
```

---

## 🏗️ Infrastructure Provisioning (Terraform)

All AWS infrastructure is managed as code under [`infra/terraform/`](file:///Users/yashas/Desktop/project-infra/ecommerce/infra/terraform).

### Prerequisites
* [Terraform >= 1.5.0](https://www.terraform.io/downloads.html)
* [AWS CLI v2](https://aws.amazon.com/cli/) configured with appropriate IAM permissions
* S3 Bucket + DynamoDB Table for remote state locking (optional for local experimentation)

### Modular Infrastructure Structure
* `modules/vpc`: 3-Tier VPC with Public, Private App, and Isolated DB subnets across 2 AZs.
* `modules/security`: Strictly chained least-privilege security groups (Internet -> ALB -> ECS -> RDS).
* `modules/s3_frontend`: Encrypted S3 bucket with CloudFront Origin Access Control (OAC).
* `modules/alb`: Internet-facing ALB with `/health` target group and HTTP listeners.
* `modules/cloudfront`: Global CDN with dual origins (S3 static SPA + ALB dynamic API).
* `modules/rds`: Multi-AZ PostgreSQL 16 on GP3 storage with automated KMS encryption & daily backups.
* `modules/ecr`: Container registry with image scanning on push and automated lifecycle policies.
* `modules/ecs`: Auto-scaling ECS Fargate cluster with non-root task execution and dynamic Secrets Manager injection.
* `modules/monitoring`: Centralized CloudWatch Log Groups, Metric Filters, SNS Alerts, and 2 Complete SRE Dashboards.

### Deployment Commands

#### 1. Staging Deployment
```bash
cd infra/terraform

# Initialize Terraform modules and backend
terraform init

# Validate configuration syntax
terraform validate

# Plan provisioning for staging
terraform plan -var-file="environments/staging.tfvars" -out="staging.tfplan"

# Apply staging infrastructure
terraform apply "staging.tfplan"
```

#### 2. Production Deployment
```bash
# Plan provisioning for production
terraform plan -var-file="environments/production.tfvars" -out="production.tfplan"

# Apply production infrastructure
terraform apply "production.tfplan"
```

#### 3. Teardown
```bash
terraform destroy -var-file="environments/staging.tfvars"
```

---

## 🔄 CI/CD Pipelines (GitHub Actions)

Located in [`.github/workflows/`](file:///Users/yashas/Desktop/project-infra/ecommerce/.github/workflows):

### 1. Pull Request Verification (`ci.yml`)
* **Triggers**: On pull request against `main` or `develop`.
* **Jobs**:
  * **Terraform Checks**: `terraform fmt -check`, `terraform validate`.
  * **Backend Checks**: Python 3.12 `flake8` linting, `pytest` unit tests, `bandit` SAST scan, `safety` dependency scan.
  * **Frontend Checks**: ESLint validation, TypeScript validation, dry-run production asset build (`npm run build`).
  * **Security Scan**: Container vulnerability scanning via **Aqua Security Trivy**.

### 2. Multi-Stage Continuous Deployment (`cd.yml`)
* **Authentication**: **Keyless AWS IAM OIDC Federation** (`aws-actions/configure-aws-credentials`) — zero static keys stored in GitHub Secrets.
* **Pipeline Stages**:
  1. **Build & Push**: Builds multi-stage Docker image, tags with commit SHA, and pushes to Amazon ECR.
  2. **Deploy to Staging**: Automatically updates Staging ECS Fargate service, syncs frontend to Staging S3, invalidates CloudFront cache, and verifies `/health`.
  3. **Deploy to Production**: Enforces **GitHub Environments Manual Approval Gate** before rolling update to Production ECS and Production S3/CloudFront.
  4. **Notifications**: Automated deployment summary to Slack / Webhook.

---

## 📊 Monitoring & Observability

Provisioned automatically via [`modules/monitoring`](file:///Users/yashas/Desktop/project-infra/ecommerce/infra/terraform/modules/monitoring):

### CloudWatch Metric Alarms
*  **ECS High CPU / Memory**: Triggers alert when utilization exceeds 80% for 4 minutes.
*  **ALB 5XX Error Rate**: Alerts if >5 server errors occur in a 5-minute window.
*  **ALB High Latency**: Alerts if target response time averages >2.0s.
*  **RDS High CPU & Low Storage**: Alerts when PostgreSQL CPU > 80% or free storage < 5 GB.

### CloudWatch Dashboards
1. **`ecommerce-<env>-infrastructure-dashboard`**: ALB request rates, response times, HTTP status codes (2XX, 4XX, 5XX), ECS CPU/Memory, and RDS PostgreSQL metrics.
2. **`ecommerce-<env>-application-dashboard`**: ECS active vs. desired task count, backend application error logs (metric filter), CloudFront global bandwidth, and edge error rates.

---

## Security & Secret Management

* **Zero Hardcoded Passwords**: Database passwords generated with high entropy via Terraform and stored directly in **AWS Secrets Manager**.
* **Direct Task Injection**: ECS tasks retrieve database connection credentials directly from Secrets Manager at startup into container memory.
* **Defense in Depth**: Database subnets have zero internet routing; compute tasks reside in private subnets behind managed NAT gateways; public ingress is strictly handled by CloudFront CDN and ALB.
* **Backup & Recovery**: Daily automated RDS snapshots with point-in-time recovery (PITR) up to 30 days and deletion protection in production.

---
**Authentication**
```
POST /signup - User registration
POST /login - User login
POST /send-otp - Send OTP verification via Resend
POST /verify-otp - Verify OTP code
```

**Seller Management**
```
POST /seller-signup - Seller registration (creates pending seller)
POST /seller-login - Seller login (only approved sellers)
GET /seller-products - Get seller's products
POST /check-seller-status - Check approval status
GET /seller-activity - Get activity logs
POST /update-seller-status - Approve/reject seller (admin only)
```
**Products**
```
GET /products - Get all published products
GET /products/<id> - Get single product details
POST /add-product - Add new product (seller only)
PUT /products/<id> - Update product
DELETE /products/<id> - Delete product
PATCH /products/<id>/publish - Publish product
PATCH /products/<id>/unpublish - Unpublish (draft) product
```
## Orders
```
POST /save-order - Save order to database
POST /send-order-email - Send order confirmation via Resend
GET /get-orders/<email> - Get user's order history
Chatbot (AI - Hugging Face)
POST /chat - Basic AI chat with Mistral-7B
POST /chat-with-history - Chat with conversation context
POST /chat-product-search - AI-powered product search
```
## Contact
```
POST /contact-us - Submit contact form
GET /admin/contact-messages - Get all messages (admin)
```
## 💾 Database Schema
**Tables Created by create_tables.py:**

- Users - Customer accounts with authentication
- Sellers - Seller accounts with approval status
- Products - Product catalog (draft/published states)
- Orders - Customer order information
- OrderItems - Individual items in orders
- ProductActivityLog - Audit trail for product changes
- SellerStatusChanges - Track seller approval/rejection with email queue
- ContactMessages - Customer support inquiries

## Triggers:

trg_seller_status_change - Auto-log status changes and queue emails

## Indexes:

Optimized for seller email, product ID, and timestamp queries

## 🛠️ Admin Tools
**Database Setup Script**
- File: create_tables.py

- Purpose: Automatically creates all database tables, indexes, and triggers

**Usage:**
```bash

cd Backend
python create_tables.py
```
**Features:**

- ✅ Drops old tables safely
- ✅ Creates all tables in correct order
- ✅ Sets up foreign keys
- ✅ Creates indexes for performance
- ✅ Sets up email notification triggers
- ✅ Verifies setup

## Seller Management Tool (CRUD)
- File: approve_seller.py

- Purpose: Admin interface for managing sellers

**Usage:**

```bash

cd Backend
python approve_seller.py
```
**Features:**

**READ/VIEW:**

- View all sellers
- View pending sellers
- View seller details by ID

**UPDATE:**

- Approve seller (sends email, allows login)
- Reject seller (sends email, blocks login)

## Update seller information
**CREATE:**

Manually create seller with chosen status

**DELETE:**

Delete seller and all products

**EMAIL:**
**Send pending approval emails**
- 🔒 Security Features
- ✅ Password hashing with bcrypt
- ✅ OTP verification for signup via Resend API
- ✅ Environment variables for sensitive data
- ✅ SQL injection protection (parameterized queries)
- ✅ Session management
- ✅ Secure authentication flow
- ✅ API keys never exposed to frontend
- ✅ CORS protection with Flask-CORS
- ✅ PostgreSQL SSL mode enabled

## 🐛 Troubleshooting
**Backend Issues**

**PostgreSQL connection error:**
```bash

DATABASE_URL=postgresql://user:password@host/dbname
```
**python create_tables.py**

**psycopg2 installation fails:**

```bash
pip install psycopg2-binary
```
**Hugging Face API errors:**

✅ Check if HF_API_KEY is valid
✅ First request takes 20-30 seconds (model loading)
✅ Free tier has rate limits
✅ Check https://status.huggingface.co/
```
**Resend email not sending:**

- ✅ Verify RESEND_API_KEY is correct
- ✅ Free tier: 3,000 emails/month, 100/day
- ✅ Check dashboard: https://resend.com/emails
- ✅ Verify sender email

**Import errors:**
```bash
pip install -r requirements.txt
```
## Frontend Issues
**Module not found:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Port already in use:**
```bash
export default defineConfig({
  server: { port: 3000 }
})
```

## CORS errors:
- Verify backend URL in frontend config
- Check Flask-CORS is installed
- Verify backend is running

## Build errors:
```bash
npm run build
```
## Database Issues
**Tables not created:**
```bash
python create_tables.py
Seller can't login after approval:
```
Run approve_seller.py to check status
Verify status is "Approved" (case-sensitive)
Products not showing:

Check product status is "published" (not "draft")
Verify seller is approved

## 📝 License
© 2025 Gowni Shashank. All Rights Reserved.

This software is proprietary and confidential. See the LICENSE file for complete terms.

**📋 License Summary**
- ✅ Viewable for portfolio/demonstration purposes only
- ❌ No permission to use, copy, modify, or distribute
- ❌ Commercial use strictly prohibited without written permission
- 💼 For licensing inquiries: shashankgowni09@gmail.com
This project is shared publicly to showcase my development capabilities.

## 🙏 Acknowledgments

**Flask - Python web framework**
- Hugging Face - AI model hosting and Mistral-7B model
- Resend - Modern email API
- React - Frontend library
- Vite - Build tool
- PostgreSQL - Database
- Render - Cloud database hosting
- Vercel - Frontend deployment


## 📬 Contact
**Gowni Shashank**

📧 Email: shashankgowni09@gmail.com
💼 LinkedIn: linkedin.com/in/shashankgowni
🐙 GitHub: @ShashankGowni

Open to collaboration on interesting projects.

**Created with 💻 by Gowni Shashank • January 2025 🌍**

