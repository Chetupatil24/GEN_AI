# 🔌 Railway Remote Connection Guide
## Connect to Railway Like SSH

Complete guide to connect and manage your Railway project remotely via CLI.

## 🚀 Quick Start

### Step 1: Install Railway CLI

```bash
# Install Railway CLI globally
npm i -g @railway/cli

# Verify installation
railway --version
```

### Step 2: Login to Railway

```bash
# Login (opens browser for authentication)
railway login

# Verify you're logged in
railway whoami
```

### Step 3: Connect to Your Project

```bash
# Link to your project (like SSH connection)
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

# Or if you're in the project directory
cd /home/chetan-patil/myprojects/1/GEN_AI
railway link
```

### Step 4: You're Connected!

Now you can manage your Railway project remotely, just like SSH.

## 📋 Common Remote Commands

### View Project Status

```bash
# Check project status
railway status

# View project info
railway whoami
```

### Manage Environment Variables

```bash
# List all variables
railway variables

# Get specific variable
railway variables get FAL_API_KEY

# Set a variable
railway variables set FAL_API_KEY="your-key-here"

# Delete a variable
railway variables delete VARIABLE_NAME
```

### View Logs (Like `tail -f`)

```bash
# View live logs (like SSH tail)
railway logs

# View last N lines
railway logs --tail 50

# Follow logs (real-time)
railway logs --follow
```

### Deploy & Manage

```bash
# Deploy current code
railway up

# Open project in browser
railway open

# View deployments
railway deployments
```

### Run Commands Remotely

```bash
# Run shell command in Railway environment
railway run bash

# Run Python command
railway run python --version

# Run any command
railway run <your-command>
```

## 🔧 Complete Remote Management Workflow

### Daily Workflow (Like SSH)

```bash
# 1. Connect to project
cd /home/chetan-patil/myprojects/1/GEN_AI
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

# 2. Check status
railway status

# 3. View logs (like SSH tail)
railway logs --tail 100

# 4. Check variables
railway variables

# 5. Set/update variables if needed
railway variables set FAL_API_KEY="new-key"

# 6. Deploy changes
railway up

# 7. Monitor deployment
railway logs --follow
```

## 🎯 Step-by-Step: First Time Setup

### Complete Setup Process

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login
# (Browser will open - authenticate)

# 3. Navigate to project
cd /home/chetan-patil/myprojects/1/GEN_AI

# 4. Link project
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

# 5. Set all required variables
railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a"
railway variables set FAL_BASE_URL="https://queue.fal.run"
railway variables set FAL_MODEL_ID="fal-ai/minimax-video"
railway variables set USE_REDIS="true"
railway variables set VIDEO_STORAGE_PATH="storage/videos"

# 6. Verify connection
railway status

# 7. Check logs
railway logs --tail 50

# 8. Deploy
railway up
```

## 📊 Monitoring & Debugging (Like SSH)

### Real-time Monitoring

```bash
# Watch logs in real-time (like SSH tail -f)
railway logs --follow

# Check specific service
railway logs --service <service-name>

# Filter logs
railway logs | grep ERROR
```

### Debugging Commands

```bash
# Check environment
railway run env | grep FAL

# Check Python version
railway run python --version

# Check installed packages
railway run pip list

# Run interactive shell
railway run bash
```

## 🔐 Security & Authentication

### Login Methods

```bash
# Browser login (default)
railway login

# Token login (for CI/CD)
railway login --browserless

# Check current user
railway whoami

# Logout
railway logout
```

## 🛠️ Advanced Remote Operations

### Project Management

```bash
# List all projects
railway list

# Switch between projects
railway link <project-id>

# View project details
railway status

# Open project dashboard
railway open
```

### Environment Management

```bash
# List environments
railway environments

# Switch environment
railway environment <env-id>

# Create new environment
railway environment create production
```

### Service Management

```bash
# List services
railway services

# View service logs
railway logs --service <service-name>

# Restart service
railway restart
```

## 📝 Quick Reference Card

```bash
# Connection
railway login                    # Login to Railway
railway link <project-id>        # Connect to project
railway whoami                   # Check current user

# Status & Info
railway status                   # Project status
railway variables                # List variables
railway deployments              # View deployments

# Logs
railway logs                     # View logs
railway logs --tail 100          # Last 100 lines
railway logs --follow            # Follow logs

# Variables
railway variables set KEY="val"  # Set variable
railway variables get KEY        # Get variable
railway variables delete KEY     # Delete variable

# Deployment
railway up                       # Deploy
railway open                     # Open dashboard

# Remote Execution
railway run <command>            # Run command remotely
railway run bash                 # Interactive shell
```

## 🎯 Common Use Cases

### Use Case 1: Quick Status Check

```bash
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
railway status
railway logs --tail 20
```

### Use Case 2: Update Environment Variables

```bash
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
railway variables set FAL_API_KEY="new-key"
railway up  # Redeploy with new variables
```

### Use Case 3: Debug Production Issue

```bash
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
railway logs --follow | grep ERROR
railway run python -c "import app; print('OK')"
```

### Use Case 4: Deploy Latest Code

```bash
cd /home/chetan-patil/myprojects/1/GEN_AI
git push origin main  # Push to GitHub
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
railway up  # Deploy to Railway
railway logs --follow  # Monitor deployment
```

## 🔄 Comparison: SSH vs Railway CLI

| SSH Command | Railway CLI Equivalent |
|-------------|------------------------|
| `ssh user@host` | `railway link <project-id>` |
| `tail -f /var/log/app.log` | `railway logs --follow` |
| `cat /etc/environment` | `railway variables` |
| `export VAR=value` | `railway variables set VAR=value` |
| `systemctl status app` | `railway status` |
| `systemctl restart app` | `railway restart` |
| `cd /app && git pull` | `railway up` |

## ✅ Verification Checklist

After connecting remotely:

- [ ] `railway whoami` shows your username
- [ ] `railway status` shows project is active
- [ ] `railway variables` shows all required variables
- [ ] `railway logs` shows application logs
- [ ] `railway open` opens Railway dashboard

## 🚨 Troubleshooting

### Issue: "Not logged in"

```bash
railway login
```

### Issue: "Project not linked"

```bash
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
```

### Issue: "Command not found"

```bash
npm i -g @railway/cli
```

### Issue: "Permission denied"

- Check you're logged in: `railway whoami`
- Verify project access in Railway dashboard

## 📞 Help & Support

- **Railway CLI Docs**: https://docs.railway.app/develop/cli
- **Railway Dashboard**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
- **GitHub Issues**: https://github.com/Chetupatil24/GEN_AI/issues

---

**You're now ready to manage Railway remotely, just like SSH! 🚀**
