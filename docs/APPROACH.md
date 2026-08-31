# Senior DevOps Technical Approach & Architecture Documentation

## 1. Executive Summary & Architecture Overview

This project implements an enterprise-grade, highly available, secure, and cost-optimized cloud infrastructure on Amazon Web Services (AWS) using **Terraform (IaC)**, **GitHub Actions (CI/CD)**, **Amazon ECS Fargate**, **Amazon RDS PostgreSQL 16**, **Amazon CloudFront**, and **AWS CloudWatch**.

The platform is designed around cloud-native Twelve-Factor principles, prioritizing:
1. **Zero-Trust Security**: Multi-tier isolated networking, non-root container runtimes, KMS-encrypted storage, automated secret injection via AWS Secrets Manager, and keyless CI/CD via OpenID Connect (OIDC).
2. **High Availability & Fault Tolerance**: Multi-AZ deployments for critical compute and database workloads, automated health checks, and self-healing container auto-scaling.
3. **Operational Excellence**: Centralized structured logging, proactive alerting via Amazon SNS, and dual CloudWatch operational dashboards for real-time telemetry.
4. **Cost Optimization**: Separation of static and dynamic compute (CloudFront + S3 for UI, Fargate for API), configurable single vs. multi-NAT gateways, and GP3 dynamic storage allocation.

---

## 2. System Architecture Diagram

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
                   │  Amazon S3 Bucket│  │  Application Load Balancer  │
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

## 3. Infrastructure as Code (Terraform) Blueprint

### 3.1 Network Topology & Subnet Segmentation
The infrastructure uses a 3-tier VPC design across 2 Availability Zones (`us-east-1a`, `us-east-1b`):
* **Public Subnets (`10.0.1.0/24`, `10.0.2.0/24`)**: Host internet-facing Application Load Balancers and managed NAT Gateways.
* **Private Application Subnets (`10.0.10.0/24`, `10.0.11.0/24`)**: Host ECS Fargate container tasks without public IP addresses, routing outbound traffic through NAT Gateways.
* **Private Database Subnets (`10.0.20.0/24`, `10.0.21.0/24`)**: Completely isolated subnets with **no route to the internet**, housing the RDS PostgreSQL cluster.

### 3.2 Compute & Ingress Strategy: Why S3 + CloudFront & ECS Fargate?
* **Frontend Hosting (S3 + CloudFront)**:
  Instead of running Node/Nginx containers 24/7 on EC2 or ECS for static frontend assets, assets are compiled into static bundles and hosted on Amazon S3 fronted by CloudFront CDN. This reduces compute costs to near-zero, provides sub-10ms global edge caching, and automatically offloads DDoS traffic.
* **Backend API Compute (ECS Fargate)**:
  Serverless containers eliminate the overhead of managing EC2 host operating systems, patching AMIs, or managing Kubernetes control plane upgrades (EKS). Fargate tasks execute on demand with dedicated CPU/memory reservations and scale dynamically based on real-time load.

### 3.3 Security Groups & Least Privilege Matrix
Traffic flows strictly downstream through security group references (no broad IP CIDRs in internal tiers):
1. **ALB SG**: Inbound TCP 80/443 from `0.0.0.0/0`.
2. **ECS Backend SG**: Inbound TCP 5000 **strictly from ALB SG ID**.
3. **RDS Database SG**: Inbound TCP 5432 **strictly from ECS Backend SG ID**.

---

## 4. Database Architecture & Secrets Management

### 4.1 RDS PostgreSQL 16 Configuration
* **Engine**: PostgreSQL 16.4 on AWS Graviton (`db.t4g.micro` in staging, `db.t4g.medium` in production).
* **High Availability**: Multi-AZ standby replica in production with automated failover.
* **Storage**: Amazon GP3 dynamic storage with automated storage auto-scaling up to 100 GB.
* **Encryption**: AWS KMS-managed AES-256 encryption at rest; encrypted automated daily backups.

