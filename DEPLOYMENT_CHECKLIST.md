# 🚀 Deployment Checklist - Backend Integration

Complete checklist for deploying Pet Roast AI Service and integrating with your Railway backend.

---

## Phase 1: AI Service Deployment (30 minutes)

### Step 1.1: Configure Environment
- [ ] Run `./setup_backend.sh` to create `.env` file
- [ ] Enter Revid.ai API key
- [ ] Enter backend webhook URL: `https://your-backend.railway.app/webhooks/pet-roast-complete`
- [ ] Enter backend CORS URL: `https://your-backend.railway.app`
- [ ] Verify `.env` file created successfully

### Step 1.2: Test Locally (Optional)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Start local server: `uvicorn app.main:app --reload --port 8000`
- [ ] Test health: `curl http://localhost:8000/healthz`
- [ ] Stop local server: `Ctrl+C`

### Step 1.3: Deploy to Railway
- [ ] Commit changes: `git add . && git commit -m "Configure backend integration"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Login to Railway: `railway login`
- [ ] Link project: `railway link` or create new: `railway init`
- [ ] Deploy: `railway up`
- [ ] Wait for deployment to complete (~3-5 minutes)

### Step 1.4: Add Redis Addon
- [ ] Go to Railway dashboard: https://railway.app
- [ ] Select your AI service project
- [ ] Click "New" → "Database" → "Redis"
- [ ] Wait for Redis to provision (~30 seconds)
- [ ] Verify `REDIS_URL` automatically set in environment variables

### Step 1.5: Set Environment Variables in Railway
- [ ] Go to project → Variables tab
- [ ] Verify these are set:
  - [ ] `REVID_API_KEY` = your_revid_api_key
  - [ ] `BACKEND_WEBHOOK_URL` = https://your-backend.railway.app/webhooks/pet-roast-complete
  - [ ] `CORS_ORIGINS` = ["https://your-backend.railway.app"]
  - [ ] `REDIS_URL` = (auto-set by Redis addon)
  - [ ] `USE_REDIS` = true
- [ ] Click "Deploy" to redeploy with new variables

### Step 1.6: Verify AI Service
- [ ] Get Railway URL from dashboard (e.g., `https://abc123.up.railway.app`)
- [ ] Test health: `curl https://your-ai-service.railway.app/healthz`
- [ ] Expected: `{"status":"ok"}`
- [ ] Test backend connection: `curl https://your-ai-service.railway.app/api/test-backend-connection`
- [ ] Expected: `{"status":"not_configured"}` or `{"status":"success"}`

**✅ AI Service Deployed!** Railway URL: ______________________________

---

## Phase 2: Backend Implementation (60 minutes)

### Step 2.1: Set Environment Variable
- [ ] In your backend Railway project, add:
  ```
  AI_SERVICE_URL=https://your-ai-service.railway.app
  ```
- [ ] Redeploy backend if needed

### Step 2.2: Implement Webhook Endpoint

#### Node.js/Express Example
- [ ] Create file: `src/controllers/webhookController.ts`
- [ ] Copy code from `BACKEND_INTEGRATION.md` (lines 180-260)
- [ ] Add route: `app.post('/webhooks/pet-roast-complete', webhookController.handleVideoComplete)`
- [ ] Test compilation: `npm run build`

#### NestJS Example
- [ ] Create controller: `nest g controller webhook`
- [ ] Copy code from `BACKEND_INTEGRATION.md` (lines 262-295)
- [ ] Add to module imports
- [ ] Test compilation: `npm run build`

### Step 2.3: Implement Video Generation Function

#### GraphQL Resolver
- [ ] Create/update resolver: `src/resolvers/petRoastResolver.ts`
- [ ] Copy code from `BACKEND_INTEGRATION.md` (lines 75-130)
- [ ] Add GraphQL schema:
  ```graphql
  type Mutation {
    generatePetRoast(input: GenerateRoastInput!): RoastJob!
  }
  ```
- [ ] Test GraphQL playground

#### REST API
- [ ] Create endpoint: `POST /api/pet-roasts`
- [ ] Copy code pattern from `BACKEND_INTEGRATION.md`
- [ ] Return job_id to client

### Step 2.4: Implement Notification Service
- [ ] Create/update: `src/services/notificationService.ts`
- [ ] Copy code from `BACKEND_INTEGRATION.md` (lines 297-350)
- [ ] Configure Firebase Admin SDK
- [ ] Test push notification sending

### Step 2.5: Database Schema
- [ ] Create table/collection: `roast_jobs`
- [ ] Fields:
  ```typescript
  {
    id: string (primary key)
    jobId: string (unique, from AI service)
    userId: string
    petId: string
    text: string
    imageUrl: string
    videoUrl?: string
    status: 'queued' | 'processing' | 'completed' | 'failed'
    error?: string
    createdAt: Date
    updatedAt: Date
  }
  ```
- [ ] Create indexes on: `jobId`, `userId`, `status`

