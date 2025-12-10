# 🔗 Backend Integration Guide

Complete guide for integrating the Pet Roast AI Service with your Railway backend.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [API Endpoints](#api-endpoints)
- [Backend Implementation](#backend-implementation)
- [Environment Configuration](#environment-configuration)
- [Error Handling](#error-handling)
- [Testing Integration](#testing-integration)

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│  Mobile App / Frontend                                      │
└─────────────────────┬──────────────────────────────────────┘
                      │ GraphQL
                      ▼
┌────────────────────────────────────────────────────────────┐
│  Backend (Node.js + GraphQL)                               │
│  Railway: https://your-backend.railway.app                 │
│                                                             │
│  ✓ Receives video generation requests                      │
│  ✓ Calls AI Service REST API                               │
│  ✓ Stores job_id in database                               │
│  ✓ Receives webhook when video ready                       │
│  ✓ Notifies user via push notification                     │
└──────┬─────────────────────────────────────────────────────┘
       │
       │ REST API
       ▼
┌────────────────────────────────────────────────────────────┐
│  AI Service (FastAPI + Python)                             │
│  Railway: https://your-ai-service.up.railway.app           │
│                                                             │
│  ✓ Validates pet presence (YOLOv5)                         │
│  ✓ Processes text (AI4Bharat translation)                  │
│  ✓ Generates video (Revid.ai)                              │
│  ✓ Stores job status (Redis)                               │
│  ✓ Webhooks backend when complete                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 API Endpoints

### 1. Generate Video (Backend → AI Service)

**Endpoint:** `POST https://your-ai-service.up.railway.app/api/generate-video`

**Request:**
```typescript
interface GenerateVideoRequest {
  text: string;           // Roast text (any language)
  image_url: string;      // Pet image URL (must be publicly accessible)
}
```

**Response (202 Accepted):**
```typescript
interface GenerateVideoResponse {
  job_id: string;         // Track this job ID
  status: "queued" | "processing";
}
```

**Error Response (400 - No Pets):**
```typescript
interface NoPetsError {
  detail: {
    error: "no_pets_detected";
    message: "No pets found in the uploaded image...";
    suggestion: "Try uploading a clear photo or video of your pet.";
  }
}
```

**Error Response (502 - Service Error):**
```typescript
interface ServiceError {
  detail: string;         // Error message from AI4Bharat or Revid
}
```

---

### 2. Check Video Status (Backend → AI Service)

**Endpoint:** `GET https://your-ai-service.up.railway.app/api/video-status/{job_id}`

**Response:**
```typescript
interface VideoStatusResponse {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  detail?: string;        // Error message if failed
  updated_at?: string;    // ISO 8601 timestamp
  video_url?: string;     // Only present when status is "completed"
}
```

---

### 3. Video Completion Webhook (AI Service → Backend)

**Endpoint:** `POST https://your-backend.railway.app/webhooks/pet-roast-complete`

**Request (from AI Service):**
```typescript
interface VideoCompleteWebhook {
  job_id: string;
  status: "completed" | "failed";
  video_url?: string;     // Only present if status is "completed"
  error?: string;         // Only present if status is "failed"
}
```

**Expected Response:**
```typescript
interface WebhookAck {
  status: "success";
  message: string;
}
```

---

## 💻 Backend Implementation

### 1. GraphQL Mutation (Generate Video)

```typescript
// types/pet-roast.ts
export interface GenerateRoastInput {
  petId: string;
  text: string;
  imageUrl: string;
}

export interface RoastJob {
  id: string;
  jobId: string;          // AI service job_id
  petId: string;
  text: string;
  imageUrl: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  videoUrl?: string;
  error?: string;
  createdAt: Date;
  updatedAt: Date;
}
```

```typescript
// resolvers/pet-roast.resolver.ts
import { Resolver, Mutation, Args, Query } from '@nestjs/graphql';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

@Resolver()
export class PetRoastResolver {
  private readonly AI_SERVICE_URL = process.env.AI_SERVICE_URL;

  constructor(
    private readonly httpService: HttpService,
    private readonly roastJobRepository: RoastJobRepository,
    private readonly notificationService: NotificationService,
  ) {}

  @Mutation(() => RoastJob)
  async generatePetRoast(
    @Args('input') input: GenerateRoastInput,
  ): Promise<RoastJob> {
    try {
      // Call AI service to generate video
      const response = await firstValueFrom(
        this.httpService.post(`${this.AI_SERVICE_URL}/api/generate-video`, {
          text: input.text,
          image_url: input.imageUrl,
        })
      );

      const { job_id, status } = response.data;

      // Save job to database
      const roastJob = await this.roastJobRepository.create({
        jobId: job_id,
        petId: input.petId,
        text: input.text,
        imageUrl: input.imageUrl,
        status: status,
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      return roastJob;

    } catch (error) {
      // Handle no pets detected error
      if (error.response?.status === 400) {
        const errorDetail = error.response.data?.detail;
        if (errorDetail?.error === 'no_pets_detected') {
          throw new Error(errorDetail.message);
        }
      }

      // Handle other errors
      throw new Error(
        `Failed to generate roast: ${error.message}`
      );
    }
  }

  @Query(() => RoastJob)
  async getRoastJob(@Args('jobId') jobId: string): Promise<RoastJob> {
    return await this.roastJobRepository.findByJobId(jobId);
  }
}
```

---

### 2. Webhook Handler (Receive Video Completion)

```typescript
// controllers/webhook.controller.ts
import { Controller, Post, Body, HttpCode } from '@nestjs/common';

interface VideoCompletePayload {
  job_id: string;
  status: 'completed' | 'failed';
  video_url?: string;
  error?: string;
}

@Controller('webhooks')
export class WebhookController {
  constructor(
    private readonly roastJobRepository: RoastJobRepository,
    private readonly notificationService: NotificationService,
    private readonly firebaseService: FirebaseService,
  ) {}

  @Post('pet-roast-complete')
  @HttpCode(200)
  async handleVideoComplete(@Body() payload: VideoCompletePayload) {
    console.log('📥 Received video completion webhook:', payload);

    try {
      // Find job in database
      const roastJob = await this.roastJobRepository.findByJobId(
        payload.job_id
      );

      if (!roastJob) {
        console.warn(`⚠️  Job not found: ${payload.job_id}`);
        return { status: 'success', message: 'Job not found, ignoring' };
      }

      // Update job status
      roastJob.status = payload.status;
      roastJob.updatedAt = new Date();

      if (payload.status === 'completed' && payload.video_url) {
        roastJob.videoUrl = payload.video_url;

        // Store video in Firebase Storage (optional)
        const firebaseUrl = await this.firebaseService.storeVideoUrl(
          payload.video_url,
          roastJob.id
        );
        roastJob.videoUrl = firebaseUrl;

        console.log(`✅ Video ready for job ${payload.job_id}`);

        // Send push notification to user
        await this.notificationService.sendVideoReadyNotification(
          roastJob.userId,
          roastJob.petId,
          firebaseUrl
        );

      } else if (payload.status === 'failed') {
        roastJob.error = payload.error || 'Video generation failed';
        console.error(`❌ Video failed for job ${payload.job_id}:`, roastJob.error);

        // Send error notification to user
        await this.notificationService.sendVideoFailedNotification(
          roastJob.userId,
          roastJob.petId
        );
      }

      // Save updated job
      await this.roastJobRepository.save(roastJob);

      return {
        status: 'success',
        message: `Job ${payload.job_id} updated successfully`
      };

    } catch (error) {
      console.error('❌ Webhook processing error:', error);
      // Return 200 anyway to avoid webhook retries
      return {
        status: 'error',
        message: error.message
      };
    }
  }
}
```

---

### 3. Notification Service (Push Notifications)

```typescript
// services/notification.service.ts
import { Injectable } from '@nestjs/common';
import * as admin from 'firebase-admin';

@Injectable()
export class NotificationService {
  async sendVideoReadyNotification(
    userId: string,
    petId: string,
    videoUrl: string
  ): Promise<void> {
    // Get user's FCM token from database
    const user = await this.userRepository.findById(userId);
    if (!user?.fcmToken) {
      console.warn(`No FCM token for user ${userId}`);
      return;
    }

    // Send push notification
    const message = {
      token: user.fcmToken,
      notification: {
        title: '🎬 Your Pet Roast is Ready!',
        body: 'Your hilarious pet roast video is ready to watch!',
      },
      data: {
        type: 'video_ready',
        petId: petId,
        videoUrl: videoUrl,
      },
    };

    try {
      await admin.messaging().send(message);
      console.log(`✅ Notification sent to user ${userId}`);
    } catch (error) {
      console.error(`❌ Failed to send notification:`, error);
    }
  }

  async sendVideoFailedNotification(
    userId: string,
    petId: string
  ): Promise<void> {
    const user = await this.userRepository.findById(userId);
    if (!user?.fcmToken) return;

    const message = {
      token: user.fcmToken,
      notification: {
        title: '😞 Video Generation Failed',
        body: 'Sorry, we couldn\'t generate your pet roast. Please try again.',
      },
      data: {
        type: 'video_failed',
        petId: petId,
      },
    };

    await admin.messaging().send(message);
  }
}
```

---

## ⚙️ Environment Configuration

### AI Service (.env)

```env
# Revid.ai API
REVID_API_KEY=your_revid_api_key_here

# Backend webhook URL (YOUR Railway backend)
BACKEND_WEBHOOK_URL=https://your-backend.railway.app/webhooks/pet-roast-complete

# CORS origins (allow your backend)
CORS_ORIGINS=["https://your-backend.railway.app","https://your-frontend.vercel.app"]

# Redis (Railway addon)
REDIS_URL=redis://default:password@redis.railway.internal:6379
USE_REDIS=true

# AI4Bharat (optional if using external service)
AI4BHARAT_BASE_URL=http://localhost:5000
AI4BHARAT_API_KEY=optional_key
```

---

### Backend (.env)

```env
# AI Service URL
AI_SERVICE_URL=https://your-ai-service.up.railway.app

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Firebase
FIREBASE_PROJECT_ID=your-project
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email

# Redis (if needed)
REDIS_URL=redis://default:password@redis.railway.internal:6379
```

---

## 🚨 Error Handling

### Common Error Scenarios

#### 1. No Pets Detected (400)

```typescript
try {
  const response = await axios.post(`${AI_SERVICE_URL}/api/generate-video`, {
    text: roastText,
    image_url: petImageUrl
  });
} catch (error) {
  if (error.response?.status === 400) {
    const errorDetail = error.response.data?.detail;
    if (errorDetail?.error === 'no_pets_detected') {
      // Show user-friendly message
      throw new Error(
        'No pets found in your image. Please upload a clear photo of your pet!'
      );
    }
  }
}
```

#### 2. AI Service Timeout (502)

```typescript
import { HttpService } from '@nestjs/axios';
import { timeout, catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

const response$ = this.httpService.post(url, data).pipe(
  timeout(30000), // 30 second timeout
  catchError(error => {
    if (error.name === 'TimeoutError') {
      return throwError(() => new Error('AI service timeout'));
    }
    return throwError(() => error);
  })
);
```

#### 3. Video Generation Failed

```typescript
// In webhook handler
if (payload.status === 'failed') {
  // Log error
  console.error(`Video failed: ${payload.error}`);

  // Update database
  await this.roastJobRepository.update(payload.job_id, {
    status: 'failed',
    error: payload.error
  });

  // Notify user
  await this.notificationService.sendVideoFailedNotification(userId, petId);
}
```

---

## 🧪 Testing Integration

### 1. Test AI Service Health

```bash
curl https://your-ai-service.up.railway.app/healthz
# Expected: {"status":"ok"}
```

### 2. Test Video Generation (with valid pet image)

```bash
curl -X POST https://your-ai-service.up.railway.app/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Roast my lazy dog!",
    "image_url": "https://example.com/dog.jpg"
  }'

# Expected (202):
# {
#   "job_id": "abc123",
#   "status": "queued"
# }
```

### 3. Test No Pets Detection

```bash
curl -X POST https://your-ai-service.up.railway.app/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test",
    "image_url": "https://example.com/no-pets.jpg"
  }'

# Expected (400):
# {
#   "detail": {
#     "error": "no_pets_detected",
#     "message": "No pets found in the uploaded image...",
#     "suggestion": "Try uploading a clear photo or video of your pet."
#   }
# }
```

### 4. Test Video Status

```bash
curl https://your-ai-service.up.railway.app/api/video-status/abc123

# Expected:
# {
#   "job_id": "abc123",
#   "status": "processing",
#   "detail": null,
#   "updated_at": "2025-12-07T10:00:00Z"
# }
```

### 5. Test Backend Webhook (Manual)

```bash
curl -X POST https://your-backend.railway.app/webhooks/pet-roast-complete \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "abc123",
    "status": "completed",
    "video_url": "https://revid.ai/videos/abc123.mp4"
  }'

# Expected:
# {
#   "status": "success",
#   "message": "Job abc123 updated successfully"
# }
```

---

## 📊 Monitoring & Logging

### AI Service Logs

```bash
railway logs --service ai-service
```

**Key log messages to monitor:**
- ✅ `Pets detected: dog, cat`
- ✅ `Updated job abc123 status: completed`
- ✅ `Notified backend about job abc123`
- ❌ `No pets detected in image: https://...`
- ❌ `Failed to notify backend: Connection timeout`

### Backend Logs

```typescript
// Add structured logging
console.log('📥 Webhook received:', {
  jobId: payload.job_id,
  status: payload.status,
  timestamp: new Date().toISOString()
});

console.log('✅ Job updated:', {
  jobId: roastJob.id,
  status: roastJob.status,
  videoUrl: roastJob.videoUrl
});

console.log('🔔 Notification sent:', {
  userId: user.id,
  notificationType: 'video_ready'
});
```

---

## ✅ Integration Checklist

### AI Service Setup
- [ ] Deploy AI service to Railway
- [ ] Add Redis addon
- [ ] Set `REVID_API_KEY` environment variable
- [ ] Set `BACKEND_WEBHOOK_URL` to your backend webhook endpoint
- [ ] Set `CORS_ORIGINS` to include backend URL
- [ ] Test `/healthz` endpoint
- [ ] Test `/api/generate-video` with pet image

### Backend Setup
- [ ] Set `AI_SERVICE_URL` environment variable
- [ ] Implement GraphQL mutation `generatePetRoast`
- [ ] Create webhook endpoint `/webhooks/pet-roast-complete`
- [ ] Implement notification service
- [ ] Add error handling for no pets detected
- [ ] Test webhook handler manually
- [ ] Configure CORS to allow AI service

### End-to-End Testing
- [ ] Generate video from mobile app
- [ ] Verify job stored in backend database
- [ ] Check AI service processes video
- [ ] Confirm webhook received by backend
- [ ] Verify push notification sent to user
- [ ] Test error scenarios (no pets, timeout, failure)

---

## 🎯 Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Generate video | `/api/generate-video` | POST |
| Check status | `/api/video-status/{job_id}` | GET |
| Webhook callback | `/webhooks/pet-roast-complete` | POST |
| Health check | `/healthz` | GET |

---

## 📞 Support

For issues or questions:
1. Check Railway logs: `railway logs`
2. Review error messages in response
3. Verify environment variables are set correctly
4. Test each endpoint individually

---

**Last Updated:** December 7, 2025
**Version:** 1.0.0
