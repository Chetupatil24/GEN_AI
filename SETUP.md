# PetSnapChat - Complete Setup Guide

## 📁 Project Structure

```
pet_roasts/                         # Main Project Directory
├── app/                            # AI Service (FastAPI)
│   ├── api/
│   │   └── routes.py              # API endpoints
│   ├── services/
│   │   ├── pet_detection.py       # YOLOv5 pet detection
│   │   ├── job_store.py           # Job queue management
│   │   └── redis_job_store.py     # Redis implementation
│   ├── clients/
│   │   ├── ai4bharat.py           # IndicTrans2 client
│   │   ├── revid.py               # Video generation
│   │   └── sarvam.py              # Alternative translation
│   ├── core/
│   │   ├── config.py              # Configuration
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── webhook.py             # Webhook utilities
│   ├── main.py                    # FastAPI app entry
│   ├── dependencies.py            # Shared dependencies
│   └── schemas.py                 # Pydantic models
│
├── backend/                        # Backend Service (GraphQL)
│   ├── src/
│   │   ├── entities/
│   │   │   ├── User.ts            # User entity
│   │   │   ├── MasterLoginType.ts # Login type entity
│   │   │   └── PetRoast.ts        # Pet roast entity ✨
│   │   ├── service/
│   │   │   ├── user.service.ts    # User service
│   │   │   └── petRoast.service.ts # Pet roast service ✨
│   │   ├── resolvers/
│   │   │   ├── UserResolver.ts    # User resolver
│   │   │   ├── PetRoastResolver.ts # Pet roast resolver ✨
│   │   │   └── dto/
│   │   │       ├── userResolverDto.ts
│   │   │       └── petRoastDto.ts # Pet roast types ✨
│   │   ├── config/
│   │   │   ├── postgres.ts        # PostgreSQL config
│   │   │   └── mongodb.ts         # MongoDB config
│   │   ├── middleware/
│   │   │   └── authContext.ts     # Firebase auth
│   │   └── index.ts               # Main entry ✨ (webhook added)
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   ├── .env
│   └── TESTING_GUIDE.md
│
├── IndicTrans2/                    # Translation Engine
│   ├── inference/                  # Translation inference
│   ├── fairseq/                    # Fairseq models
│   └── model_configs/              # Model configurations
│
├── docker-compose.unified.yml      # 🚀 Main orchestration
├── docker-compose.standalone.yml   # Standalone AI service
├── Makefile                        # 🎯 Convenience commands
├── start-petsnapchat.sh           # 🚀 Startup script
│
├── Dockerfile                      # AI service Docker
├── Dockerfile.streamlit            # Streamlit UI Docker
├── requirements.txt                # Python dependencies
├── streamlit_app.py                # Admin dashboard
├── start.sh                        # AI service starter
│
├── .env                            # ⚙️ Environment variables
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
│
├── README.md                       # 📖 Main documentation
├── QUICKSTART.md                   # ⚡ Quick reference
├── SETUP.md                        # 📚 This file
├── BACKEND_INTEGRATION.md          # Backend integration docs
└── PETSNAPCHAT_INTEGRATION.md      # Integration details
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Mobile App (React Native)                     │
│                  Apollo Client + GraphQL                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ GraphQL Mutations/Queries
                         │ (Firebase Auth Token Required)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (Node.js + GraphQL)                     │
│                    Port: 4000                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  GraphQL Resolvers:                                 │    │
│  │  • generatePetRoast (mutation)                      │    │
│  │  • getPetRoast (query)                              │    │
│  │  • myPetRoasts (query)                              │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│  ┌─────────────────────┴────────────────────────────┐      │
│  │  Services:                                         │      │
│  │  • petRoast.service.ts                            │      │
│  │    - Calls AI REST API                            │      │
│  │    - Manages database records                     │      │
│  │    - Handles webhooks                             │      │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│  ┌─────────────────────┴────────────────────────────┐      │
│  │  Databases:                                        │      │
│  │  • PostgreSQL - Users, PetRoasts                  │      │
│  │  • MongoDB - Sessions                             │      │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API (HTTP POST)
                         │ POST /api/generate-video
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Pet Roast AI Service (FastAPI + Python)             │
│                    Port: 8000                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. Pet Detection (YOLOv5)                         │    │
│  │     • Validates image contains pets                │    │
│  │     • Returns error if no pets detected            │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  2. Translation (IndicTrans2)                      │    │
│  │     • Supports 13+ Indian languages                │    │
│  │     • English to: Hindi, Marathi, Tamil, etc.      │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  3. Video Generation (Revid.ai)                    │    │
│  │     • Sends translated script                      │    │
│  │     • Returns video URL                            │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  4. Webhook Callback                               │    │
│  │     POST /webhooks/pet-roast-complete              │    │
│  │     • Notifies backend of completion               │    │
│  │     • Includes video URL and status                │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│  ┌─────────────────────┴────────────────────────────┐      │
│  │  Supporting Services:                              │      │
│  │  • Redis - Job queue management                   │      │
│  │  • IndicTrans2 - Translation service (Port 5000)  │      │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow

### Complete End-to-End Flow

1. **User Action (Mobile App)**
   ```
   User uploads pet image
   User enters roast prompt
   User selects language
   ```

2. **GraphQL Mutation (Mobile → Backend)**
   ```graphql
   mutation {
     generatePetRoast(
       petImageUrl: "https://..."
       prompt: "Roast my dog!"
     ) {
       data { jobId }
     }
   }
   ```

3. **Backend Processing**
   ```
   ✓ Validate Firebase auth token
   ✓ Create PetRoast record (status: PENDING)
   ✓ Call AI service REST API
   ✓ Return job_id to client
   ```

4. **AI Service Processing**
   ```
   ✓ Detect pets with YOLOv5
   ✓ Translate prompt to target language
   ✓ Generate video with Revid.ai
   ✓ Send webhook to backend
   ```

5. **Webhook Callback (AI → Backend)**
   ```
   POST /webhooks/pet-roast-complete
   {
     job_id: "...",
     status: "completed",
     video_url: "https://..."
   }
   ```

6. **Backend Updates Database**
   ```
   ✓ Find PetRoast by job_id
   ✓ Update status to COMPLETED
   ✓ Store video_url
   ✓ Send push notification (optional)
   ```

7. **Client Polling/Query**
   ```graphql
   query {
     getPetRoast(id: "...") {
       data {
         status
         videoUrl
       }
     }
   }
   ```

## 🚀 Installation

### Step 1: Environment Setup

```bash
cd /home/chetan-patil/myprojects/pet_roasts

# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### Step 2: Required API Keys

Add these to `.env`:

```env
# Revid.ai - Video Generation (REQUIRED)
REVID_API_KEY=your_revid_api_key_here

# Sarvam - Alternative Translation (OPTIONAL)
SARVAM_API_KEY=your_sarvam_key_here

# Firebase - Authentication (REQUIRED)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_CLIENT_EMAIL=your_service_account_email
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### Step 3: Start All Services

```bash
# Using Make (recommended)
make start

# Or using Docker Compose directly
docker-compose -f docker-compose.unified.yml up --build -d

# Or using startup script
./start-petsnapchat.sh
```

### Step 4: Verify Services

```bash
# Check all services are running
make status

# Or check manually
docker ps
```

Expected output:
```
petsnapchat-postgres     ✓ healthy
petsnapchat-mongodb      ✓ healthy
petsnapchat-redis        ✓ healthy
petsnapchat-indictrans2  ✓ healthy
petsnapchat-ai           ✓ healthy
petsnapchat-backend      ✓ healthy
petsnapchat-streamlit    ✓ running
```

### Step 5: Test the System

```bash
# View logs
make logs

# Test GraphQL endpoint
curl http://localhost:4000/graphql

# Test AI service
curl http://localhost:8000/health
```

## 🎯 Usage

### Via GraphQL (Mobile App)

#### 1. Generate Pet Roast Video

```graphql
mutation GeneratePetRoast {
  generatePetRoast(
    petImageUrl: "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=800"
    prompt: "Roast my lazy dog who sleeps all day"
  ) {
    status
    code
    message
    data {
      id
      jobId
      status
      petImageUrl
      prompt
      createdAt
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "generatePetRoast": {
      "status": "success",
      "code": 200,
      "message": "Pet roast video generation started",
      "data": {
        "id": "uuid-here",
        "jobId": "job_abc123",
        "status": "PROCESSING",
        "petImageUrl": "https://...",
        "prompt": "Roast my lazy dog...",
        "createdAt": "2025-12-03T19:30:00Z"
      }
    }
  }
}
```

#### 2. Check Video Status

```graphql
query GetPetRoast {
  getPetRoast(id: "uuid-here") {
    status
    data {
      id
      jobId
      status
      videoUrl
      error
      createdAt
      updatedAt
    }
  }
}
```

#### 3. Get All User Videos

```graphql
query MyPetRoasts {
  myPetRoasts {
    status
    data {
      id
      status
      videoUrl
      petImageUrl
      prompt
      createdAt
    }
  }
}
```

### Via REST API (Direct AI Service)

```bash
# Generate video directly (bypasses backend)
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=800",
    "prompt": "Roast my dog",
    "target_language": "hi_IN",
    "webhook_url": "http://backend:4000/webhooks/pet-roast-complete"
  }'
```

## 🛠️ Make Commands

```bash
make start          # Start all services (detached mode)
make stop           # Stop all services
make restart        # Restart all services
make logs           # View all logs (follow mode)
make logs-ai        # View AI service logs only
make logs-backend   # View backend logs only
make status         # Check service health
make clean          # Remove all containers and volumes
make build          # Rebuild all images
make test           # Run tests (if implemented)
make db-psql        # Connect to PostgreSQL
make db-mongo       # Connect to MongoDB
make db-redis       # Connect to Redis CLI
```

## 📊 Monitoring

### View Logs

```bash
# All services
make logs

# Specific service
docker logs -f petsnapchat-backend
docker logs -f petsnapchat-ai

