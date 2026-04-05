# Example AWS-Focused PRD Output
## Fitness Tracking App with AI-Powered Workout Plans

This is an example of what Claude will generate for your customers using the AWS-focused PRD workflow.

---

## 1. Product Overview

**Product Name**: FitGenius AI

**Vision**: An AI-powered fitness tracking application that creates personalized workout plans and adapts them based on user progress, built entirely on AWS cloud infrastructure.

**Problem Statement**: Beginners struggle to create effective workout routines and often quit due to lack of guidance and motivation. Current fitness apps provide generic plans that don't adapt to individual progress.

**Solution**: FitGenius AI uses AWS Bedrock (Claude) to generate personalized workout plans based on user goals, fitness level, and real-time progress tracking. The app learns from user feedback and adjusts plans automatically.

**Target Users**:
- Fitness beginners (primary)
- Intermediate fitness enthusiasts (secondary)
- Age range: 18-45
- Tech-savvy mobile users

---

## 2. User Personas

### Primary: Sarah the Beginner
- **Age**: 28
- **Background**: Office worker, no prior gym experience
- **Goals**: Lose 15 lbs, build basic strength
- **Pain Points**:
  - Intimidated by gyms
  - Doesn't know where to start
  - Needs accountability
- **Tech Comfort**: High (uses apps daily)

### Secondary: Mike the Intermediate
- **Age**: 34
- **Background**: Works out 2-3x/week inconsistently
- **Goals**: Build muscle, break through plateau
- **Pain Points**:
  - Lacks structured progression
  - Bored with current routine
  - No tracking system
- **Tech Comfort**: High

---

## 3. Core Features

### MVP Features (Week 0-8)

1. **User Registration & Onboarding**
   - Email/password or social login (Google, Apple)
   - Fitness level assessment questionnaire
   - Goal setting (weight loss, muscle gain, general fitness)
   - Body metrics input (weight, height, age)

2. **AI-Powered Workout Plan Generation**
   - Input: User goals, fitness level, available equipment
   - AWS Bedrock (Claude) generates 4-week progressive plan
   - Exercise library with instructions and videos (S3)
   - Rest day scheduling

3. **Workout Logging**
   - Quick-log interface (< 30 seconds per workout)
   - Exercise selection from plan
   - Rep/set tracking
   - Weight tracking
   - Duration timer
   - Voice input support (AWS Transcribe)

4. **Progress Tracking Dashboard**
   - Visual charts (weight, volume lifted, workout frequency)
   - Streak tracking
   - Milestone badges
   - Before/after photo uploads (S3)

5. **Plan Adaptation**
   - Weekly progress analysis
   - Automatic difficulty adjustment
   - Exercise substitutions for injuries
   - Feedback collection

### Phase 2 Features (Week 9-16)

6. **Nutrition Tracking** (Basic)
   - Calorie/macro logging
   - AI meal suggestions (Bedrock)
   - Photo-based food recognition (Rekognition)

7. **Social Features**
   - Share workouts
   - Friend challenges
   - Community feed
   - Workout buddy matching

8. **Wearable Integration**
   - Apple Watch sync
   - Fitbit sync
   - Heart rate monitoring
   - Auto-workout detection

### Future Enhancements

9. **Video Form Analysis** (Rekognition Custom Labels)
10. **Live Virtual Trainer** (Interactive Video Service)
11. **Marketplace** (Find trainers, buy programs)

---

## 4. AWS Data Model

### DynamoDB Tables

#### Users Table (On-Demand)
```
PK: userId (UUID)
Attributes:
  - email (String, GSI)
  - name (String)
  - cognitoSub (String)
  - fitnessLevel (String) // beginner, intermediate, advanced
  - goals (Map)
    - primary: String // weight_loss, muscle_gain, general_fitness
    - targetWeight: Number
    - weeklyWorkouts: Number
  - bodyMetrics (Map)
    - weight: Number
    - height: Number
    - age: Number
    - gender: String
  - preferences (Map)
    - equipment: List // bodyweight, dumbbells, full_gym
    - duration: Number // minutes per workout
    - experienceLevel: String
  - subscription (Map)
    - tier: String // free, pro
    - expiresAt: String (ISO 8601)
  - createdAt: String (ISO 8601)
  - updatedAt: String (ISO 8601)

GSI:
  - GSI1: email (PK)
```

