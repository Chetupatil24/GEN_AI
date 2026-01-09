// ============================================================================
// BACKEND IMPLEMENTATION EXAMPLES - Node.js/Express
// Complete code for connecting your backend to Pet Roast AI Service
// ============================================================================

const express = require('express');
const axios = require('axios');
const router = express.Router();

// ============================================================================
// CONFIGURATION
// ============================================================================

const AI_SERVICE_URL = process.env.PET_ROAST_AI_URL || 'https://your-ai-service.up.railway.app';
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'your-secret-key';

// ============================================================================
// 1. WEBHOOK ENDPOINT - Receive notifications from AI service
// ============================================================================

/**
 * POST /api/webhooks/video-complete
 * Called by AI service when video generation is complete
 */
router.post('/webhooks/video-complete', async (req, res) => {
    try {
        console.log('📥 Webhook received:', req.body);

        const { job_id, status, video_url, user_id, error } = req.body;

        // Validate required fields
        if (!job_id || !status) {
            return res.status(400).json({
                error: 'Missing required fields: job_id, status'
            });
        }

        // Optional: Verify webhook signature for security
        // const signature = req.headers['x-webhook-signature'];
        // if (!verifySignature(req.body, signature, WEBHOOK_SECRET)) {
        //   return res.status(401).json({ error: 'Invalid signature' });
        // }

        if (status === 'completed' && video_url) {
            console.log('✅ Video completed:', job_id);

            // Update database
            await updateVideoInDatabase({
                jobId: job_id,
                status: 'completed',
                videoUrl: video_url,
                completedAt: new Date()
            });

            // Send push notification to user
            if (user_id) {
                await sendPushNotification(user_id, {
                    title: '🎉 Your Pet Roast is Ready!',
                    body: 'Your hilarious pet roast video is ready to watch!',
                    data: {
                        videoUrl: video_url,
                        jobId: job_id,
                        screen: 'VideoPlayer'
                    }
                });
            }

            res.json({
                success: true,
                message: 'Video completion processed'
            });

        } else if (status === 'failed') {
            console.log('❌ Video generation failed:', job_id, error);

            // Update database
            await updateVideoInDatabase({
                jobId: job_id,
                status: 'failed',
                error: error || 'Video generation failed'
            });

            // Optionally notify user of failure
            if (user_id) {
                await sendPushNotification(user_id, {
                    title: '😔 Video Generation Failed',
                    body: 'Sorry, we couldn\'t generate your video. Please try again.',
                    data: { jobId: job_id }
                });
            }

            res.json({
                success: true,
                message: 'Failure recorded'
            });

        } else {
            // Status update (processing, queued, etc.)
            console.log('📊 Status update:', job_id, status);

            await updateVideoInDatabase({
                jobId: job_id,
                status: status
            });

            res.json({
                success: true,
                message: 'Status updated'
            });
        }

    } catch (error) {
        console.error('❌ Webhook processing error:', error);
        res.status(500).json({
            error: 'Webhook processing failed',
            message: error.message
        });
    }
});

// ============================================================================
// 2. GENERATE VIDEO - Call AI service to create video
// ============================================================================

/**
 * POST /api/roast/generate
 * User initiates video generation
 */
