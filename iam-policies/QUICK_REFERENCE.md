# IAM Policies - Quick Reference

## 🚀 Quick Setup (30 seconds)

```bash
cd iam-policies/examples
./create-iam-role.sh finops-mcp-role full ec2
```

---

## 📋 Available Policies

| File | Use Case | Tools |
|------|----------|-------|
| `finops-full-policy.json` | Production | 24 |
| `finops-minimal-policy.json` | Testing | 24 |
| `finops-readonly-policy.json` | Security | 24 |
| `finops-cost-only-policy.json` | Cost Analysis | 9 |

---

## 🎯 Common Scenarios

### EC2 Deployment
```bash
./create-iam-role.sh finops-mcp-role full ec2
```

### ECS Deployment
```bash
./create-iam-role.sh finops-mcp-role full ecs
```

### Lambda Deployment
```bash
./create-iam-role.sh finops-mcp-role full lambda
```

### Local Development
```bash
./create-iam-user.sh finops-mcp-user full
```

---

## 🔧 Manual Setup

### AWS Console
1. IAM → Policies → Create Policy
2. JSON tab → Paste policy
3. Create → Attach to role/user

### AWS CLI
```bash
# Create policy
aws iam create-policy \
  --policy-name FinOpsFullPolicy \
  --policy-document file://finops-full-policy.json

# Create role
aws iam create-role \
  --role-name finops-mcp-role \
  --assume-role-policy-document file://trust-policies/ec2-trust-policy.json

# Attach
aws iam attach-role-policy \
  --role-name finops-mcp-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/FinOpsFullPolicy
```

---

## 🧪 Test Permissions

```bash
# Test EC2
aws ec2 describe-instances

# Test Cost Explorer
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost

# Test Cost Optimization Hub
aws cost-optimization-hub list-recommendations
```

---

## 📚 Documentation

- **Complete Guide**: [README.md](README.md)
- **Setup Guide**: [../IAM_SETUP_GUIDE.md](../IAM_SETUP_GUIDE.md)
- **Examples**: `examples/` directory

---

## 🔒 Security Tips

1. ✅ Use IAM roles (not users)
2. ✅ Enable CloudTrail
3. ✅ Use external ID for cross-account
4. ✅ Rotate credentials regularly
5. ✅ Start with minimal policy

---

**Need Help?** See [IAM_SETUP_GUIDE.md](../IAM_SETUP_GUIDE.md)