#### Workouts Table (On-Demand)
```
PK: workoutId (UUID)
SK: userId#date (Composite)
Attributes:
  - userId (String, GSI1-PK)
  - date (String, GSI1-SK)
  - planId (String)
  - exercises (List of Maps)
    [
      {
        exerciseId: String
        name: String
        sets: Number
        reps: List<Number>
        weight: List<Number> // lbs or kg
        restSeconds: Number
        completed: Boolean
      }
    ]
  - durationMinutes (Number)
  - caloriesBurned (Number) // estimated
  - notes (String)
  - mood (String) // great, good, okay, tired
  - completedAt (String, ISO 8601)
  - createdAt (String, ISO 8601)

GSI1:
  - PK: userId
  - SK: date (descending)
```

#### WorkoutPlans Table (On-Demand)
```
PK: planId (UUID)
SK: userId
Attributes:
  - userId (String)
  - generatedAt (String, ISO 8601)
  - generatedBy (String) // "ai" or "trainer"
  - status (String) // active, completed, abandoned
  - durationWeeks (Number)
  - difficulty (String)
  - schedule (Map)
    - monday: List<ExerciseTemplate>
    - tuesday: rest
    - wednesday: List<ExerciseTemplate>
    - etc.
  - aiParameters (Map)
    - modelId: String
    - prompt: String
    - temperature: Number
    - completionTokens: Number
  - progressMetrics (Map)
    - workoutsCompleted: Number
    - workoutsMissed: Number
    - avgCompletionRate: Number
  - adaptationHistory (List)
    [
      {
        date: String
        reason: String
        changes: Map
      }
    ]
  - createdAt: String
  - updatedAt: String
```

#### ExerciseLibrary Table (Provisioned - Read-Heavy)
```
PK: exerciseId (UUID)
Attributes:
  - name (String)
  - category (String) // strength, cardio, flexibility
  - muscleGroup (String, GSI) // chest, back, legs, etc.
  - equipment (String) // bodyweight, dumbbells, barbell, machine
  - difficulty (String) // beginner, intermediate, advanced
  - instructions (String)
  - videoUrl (String) // S3 URL
  - thumbnailUrl (String) // S3 URL
  - caloriesPerRep (Number)
  - alternativeExercises (List<String>) // Exercise IDs
  - tags (List<String>)
  - createdAt: String

GSI:
  - muscleGroup-difficulty-index
```

#### ProgressPhotos Table (On-Demand)
```
PK: photoId (UUID)
SK: userId#date
Attributes:
  - userId (String)
  - date (String)
  - s3Key (String) // S3 object key
  - s3Bucket (String)
  - cloudFrontUrl (String) // CDN URL
  - type (String) // front, back, side
  - bodyWeight (Number)
  - visibility (String) // private, friends, public
  - rekognitionLabels (List) // AI-detected labels
  - createdAt: String
```

### S3 Buckets

```
fitgenius-user-photos-prod
  ├── /users/{userId}/progress/{photoId}.jpg
  └── /users/{userId}/profile/{photoId}.jpg

fitgenius-exercise-media-prod
  ├── /videos/{exerciseId}.mp4
  ├── /thumbnails/{exerciseId}.jpg
  └── /instructions/{exerciseId}.pdf

fitgenius-app-assets-prod
  ├── /images/badges/*.png
  ├── /images/icons/*.svg
  └── /audio/workout-complete.mp3
```

---

## 5. AWS Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USERS                                │
│                    (Mobile App / Web)                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│               AWS CloudFront (CDN)                          │
│  • Cache static assets                                      │
│  • SSL/TLS termination                                      │
│  • DDoS protection (AWS Shield)                             │
└────────────────┬───────────────────────────────────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
        ▼                  ▼
┌──────────────┐   ┌──────────────────┐
│  S3 Static   │   │  API Gateway     │
│  Website     │   │  (REST API)      │
│  (Amplify)   │   │                  │
└──────────────┘   └────────┬─────────┘
                            │
                   ┌────────┴────────┐
                   │   AWS WAF       │
                   │  (Firewall)     │
                   └────────┬────────┘
                            │
        ┌───────────────────┼──────────────────┐
        │                   │                  │
        ▼                   ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Lambda:     │  │  Lambda:     │  │  Lambda:     │
