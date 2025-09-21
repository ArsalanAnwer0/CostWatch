# Data sources for current AWS info
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# EKS Cluster Service Role
resource "aws_iam_role" "eks_cluster_role" {
  name = "${var.project_name}-eks-cluster-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-eks-cluster-role-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Attach required policies to EKS cluster role
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

# EKS Node Group Service Role
resource "aws_iam_role" "eks_node_role" {
  name = "${var.project_name}-eks-node-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-eks-node-role-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Attach required policies to EKS node role
resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_role.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_role.name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_role.name
}

# Additional policy for EBS CSI driver
resource "aws_iam_role_policy_attachment" "eks_ebs_csi_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
  role       = aws_iam_role.eks_node_role.name
}

# CostWatch application service role for AWS Cost Explorer access
resource "aws_iam_role" "costwatch_app_role" {
  name = "${var.project_name}-app-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-app-role-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Custom policy for CostWatch application
resource "aws_iam_policy" "costwatch_app_policy" {
  name        = "${var.project_name}-app-policy-${var.environment}"
  description = "Policy for CostWatch application to access AWS services"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          # Cost Explorer permissions
          "ce:GetCostAndUsage",
          "ce:GetDimensionValues",
          "ce:GetReservationCoverage",
          "ce:GetReservationPurchaseRecommendation",
          "ce:GetReservationUtilization",
          "ce:GetUsageReport",
          "ce:DescribeCostCategoryDefinition",
          "ce:GetCostCategories",
          # CloudWatch permissions for monitoring
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:PutMetricData",
          # EC2 permissions for resource scanning
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "ec2:DescribeSnapshots",
          "ec2:DescribeImages",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeVpcs",
          "ec2:DescribeSubnets",
          # RDS permissions
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:DescribeDBSnapshots",
          # S3 permissions
          "s3:ListAllMyBuckets",
          "s3:GetBucketLocation",
          "s3:GetBucketTagging",
          "s3:GetBucketVersioning",
          # SNS permissions for alerts
          "sns:Publish",
          "sns:CreateTopic",
          "sns:Subscribe",
          "sns:ListTopics",
          # STS permissions
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-app-policy-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Attach custom policy to application role
resource "aws_iam_role_policy_attachment" "costwatch_app_policy_attachment" {
  policy_arn = aws_iam_policy.costwatch_app_policy.arn
  role       = aws_iam_role.costwatch_app_role.name
}

# Instance profile for EC2 instances (if needed)
resource "aws_iam_instance_profile" "costwatch_app_profile" {
  name = "${var.project_name}-app-profile-${var.environment}"
  role = aws_iam_role.costwatch_app_role.name

  tags = {
    Name        = "${var.project_name}-app-profile-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}