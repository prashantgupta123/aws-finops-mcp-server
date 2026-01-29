# AWS FinOps MCP Server - Bedrock AgentCore Deployment Summary

## 📦 What We've Created

This deployment package enables you to run the AWS FinOps MCP Server on Amazon Bedrock AgentCore with two deployment methods.

## 📄 New Files Created

### 1. **BEDROCK_AGENTCORE_DEPLOYMENT.md**
Complete step-by-step deployment guide covering:
- Prerequisites and IAM setup
- Gateway (Lambda) deployment method
- Runtime (Container) deployment method
- Testing procedures
- Monitoring and observability
- Troubleshooting guide

**Use this for**: Detailed deployment instructions

### 2. **AGENTCORE_QUICKSTART.md**
Quick start guide for rapid deployment:
- One-command automated deployment
- 5-minute Gateway setup
- 10-minute Runtime setup
- MCP client configuration examples
- Quick testing procedures
- Common use cases

**Use this for**: Getting started quickly

### 3. **AGENTCORE_COMPARISON.md**
Comprehensive comparison of deployment methods:
- Decision matrix
- Detailed pros/cons
- Cost analysis and break-even points
- Performance comparison
- Use case recommendations
- Migration strategies

**Use this for**: Choosing the right deployment method

### 4. **deploy-to-agentcore.sh**
Automated deployment script:
- Interactive menu for method selection
- Automated Gateway deployment
- Automated Runtime deployment
- Prerequisites checking
- Error handling

**Use this for**: Automated deployment

## 🚀 Deployment Methods

### Method 1: Gateway (Lambda-based)

**Architecture:**
```
AI Agent → AgentCore Gateway → Lambda Function → AWS APIs
```

**Best For:**
- Quick testing and POC
- Budget-conscious deployments
- Simple tool exposure
- < 50,000 invocations/month
- Operations < 15 minutes

**Cost:** ~$10-20/month for typical usage

**Setup Time:** 5 minutes

**Command:**
```bash
./deploy-to-agentcore.sh
# Choose option 1
```

### Method 2: Runtime (Containerized)

**Architecture:**
```
AI Agent → AgentCore Runtime → Docker Container → AWS APIs
```

**Best For:**
- Production workloads
- Long-running operations (>15 min)
- Complex workflows
- > 100,000 invocations/month
- Stateful operations

**Cost:** ~$83+/month

**Setup Time:** 10 minutes

**Command:**
```bash
./deploy-to-agentcore.sh
# Choose option 2
```

## 📊 Key Features

### Both Methods Support:
- ✅ All 76 FinOps tools
- ✅ Category filtering
- ✅ OAuth authentication
- ✅ CloudWatch monitoring
- ✅ CloudTrail auditing
- ✅ IAM role-based access
- ✅ Multi-region support
- ✅ MCP protocol compliance

### Gateway-Specific:
- ✅ Serverless (no infrastructure management)
- ✅ Automatic scaling
- ✅ Pay-per-use pricing
- ✅ Lambda free tier eligible
- ✅ Instant updates

### Runtime-Specific:
- ✅ Unlimited execution time
- ✅ Full control over environment
- ✅ Stateful operations
- ✅ Custom dependencies
- ✅ Better for high-volume

## 🎯 Quick Start

### Option 1: Automated Deployment

```bash
# Clone repository
git clone <your-repo-url>
cd aws-finops-mcp-server

# Run automated deployment
./deploy-to-agentcore.sh
```

### Option 2: Manual Deployment

**Gateway Method:**
```bash
# See AGENTCORE_QUICKSTART.md section "Method 1"
# Takes 5 minutes
```

**Runtime Method:**
```bash
# See AGENTCORE_QUICKSTART.md section "Method 2"
# Takes 10 minutes
```

## 📖 Documentation Structure

```
aws-finops-mcp-server/
├── AGENTCORE_QUICKSTART.md          # Start here for quick deployment
├── BEDROCK_AGENTCORE_DEPLOYMENT.md  # Complete deployment guide
├── AGENTCORE_COMPARISON.md          # Choose deployment method
├── deploy-to-agentcore.sh           # Automated deployment script
├── README.md                        # Updated with AgentCore info
└── [existing files...]
```

## 🔧 Configuration Examples

### For Kiro

```json
{
  "mcpServers": {
    "aws-finops-agentcore": {
      "command": "mcp-client",
      "args": ["--url", "https://your-deployment-url.amazonaws.com"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### For Cursor

```json
{
  "mcp": {
    "servers": {
      "aws-finops-agentcore": {
        "url": "https://your-deployment-url.amazonaws.com"
      }
    }
  }
}
```

## 🧪 Testing

### Health Check
```bash
curl https://your-deployment-url.amazonaws.com/health
```

### List Tools
```bash
curl -X POST https://your-deployment-url.amazonaws.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

### Execute Tool
```bash
curl -X POST https://your-deployment-url.amazonaws.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "find_unused_lambda_functions",
      "arguments": {"region_name": "us-east-1", "period": 90}
    }
  }'
```

## 💰 Cost Estimates