│  Auth        │  │  Workouts    │  │  AI Plans    │
│              │  │              │  │              │
│ • Login      │  │ • Log        │  │ • Generate   │
│ • Register   │  │ • Get        │  │ • Adapt      │
│ • Refresh    │  │ • Update     │  │ • Feedback   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Cognito     │  │  DynamoDB    │  │  Bedrock     │
│  User Pools  │  │  Tables      │  │  (Claude)    │
└──────────────┘  └──────┬───────┘  └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  DynamoDB    │
                  │  Streams     │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Lambda:     │
                  │  Analytics   │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Kinesis     │
                  │  Firehose    │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  S3 Data     │
                  │  Lake        │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Athena      │
                  │  (Analytics) │
                  └──────────────┘
```

### AWS Service Justifications

**Why Amazon Cognito for Authentication?**
- Built-in user pool management with MFA
- Social identity federation (Google, Apple Sign-In)
- JWT token generation and validation
- Seamless API Gateway integration
- Secure password policies and account recovery
- Pay-per-user pricing (no base cost)

**Why AWS Lambda for Backend?**
- Serverless = no server management
- Auto-scaling from 0 to millions of requests
- Pay only for compute time used
- Native integration with API Gateway, DynamoDB, S3
- Fast cold start times (<1s) with provisioned concurrency
- Easy CI/CD with AWS SAM or CDK

**Why Amazon DynamoDB for Database?**
- Serverless = no capacity planning
- Single-digit millisecond latency
- Automatic scaling
- Built-in backup and point-in-time recovery
- Perfect for user data (key-value access patterns)
- DynamoDB Streams for real-time analytics
- On-demand pricing for unpredictable traffic

**Why AWS Bedrock for AI?**
- Access to Claude 3.5 Sonnet for plan generation
- No ML expertise required
- Pay-per-token pricing
- Low latency (<2s for plan generation)
- Content filtering built-in
- Easy prompt management

**Why S3 + CloudFront for Media?**
- Infinite scalability for photos/videos
- Automatic lifecycle policies (archive old photos)
- CloudFront CDN for global low-latency delivery
- Integrated with Rekognition for image analysis
- Versioning for photo history

**Why API Gateway?**
- RESTful API with OpenAPI spec
- Request/response transformation
- Rate limiting and throttling
- API key management
- CORS support
- WebSocket support for real-time features

**Why AWS Amplify for Frontend?**
- Git-based CI/CD
- Automatic builds and deployments
- Preview environments for branches
- Custom domain with SSL
- Hosting + CDN in one service
- Easy integration with Cognito

---

## 6. API Design (API Gateway + Lambda)

### Base URL
```
https://api.fitgenius.com/v1
```

### Authentication
All endpoints (except /auth/*) require:
```
Authorization: Bearer {JWT_TOKEN}
```

### Endpoints

#### Authentication

**POST /auth/register**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}

Response: 201 Created
{
  "userId": "uuid-123",
  "email": "user@example.com",
  "message": "Please check your email to verify your account"
}

Lambda: auth-register
```

