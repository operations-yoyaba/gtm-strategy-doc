# GTM Strategy Document Generator - Setup Complete! 🎉

## What We've Built

✅ **Webhook-based GTM strategy document generation system**
- Combines job submission and webhook handling in a single FastAPI app
- Uses OpenAI's background processing with webhooks
- Token counting and cost tracking
- Google Docs integration (when credentials available)

✅ **Cloud Run Service Deployed**
- **Service URL**: https://gtm-strategy-doc-262886408793.us-central1.run.app
- **Service Name**: gtm-strategy-doc
- **Region**: us-central1
- **Status**: ✅ Running and healthy

✅ **GitHub Repository**
- **Repository**: https://github.com/operations-yoyaba/gtm-strategy-doc
- **GitHub Actions**: Configured for automatic deployment
- **Service Account**: Created and configured

## API Endpoints

Your Cloud Run service provides these endpoints:

- **Root**: `GET /` - API information
- **Health**: `GET /health` - Service health check
- **Submit Job**: `POST /generate` - Submit background research job
- **Webhook**: `POST /webhook/openai` - OpenAI webhook handler
- **Job Status**: `GET /job-status/{response_id}` - Check job status

## Next Steps

### 1. Add GitHub Secrets (Required)

You need to add these secrets to your GitHub repository:

```bash
# Add OpenAI API key
gh secret set OPENAI_API_KEY

# Add OpenAI webhook secret (get this from OpenAI dashboard)
gh secret set OPENAI_WEBHOOK_SECRET

# Add Google Docs template ID (optional)
gh secret set GS_TEMPLATE_DOC_ID

# Add Google Drive folder ID (optional)
gh secret set GS_DRIVE_FOLDER_ID
```

### 2. Configure OpenAI Webhook

1. Go to [OpenAI Webhook Settings](https://platform.openai.com/settings/project/webhooks)
2. Click "Create" to add a new webhook endpoint
3. Configure:
   - **Name**: GTM Strategy Doc Generator
   - **URL**: `https://gtm-strategy-doc-262886408793.us-central1.run.app/webhook/openai`
   - **Events**: Select `response.completed`
4. Save the webhook secret and add it to GitHub secrets

### 3. Test the System

Once you've added the secrets, you can test the system:

```bash
# Test job submission
curl -X POST https://gtm-strategy-doc-262886408793.us-central1.run.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "companyId": 12345,
    "stageTs": "2024-01-15T10:30:00Z",
    "company": {
      "name": "Test Company",
      "industry": "Software",
      "numberofemployees": 100,
      "annualrevenue": "10000000"
    },
    "enriched_data": {}
  }'
```

## Architecture Overview

```
HubSpot → Your API → OpenAI (background) → Webhook → Google Docs
```

1. **Job Submission**: HubSpot triggers your `/generate` endpoint
2. **Background Processing**: OpenAI processes the research in the background
3. **Webhook Notification**: OpenAI calls your `/webhook/openai` endpoint when done
4. **Document Creation**: Your webhook handler creates Google Docs

## Key Benefits

- ✅ **No server timeouts**: Submit jobs and shut down compute
- ✅ **Scalable**: Handle many concurrent jobs
- ✅ **Reliable**: OpenAI retries delivery if needed
- ✅ **Cost efficient**: Only pay for compute when processing results
- ✅ **Token tracking**: Monitor usage and costs

## Service Account Details

- **Service Account**: `gtm-strategy-doc-sa@yoyaba-db.iam.gserviceaccount.com`
- **Key File**: `gtm-strategy-doc-sa-key.json` (already added to GitHub secrets)
- **Permissions**: Cloud Run Admin, Storage Admin

## Monitoring

- **Cloud Run Console**: https://console.cloud.google.com/run/detail/us-central1/gtm-strategy-doc
- **GitHub Actions**: https://github.com/operations-yoyaba/gtm-strategy-doc/actions
- **Logs**: Available in Cloud Run console

## Troubleshooting

If you encounter issues:

1. **Check Cloud Run logs** in the Google Cloud Console
2. **Verify GitHub secrets** are set correctly
3. **Test webhook endpoint** with OpenAI's test tools
4. **Check service account permissions** if Google Docs integration fails

---

**Your webhook endpoint for OpenAI configuration:**
`https://gtm-strategy-doc-262886408793.us-central1.run.app/webhook/openai`

**Ready to use! 🚀** 