### Step 2.6: Error Handling
- [ ] Handle "no pets detected" error (400)
  ```typescript
  if (error.response?.status === 400 &&
      error.response?.data?.detail?.error === 'no_pets_detected') {
    throw new Error('Please upload a clear photo of your pet');
  }
  ```
- [ ] Handle AI service timeout (502)
- [ ] Handle network errors
- [ ] Show user-friendly error messages

### Step 2.7: Deploy Backend
- [ ] Commit changes: `git add . && git commit -m "Add pet roast integration"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Railway auto-deploys (or manual: `railway up`)
- [ ] Wait for deployment (~2-3 minutes)
- [ ] Check logs: `railway logs --service backend`

**✅ Backend Updated!** Backend URL: ______________________________

---

## Phase 3: Testing Integration (20 minutes)

### Step 3.1: Manual Testing

#### Test Backend Webhook Endpoint
```bash
curl -X POST https://your-backend.railway.app/webhooks/pet-roast-complete \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test_manual",
    "status": "completed",
    "video_url": "https://example.com/test.mp4"
  }'
```
- [ ] Expected: `{"status":"success"}`
- [ ] Check backend logs for webhook received
- [ ] Verify database updated (if job exists)

#### Test AI Service → Backend Connection
```bash
curl https://your-ai-service.railway.app/api/test-backend-connection
```
- [ ] Expected: `{"status":"success", "backend_url":"...", "response_time_ms":...}`
- [ ] If "not_configured": Set `BACKEND_WEBHOOK_URL` in AI service
- [ ] If "failed": Check backend endpoint is accessible

#### Test Video Generation (with valid pet image)
```bash
curl -X POST https://your-ai-service.railway.app/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Roast my adorable lazy dog!",
    "image_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1"
  }'
```
- [ ] Expected: `{"job_id":"rev_...", "status":"queued"}`
- [ ] Note job_id: ______________________________

#### Check Video Status
```bash
curl https://your-ai-service.railway.app/api/video-status/{job_id}
```
- [ ] Poll every 5 seconds
- [ ] Status progression: queued → processing → completed
- [ ] Expected time: 30-90 seconds
- [ ] Check backend logs for webhook received
- [ ] Verify database updated with video_url

### Step 3.2: Automated Testing

#### Run Integration Test Suite
```bash
python test_integration.py \
  --ai-service-url https://your-ai-service.railway.app \
  --backend-url https://your-backend.railway.app \
  --test-image https://images.unsplash.com/photo-1543466835-00a7907e9de1
