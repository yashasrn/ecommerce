# Engineering Challenges Faced & Resolutions

This document details the practical engineering hurdles encountered during the design, provisioning, and deployment of this cloud-native e-commerce infrastructure, along with the technical resolutions implemented.

---

## Challenge 1: Single Page Application (SPA) Client-Side 404 Routing on S3 + CloudFront

### The Problem
When hosting a modern React/Vite Single Page Application on Amazon S3 fronted by CloudFront, direct navigation to deep routes (e.g., `https://ecommerce.domain.com/cart` or `/orders`) resulted in `HTTP 403 Forbidden` or `HTTP 404 Not Found` errors from S3. Because S3 is an object store, it looked for an actual key named `cart` or `orders`, which does not exist on disk.

### The Resolution
1. Configured CloudFront **Custom Error Responses**:
   * Mapped `HTTP 403: Forbidden` and `HTTP 404: Not Found` error codes from the S3 origin to return `/index.html` with an `HTTP 200: OK` response code.
   * This allows React Router to intercept the URL client-side and render the correct view without page reload failures.
2. Implemented **Origin Access Control (OAC)**:
   * Migrated from legacy Origin Access Identity (OAI) to modern AWS CloudFront OAC.
   * Created an explicit S3 Bucket Policy allowing `s3:GetObject` strictly for the CloudFront Distribution ARN with `aws:SourceArn` condition.

---

## Challenge 2: ECS Fargate Task Inability to Pull Images from ECR in Private Subnets

### The Problem
When deploying the backend container onto ECS Fargate tasks located in private application subnets, tasks repeatedly failed during the provisioning phase with the error:
```
CannotPullContainerError: inspect image has been retried 5 time(s): failed to resolve reference ...: i/o timeout
```
Fargate tasks in private subnets have no public IP addresses and cannot reach the Amazon ECR public endpoints or AWS Secrets Manager over the internet.

### The Resolution
Evaluated two architectural approaches:
* **Option A: AWS VPC Interface Endpoints (PrivateLink)** for ECR (`ecr.api`, `ecr.dkr`), S3 Gateway Endpoint, Secrets Manager, and CloudWatch Logs.
* **Option B: Managed AWS NAT Gateway** in public subnets with default routes (`0.0.0.0/0`) in private subnet route tables.

**Decision**: Implemented Managed NAT Gateways (with an option for Single NAT in staging to optimize cost). Routed all outbound internet traffic from private subnets through the NAT Gateway. This enabled ECS Fargate to pull ECR container layers, retrieve Secrets Manager credentials, and communicate with external third-party APIs (Resend, Hugging Face) without exposing containers to direct inbound internet access.

---

## Challenge 3: Decoupling Database Secrets & Eliminating Hardcoded Passwords in IaC

### The Problem
Passing database master passwords as plain-text Terraform variables or storing them in `terraform.tfvars` files poses severe security risks and risks accidental commits into Git history. Furthermore, passing raw passwords as plain environment variables in ECS Task Definitions exposes them in plaintext in the AWS ECS Console and task inspection APIs.

### The Resolution
1. Used Terraform's `random_password` resource with high entropy (24 characters, alphanumeric + symbols).
2. Provisioned an **AWS Secrets Manager** secret resource (`/ecommerce/<env>/database`) that stores the structured JSON payload containing the username, password, host endpoint, port, database name, and formatted `DATABASE_URL`.
3. Granted the **ECS Task Execution IAM Role** `secretsmanager:GetSecretValue` permissions.
4. Referenced the secret ARN directly in the ECS Container Definition using the `secrets` attribute rather than `environment`:
   ```json
   "secrets": [
     {
       "name": "DATABASE_URL",
       "valueFrom": "${aws_secretsmanager_secret.db_credentials.arn}:DATABASE_URL::"
     }
   ]
   ```
   At container launch, the ECS agent fetches the secret value directly from AWS Secrets Manager into container memory, keeping it completely out of plain text.

---

## Challenge 4: Dual-Origin CloudFront Routing & CORS Ingress Conflicts

### The Problem
The application requires serving both static frontend assets (S3) and dynamic REST API endpoints (ALB -> ECS) under a unified domain. Routing API traffic through CloudFront initially triggered cross-origin resource sharing (CORS) errors and stripped essential HTTP headers (e.g., `Authorization`, `Host`, and `Cookies`), causing API authentication failures.

### The Resolution
1. Configured **Dual Origins** on the CloudFront Distribution:
   * **Primary Default Origin (`/*`)**: S3 bucket with OAC for static assets.
   * **Custom Ordered Cache Behavior (`/api/*`, `/health`, `/signup`, `/login`, etc.)**: Targeted directly to the Application Load Balancer DNS name.
2. For dynamic API behaviors:
   * Set `CachePolicyId` to AWS Managed `CachingDisabled` (`4135ea2d-6da8-44a3-9e09-6e7e787f5096`) so dynamic API responses are never stale-cached at the edge.
   * Configured `OriginRequestPolicyId` to AWS Managed `AllViewer` (`216adef6-5c7f-47e4-b989-5492eef07d36`) to forward all headers, query strings, and authorization tokens transparently to the backend.

---

## Challenge 5: Zero-Downtime Rolling Deployments & ALB Health Check Grace Periods

### The Problem
During CI/CD automated deployments (`aws ecs update-service --force-new-deployment`), newly spawned ECS Fargate tasks were prematurely receiving live production traffic before the Python Gunicorn server and database connection pool had fully initialized, resulting in transient `HTTP 502 Bad Gateway` spikes for active users.

### The Resolution
1. Added `health_check_grace_period_seconds = 60` to the `aws_ecs_service` Terraform definition, giving containers 60 seconds to warm up before the ALB begins routing traffic.
2. Tuned the ALB Target Group health check parameters:
   * Path: `/health`
   * Healthy Threshold: 2 consecutive checks
   * Interval: 15 seconds
   * Deregistration Delay: Reduced from default 300s to 30s to expedite draining of retiring tasks while completing inflight requests.
3. Configured ECS deployment circuit breaker with automatic rollback:
   ```hcl
   deployment_circuit_breaker {
     enable   = true
     rollback = true
   }
   ```
   If new container tasks fail health checks during rollout, ECS automatically cancels the deployment and reverts to the previous healthy task definition.

---

## Challenge 6: Keyless CI/CD Authentication via AWS IAM OIDC Federation

### The Problem
Managing long-lived AWS IAM User Access Keys (`AKIA...`) in GitHub Actions secrets is an anti-pattern:
* Keys are subject to rotation burden.
* Leaked keys can be exploited indefinitely from any IP.
* Compliance audits flag long-lived credentials.

### The Resolution
Implemented **OpenID Connect (OIDC)** authentication between GitHub Actions and AWS:
1. Configured AWS IAM OpenID Connect identity provider for `token.actions.githubusercontent.com`.
2. Created an IAM Role with an `AssumeRoleWithWebIdentity` trust policy restricted strictly to the specific GitHub repository and branch:
   ```json
   {
     "Effect": "Allow",
     "Principal": {
       "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
     },
     "Action": "sts:AssumeRoleWithWebIdentity",
     "Condition": {
       "StringEquals": {
         "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
       },
       "StringLike": {
         "token.actions.githubusercontent.com:sub": "repo:<ORG>/<REPO>:*"
       }
     }
   }
   ```
3. Utilized `aws-actions/configure-aws-credentials@v4` in GitHub Actions workflows to dynamically assume this role using ephemeral credentials valid for 1 hour.
