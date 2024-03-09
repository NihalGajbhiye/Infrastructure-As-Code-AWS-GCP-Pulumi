# Infrastructure Deployment Overview

This README provides detailed information about the infrastructure components used in the Pulumi deployment script. The infrastructure consists of resources from AWS (Amazon Web Services) and GCP (Google Cloud Platform) and includes various services such as VPC, subnets, RDS, SNS, Lambda functions, EC2 instances, Load Balancers, and more.

<img width="600" alt="AWS_Flow" src="https://github.com/NihalGajbhiye/Infrastructure-As-Code-AWS-GCP-Pulumi/assets/85219483/19206902-30cd-4404-81cc-4738b47f1993">

## Components Used

### AWS (Amazon Web Services)

1. **VPC (Virtual Private Cloud)**:
   - The VPC provides an isolated virtual network environment where resources like EC2 instances and RDS databases can be launched. It ensures network security and control over IP addressing.

2. **Subnets**:
   - Subnets divide the VPC into multiple segments to control the network traffic and provide security. Public subnets are accessible from the internet, while private subnets are not directly accessible.

3. **Internet Gateway (IGW)**:
   - The Internet Gateway enables communication between instances in the VPC and the internet. It serves as a gateway for outbound and inbound traffic.

4. **Route Tables**:
   - Route tables define rules for routing network traffic within the VPC. They specify the destination for traffic leaving the subnet.

5. **RDS (Relational Database Service)**:
   - RDS provides managed database services, including PostgreSQL in this case. It simplifies database management tasks and ensures high availability and durability.

6. **SNS (Simple Notification Service)**:
   - SNS allows the sending and receiving of notifications and alerts. It can be integrated with various AWS services to trigger notifications based on events.

7. **Lambda Function**:
   - Lambda functions are serverless compute services that execute code in response to triggers. They can be used for various tasks, including data processing, automation, and event-driven actions.

8. **CloudWatch**:
   - CloudWatch provides monitoring and observability for AWS resources. It collects and tracks metrics, logs, and events, enabling resource optimization and troubleshooting.

9. **Elastic Load Balancer (ELB)**:
   - ELB distributes incoming application traffic across multiple targets, such as EC2 instances, to ensure high availability and fault tolerance. It automatically scales to handle varying load levels.

10. **Autoscaling Group**:
    - Autoscaling groups automatically adjust the number of EC2 instances based on demand or other criteria. They help maintain application performance and optimize costs by scaling resources up or down as needed.

### GCP (Google Cloud Platform)

1. **Storage Bucket**:
   - GCP storage buckets provide scalable storage solutions for objects and data. They support various storage classes and access control features.

2. **Service Account**:
   - Service accounts allow interactions with GCP resources on behalf of applications and services. They are associated with specific roles and permissions for secure access control.

## Integration Overview

1. **VPC Setup**:
   - The VPC is created with specified CIDR blocks, enabling DNS support and hostnames. It serves as the foundation for launching other network resources.

2. **Subnet Configuration**:
   - Public and private subnets are created across multiple availability zones to distribute resources and enhance fault tolerance. They provide isolation and security for different types of workloads.

3. **Internet Gateway and Route Tables**:
   - An internet gateway is attached to the VPC to enable internet access, and route tables are configured to route traffic properly. This allows instances to communicate with the internet and other resources within the VPC.

4. **RDS Deployment**:
   - RDS instances are provisioned with PostgreSQL as the database engine, along with necessary security groups and subnet groups. This enables the storage and management of relational data with high availability and durability.

5. **SNS Topic**:
   - An SNS topic is created for sending notifications. It can be subscribed to by various services and endpoints to receive alerts and messages based on defined triggers.

6. **Lambda Function Deployment**:
   - Lambda functions are deployed with IAM roles and policies allowing access to DynamoDB, SES, CloudWatch, and other services. They provide scalable and event-driven compute resources for executing application logic.

7. **EC2 Instance Launch**:
   - EC2 instances are launched using launch templates, incorporating user data scripts for configuration. This allows for the deployment of virtual servers with customizable settings and bootstrapping actions.

8. **Load Balancer Setup**:
   - Elastic Load Balancer (ELB) is configured to distribute traffic to EC2 instances across availability zones. It ensures high availability and fault tolerance by evenly distributing incoming requests.

9. **Autoscaling Configuration**:
    - Autoscaling groups are defined to automatically adjust the number of EC2 instances based on CPU utilization. This helps maintain application performance and availability during traffic spikes and fluctuations.

10. **DNS Configuration**:
    - Route53 DNS records are set up to point to the load balancer for domain resolution. This allows users to access the application using a custom domain name.

## Conclusion

The Pulumi script orchestrates the deployment of a comprehensive infrastructure stack consisting of AWS and GCP resources. Each component is integrated to ensure seamless communication and operation within the infrastructure environment, providing a scalable, resilient, and secure platform for hosting applications.