```

**Expected Results:**
- [ ] ✅ Health Check: PASSED
- [ ] ✅ Backend Connectivity: PASSED
- [ ] ✅ Generate Video: PASSED
- [ ] ✅ Video Status: PASSED
- [ ] ✅ Manual Webhook: PASSED
- [ ] **Results: 5/5 tests passed**

### Step 3.3: End-to-End Testing (Mobile App)

#### From Mobile App
- [ ] Login as test user
- [ ] Navigate to pet profile
- [ ] Take/upload pet photo
- [ ] Enter roast text
- [ ] Submit request
- [ ] User sees "Processing..." message
- [ ] Wait 60-90 seconds
- [ ] User receives push notification "Video Ready!"
- [ ] User taps notification
- [ ] Video plays successfully
- [ ] User can share video

#### Error Cases
- [ ] Upload image with no pets
  - Expected: "Please upload a clear photo of your pet"
- [ ] Network timeout
  - Expected: "Please try again later"
- [ ] Service unavailable
  - Expected: Graceful error message

**✅ Integration Tested!**

---

## Phase 4: Monitoring & Optimization (Ongoing)

### Step 4.1: Set Up Monitoring

#### Railway Monitoring
- [ ] Go to Railway dashboard
- [ ] Enable monitoring for AI service
- [ ] Enable monitoring for backend
- [ ] Set up alerts for:
  - [ ] High error rate (>5%)
  - [ ] Slow response time (>5s)
  - [ ] High memory usage (>80%)

#### Application Logging
- [ ] Check AI service logs: `railway logs --service ai-service`
- [ ] Check backend logs: `railway logs --service backend`
- [ ] Monitor for errors:
  - [ ] Webhook delivery failures
  - [ ] Pet detection failures
  - [ ] Video generation failures

### Step 4.2: Performance Metrics

Track these metrics:
- [ ] **Success Rate:** % of videos completed successfully
  - Target: >95%
- [ ] **Average Processing Time:** Time from request to completion
  - Target: <90 seconds
- [ ] **Webhook Delivery Rate:** % of webhooks delivered to backend
  - Target: >99%
- [ ] **Pet Detection Accuracy:** % of images with pets detected correctly
  - Target: >90%
- [ ] **API Response Time:** Average response time for endpoints
  - Target: <1 second

### Step 4.3: Optimization

If issues found:
- [ ] High webhook failure rate
  - Check `BACKEND_WEBHOOK_URL` is correct
  - Verify backend endpoint is accessible
  - Check network connectivity
- [ ] High pet detection failures
  - Review image quality requirements
  - Update user instructions
- [ ] Slow video generation
  - Check Revid.ai account limits
  - Consider upgrading plan

### Step 4.4: Scaling Considerations

For production load:
- [ ] **Redis:** Ensure sufficient memory for job storage
- [ ] **Workers:** Consider adding worker dynos for parallel processing
- [ ] **Rate Limiting:** Implement rate limits to prevent abuse
- [ ] **Caching:** Cache frequently accessed data
- [ ] **CDN:** Use CDN for video delivery

**✅ Monitoring Configured!**

---

## Phase 5: Production Readiness (Final Checks)

### Security
- [ ] Environment variables not committed to Git
- [ ] API keys stored securely in Railway
- [ ] CORS configured with specific origins (not "*")
- [ ] Webhook endpoint validates source
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints

### Documentation
- [ ] API documentation accessible to team
- [ ] Architecture diagram shared
- [ ] Runbook created for common issues
- [ ] On-call procedures documented

### Backup & Recovery
- [ ] Redis backup configured (Railway automatic)
- [ ] Database backup configured
- [ ] Rollback plan documented
- [ ] Disaster recovery tested

### User Experience
- [ ] Error messages user-friendly
- [ ] Loading states implemented
- [ ] Push notifications working
- [ ] Video playback smooth
- [ ] Share functionality working

### Legal & Compliance
- [ ] Terms of service updated
- [ ] Privacy policy updated
- [ ] User consent for video generation
- [ ] Content moderation plan

**✅ Production Ready!**

---

## 📊 Deployment Summary

| Component | Status | URL |
|-----------|--------|-----|
| AI Service | ⬜ | ________________________ |
| Backend | ⬜ | ________________________ |
| Redis | ⬜ | (Railway internal) |
| Integration Tests | ⬜ | N/A |
| Mobile App | ⬜ | (App Store/Play Store) |

### Completion Progress

- [ ] Phase 1: AI Service Deployment (6 steps)
- [ ] Phase 2: Backend Implementation (7 steps)
- [ ] Phase 3: Testing Integration (3 steps)
- [ ] Phase 4: Monitoring & Optimization (4 steps)
- [ ] Phase 5: Production Readiness (4 steps)

**Total Steps:** 24
**Completed:** ___ / 24

---

## 🆘 Troubleshooting Guide

### Issue: AI Service Health Check Fails
**Symptoms:** `curl healthz` returns error
**Solutions:**
1. Check Railway logs: `railway logs --service ai-service`
2. Verify deployment completed: Railway dashboard
3. Check environment variables set correctly
4. Restart service: Railway dashboard → Restart

### Issue: Backend Connection Test Fails
**Symptoms:** `/api/test-backend-connection` returns "failed"
**Solutions:**
1. Verify `BACKEND_WEBHOOK_URL` is correct
2. Test backend endpoint directly: `curl {backend}/webhooks/pet-roast-complete`
3. Check CORS settings in backend
4. Check firewall/network rules

### Issue: No Pets Detected
**Symptoms:** Generate video returns 400 error
**Solutions:**
1. Use test image: `https://images.unsplash.com/photo-1543466835-00a7907e9de1`
2. Ensure image contains clear, visible pets
3. Check supported pets list in API_REFERENCE.md
4. Try different image

### Issue: Webhook Not Received
**Symptoms:** Video completes but backend not updated
**Solutions:**
1. Check AI service logs for webhook attempts
2. Verify backend endpoint exists and returns 200
3. Check `BACKEND_WEBHOOK_URL` environment variable
4. Test webhook manually with curl
5. Check backend logs for errors

### Issue: Video Generation Timeout
**Symptoms:** Video status stays "processing" forever
**Solutions:**
1. Check Revid.ai account status
2. Verify `REVID_API_KEY` is valid
3. Check Revid.ai rate limits
4. Poll video status instead of waiting
5. Contact Revid.ai support

---

## 📞 Support Contacts

| Service | Contact | Documentation |
|---------|---------|---------------|
| AI Service | Your team | BACKEND_INTEGRATION.md |
| Backend | Your team | Backend repo |
| Railway | support@railway.app | railway.app/help |
| Revid.ai | support@revid.ai | revid.ai/docs |

---

## ✅ Final Sign-Off

### Deployment Team
- [ ] AI Service Deployed: ________________ (Name, Date)
- [ ] Backend Updated: ________________ (Name, Date)
- [ ] Integration Tested: ________________ (Name, Date)
- [ ] Monitoring Configured: ________________ (Name, Date)
- [ ] Production Approved: ________________ (Name, Date)

### Stakeholder Approval
- [ ] Technical Lead: ________________
- [ ] Product Manager: ________________
- [ ] QA Lead: ________________

**Deployment Date:** ________________
**Go-Live Time:** ________________
**Status:** ⬜ Ready for Production

---

**Need Help?** Review:
- [QUICK_START_BACKEND.md](QUICK_START_BACKEND.md) - Quick reference
- [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) - Detailed guide
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - What we built

**Good luck with your deployment! 🚀**