### 4.2 Dynamic Secret Injection (No Hardcoded Secrets)
* Master database credentials are generated using Terraform `random_password` and stored directly into **AWS Secrets Manager** (`/ecommerce/<env>/database`).
* The ECS Task Execution Role is granted IAM permission to read the secret at container startup.
* In the ECS Container Definition, the secret is mapped directly to the `DATABASE_URL` environment variable using `secrets` ARN reference:
  ```json
  "secrets": [
    {
      "name": "DATABASE_URL",
      "valueFrom": "${db_secret_arn}:DATABASE_URL::"
    }
  ]
  ```
  This ensures zero database passwords exist in source control, environment files, or container image layers.

---

## 5. CI/CD Deployment Automation (GitHub Actions)

### 5.1 Keyless Authentication via AWS IAM OIDC
Traditional CI/CD pipelines require storing long-lived `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in GitHub repository secrets, which pose significant credential leakage risks.

This pipeline uses **AWS OpenID Connect (OIDC) Federation**:
* GitHub Actions requests a short-lived JSON Web Token (JWT).
* AWS Security Token Service (STS) validates the token against GitHub's OIDC Provider and assumes an IAM Role (`role-to-assume`) for only the duration of the deployment.

### 5.2 Pull Request Pipeline (`ci.yml`)
1. **Terraform Format & Lint**: Runs `terraform fmt -check`, `terraform init -backend=false`, and `terraform validate`.
2. **Backend Unit & SAST Testing**:
   * Runs Python 3.12 `flake8` linting.
   * Executes static security scans with `bandit` and dependency checks with `safety`.
   * Runs `pytest tests/` unit and integration test suite.
3. **Frontend Build Validation**:
   * Runs ESLint and production asset build (`npm run build`).
4. **Vulnerability Scanning**:
   * Scans container image layers and repo filesystem using **Aqua Security Trivy** for CVEs.

### 5.3 Continuous Deployment Pipeline (`cd.yml`)
```
Merge to Main ──► Build Docker & Push to ECR ──► Deploy Staging (ECS + S3/CDN)
                                                          │
                                                    Health Verification
                                                          │
                                                          ▼
                                            [Manual Approval Gate]
                                            (GitHub Environment: Prod)
                                                          │
                                                          ▼
                                              Deploy Production (ECS + S3/CDN)
```

---

## 6. Observability, Logging, and SRE Dashboards

### 6.1 Centralized Logging
* Backend container stdout/stderr streams are piped to CloudWatch Logs (`/ecs/ecommerce-<env>-backend`) via the `awslogs` driver.
* Log retention is automatically managed (14 days for staging, 30 days for production) to optimize storage cost.
* A **CloudWatch Metric Filter** pattern matches `ERROR`, `Exception`, and `500` occurrences to generate a live `BackendErrorCount` operational metric.

### 6.2 Proactive Alerting (Amazon SNS)
* Alarms configured for:
  - ECS Service CPU / Memory utilization > 80%
  - ALB Target 5XX count > 5 within 5 minutes
  - ALB Target Latency > 2.0 seconds
  - RDS CPU > 80% and Free Storage < 5 GB
* Connected to an Amazon SNS topic for immediate engineer notification via email or Slack webhook.

### 6.3 Dual CloudWatch Dashboards
1. **Service Health & Performance Dashboard**: Real-time ingress telemetry, request volume, p50/p95 target response times, HTTP status code distribution (2xx, 4xx, 5xx), and ECS container compute usage.
2. **Database & Infrastructure Reliability Dashboard**: RDS PostgreSQL active connection counts, freeable memory, storage headroom, and CloudFront global edge delivery health.

---

## 7. Cost Optimization Strategy

| Measure | Implementation | Rationale |
| :--- | :--- | :--- |
| **Edge-Optimized Static UI** | CloudFront CDN + S3 Bucket | Eliminates 24/7 container compute costs for static HTML/JS/CSS assets. |
| **Configurable NAT Gateways** | Single NAT in Staging (`enable_single_nat_gateway = true`), Multi-AZ in Prod | Saves ~$35/month per NAT gateway in non-production environments. |
| **Serverless Compute** | AWS Fargate with Auto Scaling | No idle EC2 instance charges; scale to zero/minimum capacity during off-peak hours. |
| **Storage Optimization** | AWS GP3 SSDs + S3 Lifecycle Policies | GP3 provides 20% lower cost per GB compared to GP2 with decoupled baseline IOPS. |
| **Log Retention Policies** | 14-30 day expiration on CloudWatch Log Groups | Prevents unconstrained log storage billing growth over time. |