**POST /auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "accessToken": "eyJhbGci...",
  "refreshToken": "eyJhbGci...",
  "expiresIn": 3600,
  "user": {
    "userId": "uuid-123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}

Lambda: auth-login
```

**POST /auth/refresh**
```json
Request:
{
  "refreshToken": "eyJhbGci..."
}

Response: 200 OK
{
  "accessToken": "eyJhbGci...",
  "expiresIn": 3600
}

Lambda: auth-refresh
```

#### User Profile

**GET /users/me**
```json
Response: 200 OK
{
  "userId": "uuid-123",
  "email": "user@example.com",
  "name": "John Doe",
  "fitnessLevel": "beginner",
  "goals": {
    "primary": "weight_loss",
    "targetWeight": 160,
    "weeklyWorkouts": 4
  },
  "bodyMetrics": {
    "weight": 180,
    "height": 70,
    "age": 28,
    "gender": "male"
  },
  "createdAt": "2025-11-01T10:00:00Z"
}

Lambda: user-get-profile
DynamoDB: Users table (GetItem)
```

**PUT /users/me**
```json
Request:
{
  "name": "John Doe",
  "bodyMetrics": {
    "weight": 178
  }
}

Response: 200 OK
{
  "userId": "uuid-123",
  ...updated fields
}

Lambda: user-update-profile
DynamoDB: Users table (UpdateItem)
```

#### Workouts

**POST /workouts**
```json
Request:
{
  "date": "2025-11-08",
  "planId": "plan-uuid-456",
  "exercises": [
    {
      "exerciseId": "ex-123",
      "name": "Push-ups",
      "sets": 3,
      "reps": [12, 10, 10],
      "weight": [0, 0, 0],
      "completed": true
    }
  ],
  "durationMinutes": 45,
  "mood": "great",
  "notes": "Felt strong today!"
}

Response: 201 Created
{
  "workoutId": "workout-uuid-789",
  "userId": "uuid-123",
  "date": "2025-11-08",
  ...
}

Lambda: workout-create
DynamoDB: Workouts table (PutItem)
EventBridge: Emit "workout.completed" event
```

**GET /workouts?startDate=2025-11-01&endDate=2025-11-08**
```json
Response: 200 OK
{
  "workouts": [
    {
      "workoutId": "workout-uuid-789",
      "date": "2025-11-08",
      "exercises": [...],
      "durationMinutes": 45
    }
  ],
  "count": 5,
  "nextToken": null
}

Lambda: workout-list
DynamoDB: Workouts table (Query on GSI1)
```

#### AI Workout Plans

**POST /plans/generate**
```json
Request:
{
  "goals": {
    "primary": "muscle_gain",
    "weeklyWorkouts": 4,
    "durationWeeks": 8
  },
  "equipment": ["dumbbells", "pull_up_bar"],
  "fitnessLevel": "intermediate"
}

Response: 200 OK
{
  "planId": "plan-uuid-456",
  "durationWeeks": 8,
  "schedule": {
    "monday": [
      {
        "exerciseId": "ex-123",
        "name": "Bench Press",
        "sets": 4,
        "repsRange": "8-12",
        "restSeconds": 90
      }
    ],
    ...
  },
  "generatedAt": "2025-11-08T12:00:00Z"
}

Lambda: plan-generate
Bedrock: Invoke Claude 3.5 Sonnet
DynamoDB: WorkoutPlans table (PutItem)
```

**PUT /plans/:planId/feedback**
```json
Request:
{
  "feedback": "too_hard",
  "specificExercises": ["ex-123"],
  "notes": "Need to reduce weight on bench press"
}

Response: 200 OK
{
  "planId": "plan-uuid-456",
  "adapted": true,
  "changes": [
    "Reduced bench press from 4 sets to 3 sets",
    "Suggested lighter dumbbell variation"
  ]
}

Lambda: plan-adapt
Bedrock: Generate adaptations with Claude
DynamoDB: WorkoutPlans table (UpdateItem)
```

#### Progress & Analytics

**GET /progress/charts?metric=weight&startDate=2025-10-01**
```json
Response: 200 OK
{
  "metric": "weight",
  "dataPoints": [
    { "date": "2025-10-01", "value": 180 },
    { "date": "2025-10-08", "value": 178 },
    { "date": "2025-10-15", "value": 176 }
  ],
  "trend": "decreasing",
  "percentChange": -2.2
}

Lambda: analytics-charts
DynamoDB: Workouts table + Users table
```

**POST /progress/photos**
```json
Request (multipart/form-data):
{
  "photo": <binary>,
  "type": "front",
  "date": "2025-11-08"
}

Response: 201 Created
{
  "photoId": "photo-uuid-999",
  "s3Key": "users/uuid-123/progress/photo-uuid-999.jpg",
  "cloudFrontUrl": "https://cdn.fitgenius.com/...",
  "rekognitionLabels": ["Person", "Fitness", "Gym"],
  "createdAt": "2025-11-08T15:00:00Z"
}

Lambda: photo-upload
S3: Put object to fitgenius-user-photos-prod
Rekognition: DetectLabels API
DynamoDB: ProgressPhotos table (PutItem)
```

---

## 7. UX Flows

### Flow 1: New User Onboarding (< 2 minutes)

```
1. User opens app
   └─> Display: Splash screen with logo

2. Sign up screen
   └─> Input: Email, Password, Name
   └─> OR: "Continue with Google" (Cognito Social Login)
   └─> OR: "Continue with Apple"

3. Email verification
   └─> Cognito sends verification code
   └─> User enters 6-digit code

4. Fitness assessment (5 questions)
   Q1: "What's your fitness experience?"
       [Beginner] [Intermediate] [Advanced]
   Q2: "What's your primary goal?"
       [Lose Weight] [Build Muscle] [Get Fit] [Other]
   Q3: "What equipment do you have?"
       [None] [Dumbbells] [Full Gym]
   Q4: "How many days/week can you workout?"
       [2-3] [4-5] [6-7]
   Q5: "How long per workout?"
       [20-30 min] [30-45 min] [45-60 min] [60+ min]

5. Body metrics input
   └─> Weight, Height, Age, Gender
   └─> Optional: Take "before" photo

6. AI generates personalized plan
   └─> Loading animation: "Claude is creating your plan..."
   └─> Progress bar: Analyzing goals → Selecting exercises → Building schedule
   └─> Duration: ~10-15 seconds (Bedrock API call)

7. Plan preview
   └─> Show week 1 schedule
   └─> "Start Today" button

8. Dashboard
   └─> User lands on home screen
   └─> Next workout highlighted
```

### Flow 2: Quick Workout Logging (< 30 seconds)

```
1. User opens app on workout day
   └─> Display: Big "Start Today's Workout" button
   └─> Shows: Chest & Triceps • 45 min • 6 exercises

2. User taps "Start Workout"
   └─> Timer begins
   └─> First exercise displayed: Bench Press • 4 sets x 8-12 reps

3. For each set:
   └─> User does the set
   └─> User inputs: Reps completed, Weight used
   └─> Quick input: Swipe up/down to adjust numbers
   └─> Tap "✓" when done
   └─> Rest timer starts (90 seconds)
   └─> Skip button if needed

4. Between exercises:
   └─> "Great job! 💪" micro-animation
   └─> Next exercise preview
   └─> Water break reminder

5. Finish workout:
   └─> "How did you feel?" [Mood selector]
   └─> Optional notes (voice input available via Transcribe)
   └─> Tap "Complete Workout"

6. Celebration screen:
   └─> Confetti animation 🎉
   └─> Stats: Duration, Calories, Volume lifted
   └─> "7-day streak!" badge
   └─> Share to social (optional)

7. Return to dashboard:
   └─> Workout logged
   └─> Progress chart updates
   └─> Next workout unlocked
```

### Flow 3: AI Plan Adaptation

```
1. User completes Week 2
   └─> DynamoDB Stream triggers analytics Lambda

2. Analytics Lambda analyzes performance:
   └─> Completion rate: 85%
   └─> Weight progression: Good
   └─> Missed exercises: 2 (both leg day)
   └─> Mood average: "tired"

3. EventBridge triggers adaptation check:
   └─> If completion < 70%: Suggest lighter plan
   └─> If completion > 90%: Suggest progression
   └─> If specific exercises skipped: Suggest alternatives

4. Lambda invokes Bedrock (Claude):
   └─> Prompt: "User is doing well but struggling with leg days.
                Suggest modifications..."
   └─> Claude generates: Alternative leg exercises, reduce volume

5. User receives notification:
   └─> "Your plan has been updated based on your progress!"
   └─> Shows: What changed and why
   └─> Option to accept or keep original

6. User accepts:
   └─> Plan updated in DynamoDB
   └─> Week 3 reflects new exercises
```

---

## 8. AWS Tech Stack (Complete)

### Frontend
- **AWS Amplify Hosting**
  - React Native mobile app (iOS + Android)
  - React web app
  - Automatic deployments from Git
  - Custom domain: app.fitgenius.com
  - SSL certificate (ACM)

- **Amazon CloudFront**
  - Global CDN for static assets
  - Edge caching
  - HTTPS enforcement
  - AWS Shield Standard (DDoS protection)

### Backend
- **AWS Lambda** (Node.js 20.x)
  - auth-register (512 MB, 10s timeout)
  - auth-login (512 MB, 10s timeout)
  - auth-refresh (256 MB, 3s timeout)
  - user-get-profile (256 MB, 3s timeout)
  - user-update-profile (512 MB, 5s timeout)
  - workout-create (512 MB, 5s timeout)
  - workout-list (512 MB, 5s timeout)
  - plan-generate (2048 MB, 30s timeout) ← Bedrock calls
  - plan-adapt (2048 MB, 30s timeout)
  - analytics-charts (1024 MB, 10s timeout)
  - photo-upload (1024 MB, 15s timeout)
  - analytics-processor (1024 MB, 60s timeout) ← DynamoDB Streams

### API Layer
- **Amazon API Gateway** (REST API)
  - Regional endpoint (us-east-1)
  - Custom domain: api.fitgenius.com
  - Rate limiting: 10,000 req/sec burst, 5,000 steady
  - Per-user rate limit: 100 req/min
  - CORS enabled
  - Request validation
  - CloudWatch logging

### Authentication
- **Amazon Cognito User Pools**
  - Email/password authentication
  - Social login: Google, Apple Sign-In
  - MFA (optional, SMS via SNS)
  - Password policies: 8+ chars, mixed case, numbers
  - Account recovery via email
  - JWT token expiration: 1 hour
  - Refresh token: 30 days

### Database
- **Amazon DynamoDB**
  - Users table (On-Demand)
  - Workouts table (On-Demand)
  - WorkoutPlans table (On-Demand)
  - ExerciseLibrary table (Provisioned: 10 RCU, 5 WCU)
  - ProgressPhotos table (On-Demand)
  - Point-in-time recovery enabled
  - Encryption at rest (AWS managed keys)
  - DynamoDB Streams enabled on Workouts table

### AI/ML
- **AWS Bedrock**
  - Model: Claude 3.5 Sonnet
  - Use cases:
    - Workout plan generation
    - Plan adaptation based on feedback
    - Exercise substitution suggestions
    - Motivational messages
  - Guardrails: Enabled (filter harmful content)
  - Estimated usage: 50k tokens/day

- **Amazon Rekognition**
  - DetectLabels for progress photos
  - Content moderation (filter inappropriate images)

- **Amazon Transcribe**
  - Real-time transcription for voice workout logging
  - Medical vocabulary for fitness terms

### Storage
- **Amazon S3**
  - fitgenius-user-photos-prod
    - Lifecycle: Archive to Glacier after 90 days
    - Versioning: Disabled
    - Public access: Blocked (use CloudFront)
  - fitgenius-exercise-media-prod
    - Lifecycle: Standard storage (frequently accessed)
    - Versioning: Enabled
  - fitgenius-app-assets-prod
  - fitgenius-analytics-data-lake-prod
    - Parquet files from Athena queries

### Content Delivery
- **Amazon CloudFront**
  - Distribution for S3 buckets
  - Edge locations: Global
  - Cache behavior: 1 day for images, 1 week for videos
  - SSL/TLS: ACM certificate

### Analytics & Monitoring
- **Amazon Kinesis Data Firehose**
  - Ingest workout events from DynamoDB Streams
  - Batch and deliver to S3 data lake
  - Buffer: 60 seconds or 1 MB

- **Amazon Athena**
  - Query workout data in S3
  - Tables: workouts, users, plans
  - Saved queries for common analytics

- **Amazon CloudWatch**
  - Lambda logs and metrics
  - API Gateway metrics
  - Custom metrics: Workout completions, AI plan generations
  - Alarms: Error rate > 1%, Latency > 3s

- **AWS X-Ray**
  - Distributed tracing for Lambda functions
  - Performance bottleneck identification

### Security
- **AWS WAF**
  - Attached to API Gateway
  - Rules:
    - Rate limiting (100 req/5min per IP)
    - Block known bad IPs (AWS Managed Rules)
    - SQL injection protection
    - XSS protection

- **AWS Secrets Manager**
  - Store API keys for third-party services
  - Auto-rotation enabled

- **AWS KMS**
  - Encrypt DynamoDB tables
  - Encrypt S3 objects
  - Encrypt Secrets Manager secrets

### Messaging & Events
- **Amazon EventBridge**
  - Custom events:
    - workout.completed
    - plan.generated
    - photo.uploaded
  - Rules:
    - Weekly plan adaptation check
    - Monthly billing events

- **Amazon SNS**
  - Email notifications
  - SMS for MFA
  - Mobile push notifications (FCM/APNS)

### CI/CD
- **AWS Amplify** (Frontend)
  - Git-based deployments
  - Preview environments for PRs

- **AWS SAM or CDK** (Backend)
  - Infrastructure as Code
  - Deploy Lambda functions
  - CloudFormation stacks

- **AWS CodePipeline** (Optional)
  - Source: GitHub
  - Build: CodeBuild
  - Deploy: SAM deploy

---

## 9. Success Metrics

### User Engagement KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| DAU/MAU Ratio | > 0.3 | CloudWatch custom metric |
| Avg Workouts/Week | 3+ | Athena query on workouts table |
| 7-Day Retention | > 40% | Cohort analysis (Athena) |
| 30-Day Retention | > 25% | Cohort analysis |
| Avg Session Duration | > 5 min | CloudWatch |
| Workout Completion Rate | > 60% | Workouts.completed / Workouts.started |
| Plan Completion Rate (4 weeks) | > 50% | Plans analysis |
| Photo Upload Rate | > 20% of users | ProgressPhotos count |

### Technical Performance KPIs

| Metric | Target | Monitoring |
|--------|--------|------------|
| API Response Time (p95) | < 200ms | CloudWatch API Gateway metrics |
| API Response Time (p99) | < 500ms | CloudWatch API Gateway metrics |
| Lambda Cold Start (p95) | < 1s | X-Ray |
| DynamoDB Read Latency | < 10ms | CloudWatch DynamoDB metrics |
| Bedrock Plan Generation | < 15s | Lambda duration metric |
| App Crash Rate | < 0.1% | Amplify analytics |
| API Error Rate | < 0.5% | CloudWatch |
| S3 Upload Success Rate | > 99.9% | CloudWatch S3 metrics |

### Business Metrics

| Metric | Target | Source |
|--------|--------|--------|
| Free-to-Pro Conversion | > 5% | DynamoDB subscription status |
| Monthly Churn Rate | < 8% | Subscription cancellations |
| NPS Score | > 50 | In-app survey |
| Customer Acquisition Cost | < $10 | Marketing spend / new users |
| Lifetime Value (LTV) | > $120 | Revenue per user over 12 months |
| Monthly Recurring Revenue | $50k (Year 1) | Stripe/payment data |

### AI-Specific Metrics

| Metric | Target | Monitoring |
|--------|--------|------------|
| AI Plan Acceptance Rate | > 80% | Users who start generated plan |
| Plan Adaptation Trigger Rate | 30% | Weekly adaptations / total users |
| AI Plan Quality Score | > 4.0/5.0 | User ratings |
| Bedrock Token Usage | < 100k tokens/day | CloudWatch custom metric |
| AI Generation Errors | < 1% | Lambda error logs |

---

## 10. AWS Cost Estimate

### Monthly Cost Breakdown (1,000 Active Users)

#### Compute & Backend
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **AWS Lambda** | 2M invocations, 500ms avg, 512MB avg | $8.50 |
| **API Gateway** | 2M requests | $7.00 |
| **EventBridge** | 100k events | $1.00 |
| **Step Functions** | 10k executions (plan generation) | $0.25 |
| **SUBTOTAL** | | **$16.75** |

#### Database & Storage
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **DynamoDB** | 10M reads, 2M writes (On-Demand) | $15.00 |
| **S3 Storage** | 100 GB (photos + media) | $2.30 |
| **S3 Requests** | 1M PUTs, 5M GETs | $5.50 |
| **CloudFront** | 500 GB transfer, 10M requests | $50.00 |
| **SUBTOTAL** | | **$72.80** |

#### AI/ML
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **Bedrock (Claude 3.5 Sonnet)** | 50k tokens/day input, 200k output | $180.00 |
| **Rekognition** | 10k image analyses | $10.00 |
| **Transcribe** | 100 hours audio | $24.00 |
| **SUBTOTAL** | | **$214.00** |

#### Authentication & Security
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **Cognito** | 1,000 MAUs | $0 (free tier) |
| **WAF** | 1 ACL, 10M requests | $5.00 |
| **Secrets Manager** | 5 secrets | $2.00 |
| **KMS** | 10k requests | $0.03 |
| **SUBTOTAL** | | **$7.03** |

#### Analytics & Monitoring
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **Kinesis Firehose** | 10 GB ingested | $0.35 |
| **Athena** | 100 GB scanned | $5.00 |
| **CloudWatch Logs** | 10 GB ingested, 5 GB stored | $6.00 |
| **CloudWatch Metrics** | Custom metrics | $3.00 |
| **X-Ray** | 100k traces | $0.50 |
| **SUBTOTAL** | | **$14.85** |

#### Hosting & CDN
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **Amplify Hosting** | Build minutes + hosting | $12.00 |
| **Route 53** | 2 hosted zones | $1.00 |
| **ACM Certificates** | 2 certs | $0 (free) |
| **SUBTOTAL** | | **$13.00** |

#### Messaging
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **SNS** | 100k notifications | $0.50 |
| **SES** | 10k emails | $1.00 |
| **SUBTOTAL** | | **$1.50** |

### **TOTAL MONTHLY COST (1,000 users): ~$340**

### Cost at Scale

| Users | Monthly Cost | Cost/User |
|-------|--------------|-----------|
| 100 | $120 | $1.20 |
| 1,000 | $340 | $0.34 |
| 10,000 | $1,800 | $0.18 |
| 100,000 | $12,000 | $0.12 |

### Cost Optimization Strategies

1. **Bedrock Tokens**: Use caching for similar plan requests (-30%)
2. **Lambda**: Use ARM64 architecture (-20% compute cost)
3. **DynamoDB**: Use reserved capacity for predictable load (-50%)
4. **CloudFront**: Use Reserved Capacity for high traffic (-25%)
5. **S3**: Implement lifecycle policies to Glacier (-75% for old photos)
6. **Savings Plans**: 1-year commitment (-20% overall)

**Optimized Cost**: ~$250/month for 1,000 users

---

## 11. Timeline Estimate

### Phase 1: MVP (12 weeks)

**Week 1-2: Setup & Infrastructure**
- AWS account setup
- Amplify app configuration
- Cognito user pool creation
- DynamoDB table design & creation
- API Gateway setup
- IAM roles & policies
- CI/CD pipeline (SAM/CDK)

**Week 3-4: Authentication & User Management**
- Lambda functions: auth-*, user-*
- Cognito integration
- Frontend: Login/register screens
- Email verification flow
- Profile management

**Week 5-7: Workout Logging**
- Exercise library seeding (DynamoDB)
- Lambda functions: workout-*
- Frontend: Workout logging UI
- Timer functionality
- Quick-log optimizations

**Week 8-9: AI Plan Generation**
- Bedrock integration
- Lambda: plan-generate
- Prompt engineering & testing
- Frontend: Plan display
- Schedule visualization

**Week 10-11: Progress Tracking**
- Lambda: analytics-*, photo-upload
- S3 + Rekognition integration
- DynamoDB Streams → Firehose setup
- Charts & visualization
- Badge system

**Week 12: Testing & Launch**
- End-to-end testing
- Load testing (Artillery or k6)
- Security review
- Beta launch (100 users)
- Monitoring dashboards

### Phase 2: Enhanced Features (8 weeks)

**Week 13-14: Nutrition Tracking**
- Food database integration
- Calorie/macro logging
- Rekognition for food photos

**Week 15-16: Social Features**
- Friend system (DynamoDB GSI)
- Workout sharing
- Challenge system (Step Functions)

**Week 17-18: Wearable Integration**
- Apple HealthKit SDK
- Fitbit API integration
- Data sync Lambda

**Week 19-20: Polish & Optimization**
- Performance tuning
- Cost optimization
- UX improvements
- A/B testing (Amplify Experiments)

### Phase 3: Advanced Features (8 weeks)
- Video form analysis (Rekognition Custom Labels)
- Live trainer sessions (IVS)
- Marketplace

**Total Timeline: 28 weeks (7 months) to full product**
**MVP Launch: 12 weeks (3 months)**

---

## Appendix: AWS Well-Architected Alignment

This architecture follows AWS Well-Architected Framework pillars:

✅ **Operational Excellence**: CloudWatch, X-Ray, automated deployments
✅ **Security**: Cognito, WAF, encryption at rest/transit, IAM least privilege
✅ **Reliability**: Multi-AZ (Lambda, DynamoDB), auto-scaling, retries
✅ **Performance Efficiency**: Lambda, DynamoDB On-Demand, CloudFront CDN
✅ **Cost Optimization**: Serverless, pay-per-use, S3 lifecycle policies
✅ **Sustainability**: Serverless reduces idle resources

---

**Document Version**: 1.0
**Last Updated**: November 8, 2025
**Generated By**: Claude Code PRD Assistant (AWS-Focused)
**Ready for**: Development kickoff, stakeholder review, cost approval