# Last 100 lines
docker logs --tail 100 petsnapchat-backend
```

### Check Database

```bash
# PostgreSQL
make db-psql
# Then: SELECT * FROM pet_roasts;

# MongoDB
make db-mongo
# Then: use petsnapchat; db.sessions.find();

# Redis
make db-redis
# Then: KEYS *
```

### Health Checks

```bash
# Check all services
make status

# Individual health checks
curl http://localhost:4000/graphql
curl http://localhost:8000/health
curl http://localhost:8501
```

## 🐛 Troubleshooting

### Issue: Services not starting

**Check logs:**
```bash
make logs
```

**Common fixes:**
```bash
# Clean restart
make clean
make build
make start
```

### Issue: Backend can't connect to AI service

**Check network:**
```bash
docker network inspect pet_roasts_petsnapchat-network
```

**Verify AI service is running:**
```bash
docker ps | grep petsnapchat-ai
curl http://localhost:8000/health
```

### Issue: Database connection errors

**Check database health:**
```bash
docker ps | grep postgres
docker ps | grep mongodb
```

**Reset databases:**
```bash
make clean
make start
```

### Issue: No pets detected error

**Verify image URL is accessible:**
```bash
curl -I "https://your-image-url.com/image.jpg"
```

**Use a valid pet image:**
- Must contain visible pets (dogs, cats, etc.)
- YOLO must be able to detect the pet
- High-quality, well-lit images work best

### Issue: Translation not working

**Check IndicTrans2 service:**
```bash
docker logs petsnapchat-indictrans2
curl http://localhost:5000/health
```

**Supported languages:**
- Hindi (hi_IN)
- Marathi (mr_IN)
- Tamil (ta_IN)
- Telugu (te_IN)
- Bengali (bn_IN)
- Gujarati (gu_IN)
- Kannada (kn_IN)
- Malayalam (ml_IN)
- Punjabi (pa_IN)
- Odia (or_IN)
- Assamese (as_IN)
- Urdu (ur_IN)

## 🚢 Production Deployment

### Pre-Deployment Checklist

- [ ] Set strong database passwords
- [ ] Configure SSL certificates
- [ ] Set NODE_ENV=production
- [ ] Enable production logging
- [ ] Configure database backups
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure rate limiting
- [ ] Set up CDN for video storage
- [ ] Enable CORS properly
- [ ] Configure secrets management

### Environment Variables (Production)

```env
# Backend
NODE_ENV=production
PORT=4000
DATABASE_URL=postgresql://user:pass@db-host:5432/petsnapchat
MONGODB_URI=mongodb://user:pass@mongo-host:27017/petsnapchat
PET_ROAST_API_URL=https://ai.yourdomain.com
WEBHOOK_BASE_URL=https://api.yourdomain.com

# AI Service
REDIS_URL=redis://redis-host:6379
INDICTRANS2_URL=http://translation-service:5000
REVID_API_KEY=prod_key_here
```

### Deployment Steps

1. **Build production images:**
   ```bash
   docker-compose -f docker-compose.unified.yml build
   ```

2. **Push to registry:**
   ```bash
   docker tag petsnapchat-backend:latest registry.com/petsnapchat-backend:v1.0
   docker push registry.com/petsnapchat-backend:v1.0
   ```

3. **Deploy to cloud:**
   - AWS ECS/EKS
   - Google Cloud Run
   - Azure Container Instances
   - DigitalOcean Apps

4. **Configure monitoring:**
   - Application logs
   - Database metrics
   - API response times
   - Error rates

## 📱 Mobile App Integration

### Install Dependencies

```bash
npm install @apollo/client graphql firebase
```

### Setup Apollo Client

```typescript
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { auth } from './firebase';

const httpLink = createHttpLink({
  uri: 'https://api.yourdomain.com/graphql',
});

const authLink = setContext(async (_, { headers }) => {
  const token = await auth.currentUser?.getIdToken();
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  };
});

export const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
```

### Usage in React Native

```typescript
import { useMutation, useQuery } from '@apollo/client';
import { GENERATE_PET_ROAST, GET_PET_ROAST } from './queries';

function PetRoastScreen() {
  const [generatePetRoast, { loading, data }] = useMutation(GENERATE_PET_ROAST);

  const handleGenerateVideo = async (imageUrl: string, prompt: string) => {
    try {
      const result = await generatePetRoast({
        variables: { petImageUrl: imageUrl, prompt },
      });
      console.log('Job ID:', result.data.generatePetRoast.data.jobId);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <View>
      {/* Your UI here */}
    </View>
  );
}
```

## 🎓 Learning Resources

- **GraphQL**: https://graphql.org/learn/
- **Apollo Client**: https://www.apollographql.com/docs/react/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **TypeORM**: https://typeorm.io/
- **Firebase Auth**: https://firebase.google.com/docs/auth

## 📞 Support

For issues or questions:
1. Check TROUBLESHOOTING section above
2. Review logs: `make logs`
3. Check service health: `make status`
4. Refer to TESTING_GUIDE.md in backend/

---

**Built with ❤️ by PetSnapChat Team**
