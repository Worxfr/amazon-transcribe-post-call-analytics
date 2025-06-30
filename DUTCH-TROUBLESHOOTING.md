# Dutch PCA Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Step Functions Errors

#### Parameter Validation Failed
**Error**: `Parameter validation failed: Unknown parameter in Settings: "LanguageCode"`

**Cause**: AWS Transcribe Standard API parameter placement issue

**Solution**: ✅ **FIXED** - Parameters correctly placed at top level in `pca-aws-sf-start-transcribe-job.py`

**Verification**:
```bash
aws logs filter-log-events --region eu-west-1 \
  --log-group-name "/aws/lambda/*SFStartTranscribeJob*" \
  --filter-pattern "Configured Standard Transcribe API for Dutch language"
```

#### Content Redaction Not Supported
**Error**: `Content redaction isn't supported in this language`

**Cause**: AWS Transcribe doesn't support PII redaction for Dutch

**Solution**: ✅ **FIXED** - Content redaction automatically disabled for Dutch

**Verification**: Look for log message: `"Content redaction disabled for Dutch language"`

### 2. Sentiment Analysis Issues

#### Flat Sentiment Scores (All 0.0)
**Symptom**: Frontend shows all sentiment scores as 0.0

**Cause**: Dutch NLP API scores (0.0-1.0) below PCA thresholds (2.0)

**Solution**: ✅ **FIXED** - 5x sentiment scaling applied

**Verification**: Check processed JSON for non-zero sentiment scores:
```json
{
  "SentimentIsPositive": 1,
  "SentimentScore": 4.0,
  "BaseSentimentScores": {"Positive": 4.0, "Negative": 0.5}
}
```

#### Dutch NLP API Not Called
**Symptom**: System uses English processing instead of Dutch NLP API

**Cause**: Language detection not setting correct language code

**Solution**: ✅ **FIXED** - Special handling for `nl-NL` in turn-by-turn processor

**Verification**: Look for log messages:
- `"Set language code to 'nl' for Dutch NLP API processing"`
- `"Using Dutch NLP API for language: nl"`

### 3. Lambda Function Errors

#### HTTP Client Import Error
**Error**: `ImportError: No module named 'requests'`

**Cause**: `requests` library not available in Lambda runtime

**Solution**: ✅ **FIXED** - Replaced with `urllib3` in Dutch NLP integration

**Verification**: No import errors in Lambda logs

#### Dutch NLP API Connection Issues
**Error**: HTTP connection timeouts or 500 errors

**Troubleshooting Steps**:
1. Verify Dutch NLP API endpoint is accessible
2. Check API Gateway logs for your Dutch NLP API
3. Verify API endpoints match expected format:
   - `/sentiment`
   - `/entities` 
   - `/key-phrases`
   - `/analyze`

### 4. Configuration Issues

#### Environment Variables Not Set
**Check Lambda Environment Variables**:
```bash
aws lambda get-function-configuration \
  --function-name "YourStack-SFProcessTurn-*" \
  --query 'Environment.Variables'
```

**Expected Variables**:
```json
{
  "DUTCH_NLP_API_ENDPOINT": "https://your-dutch-nlp-api.execute-api.region.amazonaws.com/stage",
  "ENABLE_DUTCH_NLP": "true",
  "DEFAULT_TRANSCRIBE_LANGUAGE": "nl-NL"
}
```

#### CloudFormation Parameters
**Check Stack Parameters**:
```bash
aws cloudformation describe-stacks \
  --stack-name YourStack-Name \
  --query 'Stacks[0].Parameters'
```

## 🔍 Debugging Commands

### Check Recent Processing
```bash
# Check for Dutch audio processing
aws s3 ls s3://your-pca-output-bucket/parsedFiles/ \
  --recursive | grep "$(date +%Y-%m-%d)"

# Check Lambda logs for Dutch processing
aws logs filter-log-events --region your-region \
  --log-group-name "/aws/lambda/*SFProcessTurn*" \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "Dutch"
```

### Test Dutch NLP API Directly
```bash
# Replace with your actual Dutch NLP API endpoint
curl -X POST 'https://your-dutch-nlp-api.execute-api.region.amazonaws.com/stage/sentiment' \
  -H 'Content-Type: application/json' \
  -d '{"text": "Dit is een geweldige service!"}'
```

### Verify Transcribe Job Success
```bash
aws transcribe list-transcription-jobs \
  --status COMPLETED \
  --max-results 5 \
  --query 'TranscriptionJobSummaries[?LanguageCode==`nl-NL`]'
```

## 📊 Success Indicators

### Healthy Dutch Processing Shows:
1. ✅ Transcribe jobs complete with `LanguageCode: "nl-NL"`
2. ✅ Lambda logs show `"Using Dutch NLP API for language: nl"`
3. ✅ Processed JSON contains non-zero sentiment scores
4. ✅ Dutch entities and summaries present in output
5. ✅ Frontend dashboard displays sentiment visualization

### Performance Benchmarks:
- **Transcribe Job**: ~20-30 seconds for 2-minute audio
- **Turn-by-Turn Processing**: ~90-120 seconds for 2-minute audio
- **Dutch NLP API Calls**: Multiple calls per speech segment
- **Total Processing**: ~2-3 minutes for 2-minute audio

## 🆘 Getting Help

If issues persist after checking this guide:

1. **Check CloudWatch Logs** for specific error messages
2. **Verify Dutch NLP API** is responding correctly
3. **Test with Sample Audio** to isolate issues
4. **Review CloudFormation Stack** parameters and status
5. **Check S3 Bucket Permissions** for input/output access

---

**Most common issues have been resolved in the current implementation. This guide covers legacy troubleshooting for reference.**
