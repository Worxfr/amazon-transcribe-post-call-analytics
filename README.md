# Amazon Transcribe Post Call Analytics (PCA) - Deployment Guide

This guide walks you through deploying a new instance of the Post Call Analytics solution with Dutch language support and custom NLP processing.

## Prerequisites

Before deploying, ensure you have:

1. **AWS CLI configured** with appropriate permissions
2. **Amazon QuickSight enabled** in your AWS account (required for dashboards)
3. **Amazon Bedrock model access** - Request access to Claude 3 Haiku in the Bedrock console
4. **Dutch NLP API endpoint** (if using custom Dutch processing)

## Step 1: Package and Upload to S3

First, create a private S3 bucket and package the CloudFormation template:

```bash
# Run the publish script to create bucket and upload artifacts
./publish.sh
```

This script will:
- Create a private S3 bucket for deployment artifacts
- Package the CloudFormation template with all dependencies
- Upload the packaged template to S3
- Generate a `build/packaged.template` file ready for deployment

## Step 2: Deploy the Stack

Deploy the PCA stack using the packaged template:

```bash
aws cloudformation deploy \
  --template-file /path/to/your/project/build/packaged.template \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  --stack-name PCA-20250107 \
  --region eu-west-1 \
  --parameter-overrides \
    AdminEmail=your-email@domain.com \
    EnablePcaDashboards='Yes' \
    GlueDatabaseName=pca-analytics-database \
    EnableDutchNLP=true \
    DutchNLPApiEndpoint=https://your-dutch-nlp-api.execute-api.region.amazonaws.com/dev \
    TranscribeLanguages=nl-NL \
    DefaultTranscribeLanguage=nl-NL \
    CallSummarization=BEDROCK \
    SummarizationBedrockModelId=anthropic.claude-3-haiku-20240307-v1:0 \
    GenAIQueryBedrockModelId=anthropic.claude-3-haiku-20240307-v1:0
```

### Key Parameters Explained

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `AdminEmail` | Email for admin user notifications | `admin@company.com` |
| `EnablePcaDashboards` | Enable QuickSight dashboards | `'Yes'` or `'No'` |
| `GlueDatabaseName` | Database name for analytics (required if dashboards enabled) | `pca-analytics-database` |
| `EnableDutchNLP` | Enable custom Dutch NLP processing | `true` or `false` |
| `DutchNLPApiEndpoint` | Your Dutch NLP API endpoint URL | `https://api.amazonaws.com/dev` |
| `TranscribeLanguages` | Language for transcription | `nl-NL` (Dutch) or `en-US` |
| `DefaultTranscribeLanguage` | Default transcription language | `nl-NL` |
| `CallSummarization` | Summarization method | `BEDROCK` |
| `SummarizationBedrockModelId` | Bedrock model for summarization | `anthropic.claude-3-haiku-20240307-v1:0` |
| `GenAIQueryBedrockModelId` | Bedrock model for GenAI queries | `anthropic.claude-3-haiku-20240307-v1:0` |

## Step 3: Monitor Deployment

Monitor the deployment progress:

```bash
# Watch stack events
aws cloudformation describe-stack-events --stack-name PCA-20250107 --region eu-west-1

# Check stack status
aws cloudformation describe-stacks --stack-name PCA-20250107 --region eu-west-1 --query 'Stacks[0].StackStatus'
```

Deployment typically takes 15-20 minutes.

## Step 4: Post-Deployment Configuration

After successful deployment:

1. **Check your email** for temporary admin credentials
2. **Access the PCA UI** using the CloudFormation stack outputs
3. **Configure QuickSight** (if dashboards enabled):
   - Grant S3 access to the PCA output bucket
   - Share dashboard assets as needed

## Regional Considerations

- **QuickSight Region**: Deploy in the same region where QuickSight is configured
- **Bedrock Models**: Ensure your chosen models are available in the deployment region
- **Cross-Region APIs**: Dutch NLP API can be in a different region than the main deployment

## Troubleshooting Common Issues

### ValidationError: Parameters must have values
- Ensure all required parameters are provided
- Use quoted values for boolean-like parameters: `'Yes'`/`'No'`

### Bedrock Model Not Available
- Check model availability in your region: `aws bedrock list-foundation-models --region your-region`
- Request model access in the Bedrock console if needed

### QuickSight Region Mismatch
- Deploy PCA in the same region where QuickSight is configured
- Or set up QuickSight in your preferred deployment region

## Clean Up

To remove the deployment:

```bash
aws cloudformation delete-stack --stack-name PCA-20250107 --region eu-west-1
```

## Support

For detailed technical information, see [OLDREADME.md](./OLDREADME.md).

For issues or questions, refer to the AWS documentation or contact your AWS support team.