### Gateway (Lambda) Method

**Low Volume** (1,000 invocations/month):
- Lambda: ~$0.02
- Gateway: ~$1.00
- **Total: ~$1.02/month**

**Medium Volume** (10,000 invocations/month):
- Lambda: ~$0.17
- Gateway: ~$10.00
- **Total: ~$10.17/month**

**High Volume** (100,000 invocations/month):
- Lambda: ~$1.70
- Gateway: ~$100.00
- **Total: ~$101.70/month**

### Runtime (Container) Method

**Any Volume**:
- Container (24/7): ~$73.00
- Gateway: Based on invocations
- **Total: ~$83+ /month**

**Break-even point**: ~80,000 invocations/month

## 🔐 Security Features

### Authentication
- OAuth 2.0 with Amazon Cognito
- IAM role-based access
- API key support
- SigV4 signing

### Monitoring
- CloudWatch Logs
- CloudWatch Metrics
- CloudTrail audit logs
- Custom dashboards

### Compliance
- VPC support
- Encryption at rest
- Encryption in transit
- IAM policies

## 📈 Scaling

### Gateway (Lambda)
- Automatic scaling to 1000 concurrent executions
- Burst capacity available
- No configuration needed

### Runtime (Container)
- Configurable container size
- Auto-scaling support
- Multi-region deployment
- Load balancing

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied**
   - Check IAM policies
   - Verify role trust relationships
   - See BEDROCK_AGENTCORE_DEPLOYMENT.md

2. **Tools Not Found**
   - Synchronize gateway targets
   - Check tool registration
   - Verify MCP protocol version

3. **Container Fails**
   - Check Docker logs
   - Verify environment variables
   - Test locally first

4. **High Costs**
   - Review invocation patterns
   - Consider switching methods
   - Use category filtering

## 🎓 Learning Path

### Day 1: Quick Start
1. Read AGENTCORE_QUICKSTART.md
2. Run `./deploy-to-agentcore.sh`
3. Test with health check
4. Try a few tools

### Day 2: Deep Dive
1. Read BEDROCK_AGENTCORE_DEPLOYMENT.md
2. Understand architecture
3. Configure authentication
4. Set up monitoring

### Day 3: Optimization
1. Read AGENTCORE_COMPARISON.md
2. Analyze costs
3. Optimize configuration
4. Plan production deployment

### Week 2: Production
1. Deploy to production
2. Set up CI/CD
3. Configure alerts
4. Document procedures

## 🔄 Migration Path

### From Local to AgentCore

**Current Setup:**
```bash
# Local MCP server
python -m aws_finops_mcp
```

**Migrate to Gateway:**
```bash
# Deploy to AgentCore Gateway
./deploy-to-agentcore.sh
# Choose option 1
```

**Migrate to Runtime:**
```bash
# Deploy to AgentCore Runtime
./deploy-to-agentcore.sh
# Choose option 2
```

**No code changes required!**

## 📚 Additional Resources

### AWS Documentation
- [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AgentCore Gateway Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [AgentCore Runtime Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html)

### MCP Protocol
- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)

### Project Documentation
- [Main README](./README.md)
- [Tools Reference](./TOOLS_REFERENCE.md)
- [IAM Setup Guide](./IAM_SETUP_GUIDE.md)

## 🎉 Success Criteria

After deployment, you should be able to:

✅ Access the MCP server via AgentCore URL
✅ List all available tools
✅ Execute tools successfully
✅ View logs in CloudWatch
✅ Monitor metrics
✅ Authenticate users
✅ Scale automatically
✅ Optimize costs

## 🆘 Getting Help

### Documentation
1. Start with AGENTCORE_QUICKSTART.md
2. Refer to BEDROCK_AGENTCORE_DEPLOYMENT.md for details
3. Check AGENTCORE_COMPARISON.md for decisions

### Troubleshooting
1. Check CloudWatch Logs
2. Review IAM permissions
3. Test locally first
4. See troubleshooting section in deployment guide

### Support
- Open an issue in the repository
- Check AWS documentation
- Review CloudTrail logs
- Contact AWS Support

## 🚀 Next Steps

1. **Choose Deployment Method**
   - Read AGENTCORE_COMPARISON.md
   - Consider your requirements
   - Make a decision

2. **Deploy**
   - Run `./deploy-to-agentcore.sh`
   - Or follow manual steps
   - Test the deployment

3. **Configure**
   - Set up authentication
   - Configure monitoring
   - Optimize settings

4. **Use**
   - Connect your AI assistant
   - Start using tools
   - Monitor usage

5. **Optimize**
   - Review costs
   - Adjust configuration
   - Scale as needed

## 📝 Summary

You now have everything needed to deploy the AWS FinOps MCP Server on Amazon Bedrock AgentCore:

- ✅ Complete deployment guides
- ✅ Automated deployment script
- ✅ Comparison and decision tools
- ✅ Testing procedures
- ✅ Monitoring setup
- ✅ Troubleshooting guides

**Ready to deploy?** Run `./deploy-to-agentcore.sh` and get started! 🎯
