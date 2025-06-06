# 🐳 Coin Flip Simulation - Docker Edition

**🔧 ISSUE FIXED**: Added missing Flask-CORS dependency

Run the complete coin flip simulation with a single Docker command!

## 🚀 Super Easy Setup

### Prerequisites
- Docker
- Docker Compose

### One-Command Launch
```bash
docker-compose up --build
```

That's it! 🎉

## 📱 Access the Application

Once running, open your browser and go to:
**http://localhost:8080**

## 🔧 What Was Fixed

- ✅ Added `Flask-CORS==5.0.0` to requirements.txt
- ✅ Backend now properly handles CORS for frontend communication
- ✅ All services should start without errors

## 🎯 What You Get

- **1000 Parallel Sessions** running simultaneously
- **Real-time Updates** via WebSocket
- **Interactive Dashboard** with charts and visualizations
- **Pattern Configuration** (consecutive heads/tails, alternating, custom)
- **Expected Value Analysis** (theory vs actual)

## 🔧 Available Patterns

- 2, 3, 4 consecutive heads/tails
- 3, 4 alternating patterns
- Custom sequences (H-T-H, T-H-T, etc.)

## 📊 How to Use

1. **Start**: Run `docker-compose up --build`
2. **Open**: http://localhost:8080
3. **Select Pattern**: Choose from dropdown (e.g., "2 consecutive tails")
4. **Run Simulation**: Click "Start" button
5. **Watch Magic**: See 1000 sessions complete in real-time!

## 🏗 Architecture

The Docker setup includes:
- **Backend**: Flask + SocketIO + CORS (Python)
- **Frontend**: React + Tailwind CSS
- **Reverse Proxy**: Nginx (routes traffic)
- **Networking**: Internal Docker network

## 📈 Expected Values

| Pattern | Theory | Formula |
|---------|--------|---------|
| 2 consecutive tails | 6 | 2^(2+1) - 2 |
| 3 consecutive tails | 14 | 2^(3+1) - 2 |
| 4 consecutive tails | 30 | 2^(4+1) - 2 |

## 🛠 Development Commands

```bash
# Start services
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose build frontend
```

## 🔍 Service Details

- **Frontend**: http://localhost:3000 (internal)
- **Backend**: http://localhost:5000 (internal)
- **Main App**: http://localhost:8080 (public access)

## 🎲 Example Usage

1. Run: `docker-compose up --build`
2. Open: http://localhost:8080
3. Select: "2 consecutive tails"
4. Click: "Start"
5. Watch: 1000 sessions complete with real-time updates
6. Observe: Actual EV converge to theoretical value of 6 flips

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Stop any existing containers
docker-compose down

# Check what's using port 8080
lsof -i :8080

# Kill process if needed
sudo kill -9 <PID>
```

### Container Issues
```bash
# Clean rebuild
docker-compose down
docker system prune -f
docker-compose up --build
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

## 🎯 Features

- **Containerized**: No dependency issues
- **One Command**: Super easy to run
- **Real-time**: WebSocket updates
- **Modular**: Easy to extend patterns
- **Responsive**: Works on mobile and desktop
- **Statistical**: Theory vs actual analysis
- **CORS Fixed**: Proper frontend-backend communication

Enjoy exploring probability theory with Docker! 🐳🎲

# CoinFlipSimulation