router.post('/roast/generate', async (req, res) => {
    try {
        const { text, imageUrl, userId } = req.body;

        // Validate input
        if (!text || !imageUrl) {
            return res.status(400).json({
                error: 'Missing required fields: text, imageUrl'
            });
        }

        console.log('🎬 Generating video for user:', userId);

        // Call AI service
        const response = await axios.post(
            `${AI_SERVICE_URL}/api/generate-video`,
            {
                text: text,
                image_url: imageUrl
            },
            {
                timeout: 30000,
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        const { job_id, status } = response.data;

        console.log('✅ Video job created:', job_id);

        // Save to database
        await saveVideoToDatabase({
            jobId: job_id,
            userId: userId,
            status: status,
            imageUrl: imageUrl,
            roastText: text,
            createdAt: new Date()
        });

        res.json({
            success: true,
            jobId: job_id,
            status: status,
            message: 'Video generation started'
        });

    } catch (error) {
        console.error('❌ Video generation error:', error);

        if (error.response) {
            // AI service returned an error
            const status = error.response.status;
            const message = error.response.data?.detail || 'Video generation failed';

            if (status === 400) {
                // Likely no pet detected
                return res.status(400).json({
                    error: message,
                    hint: 'Make sure the image contains a visible pet'
                });
            }

            return res.status(502).json({
                error: 'AI service error',
                message: message
            });
        }

        res.status(500).json({
            error: 'Failed to generate video',
            message: error.message
        });
    }
});

// ============================================================================
// 3. CHECK VIDEO STATUS - Poll for completion
// ============================================================================

/**
 * GET /api/roast/status/:jobId
 * Check video generation status
 */
router.get('/roast/status/:jobId', async (req, res) => {
    try {
        const { jobId } = req.params;

        // First check our database
        const video = await getVideoFromDatabase(jobId);

        if (!video) {
            return res.status(404).json({
                error: 'Job not found'
            });
        }

        // If already completed, return from database
        if (video.status === 'completed') {
            return res.json({
                jobId: video.jobId,
                status: 'completed',
                videoUrl: video.videoUrl,
                createdAt: video.createdAt,
                completedAt: video.completedAt
            });
        }

        // If still processing, check AI service for latest status
        try {
            const response = await axios.get(
                `${AI_SERVICE_URL}/api/video-status/${jobId}`,
                { timeout: 10000 }
            );

            const aiStatus = response.data;

            // Update our database if status changed
            if (aiStatus.status !== video.status) {
                await updateVideoInDatabase({
                    jobId: jobId,
                    status: aiStatus.status,
                    videoUrl: aiStatus.video_url
                });
            }

            res.json({
                jobId: jobId,
                status: aiStatus.status,
                videoUrl: aiStatus.video_url || video.videoUrl,
                createdAt: video.createdAt
            });

        } catch (error) {
            // AI service unavailable, return database status
            console.warn('AI service unavailable, returning cached status');
            res.json({
                jobId: video.jobId,
                status: video.status,
                videoUrl: video.videoUrl,
                createdAt: video.createdAt
            });
        }

    } catch (error) {
        console.error('❌ Status check error:', error);
        res.status(500).json({
            error: 'Failed to check status',
            message: error.message
        });
    }
});

// ============================================================================
// 4. GET USER'S VIDEOS - List all videos for a user
// ============================================================================

/**
 * GET /api/roast/user/:userId
 * Get all videos for a specific user
 */
router.get('/roast/user/:userId', async (req, res) => {
    try {
        const { userId } = req.params;
        const videos = await getUserVideosFromDatabase(userId);

        res.json({
            success: true,
            videos: videos,
            count: videos.length
        });

    } catch (error) {
        console.error('❌ Error fetching user videos:', error);
        res.status(500).json({
            error: 'Failed to fetch videos'
        });
    }
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Update video record in database
 */
async function updateVideoInDatabase(data) {
    // Replace with your actual database logic
    // Example using Prisma:
    /*
    await prisma.video.update({
      where: { jobId: data.jobId },
      data: {
        status: data.status,
        videoUrl: data.videoUrl,
        error: data.error,
        completedAt: data.completedAt
      }
    });
    */

    console.log('💾 Database update:', data);

    // Example using MongoDB:
    /*
    await Video.findOneAndUpdate(
      { jobId: data.jobId },
      { $set: data },
      { upsert: true }
    );
    */
}

/**
 * Save new video record to database
 */
async function saveVideoToDatabase(data) {
    // Replace with your actual database logic
    // Example using Prisma:
    /*
    await prisma.video.create({
      data: {
        jobId: data.jobId,
        userId: data.userId,
        status: data.status,
        imageUrl: data.imageUrl,
        roastText: data.roastText,
        createdAt: data.createdAt
      }
    });
    */

    console.log('💾 Database save:', data);
}

/**
 * Get video from database
 */
async function getVideoFromDatabase(jobId) {
    // Replace with your actual database logic
    // Example using Prisma:
    /*
    return await prisma.video.findUnique({
      where: { jobId: jobId }
    });
    */

    console.log('🔍 Database query:', jobId);

    // Mock response for example
    return {
        jobId: jobId,
        status: 'processing',
        createdAt: new Date()
    };
}

/**
 * Get all videos for a user
 */
async function getUserVideosFromDatabase(userId) {
    // Replace with your actual database logic
    // Example using Prisma:
    /*
    return await prisma.video.findMany({
      where: { userId: userId },
      orderBy: { createdAt: 'desc' }
    });
    */

    console.log('🔍 Fetching videos for user:', userId);
    return [];
}

/**
 * Send push notification to user
 */
async function sendPushNotification(userId, notification) {
    // Replace with your actual push notification logic
    // Example using Firebase:
    /*
    const admin = require('firebase-admin');
  
    const userToken = await getUserPushToken(userId);
  
    if (userToken) {
      await admin.messaging().send({
        token: userToken,
        notification: {
          title: notification.title,
          body: notification.body
        },
        data: notification.data
      });
    }
    */

    console.log('📱 Push notification:', userId, notification);
}

/**
 * Verify webhook signature (optional but recommended)
 */
function verifySignature(payload, signature, secret) {
    const crypto = require('crypto');

    const expectedSignature = crypto
        .createHmac('sha256', secret)
        .update(JSON.stringify(payload))
        .digest('hex');

    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSignature)
    );
}

// ============================================================================
// EXPORT ROUTER
// ============================================================================

module.exports = router;

// ============================================================================
// USAGE IN YOUR MAIN APP
// ============================================================================

/*
// In your main app.js or server.js:

const express = require('express');
const petRoastRoutes = require('./routes/petRoast');

const app = express();

app.use(express.json());
app.use('/api', petRoastRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
  console.log(`🔗 AI Service: ${process.env.PET_ROAST_AI_URL}`);
});
*/
