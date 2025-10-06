# FISO Full Stack Startup Scripts

This directory contains several startup scripts to easily launch both the frontend and backend components of the FISO platform.

## Available Scripts

### 1. PowerShell Script (Recommended for Windows)
```powershell
.\start-fiso.ps1
```

**Features:**
- Full dependency checking and installation
- Background job management
- Colored output with emojis
- Graceful shutdown handling
- Flexible parameter options

**Usage Examples:**
```powershell
# Start both frontend and backend in development mode
.\start-fiso.ps1

# Start in production mode
.\start-fiso.ps1 -Mode prod

# Start only frontend
.\start-fiso.ps1 -Frontend

# Start only backend with custom port
.\start-fiso.ps1 -Backend -Port 8080

# Custom ports for both services
.\start-fiso.ps1 -Port 8080 -FrontendPort 3001
```

### 2. Batch Script (Traditional Windows)
```batch
start-fiso.bat
```

**Features:**
- Traditional Windows batch file
- Opens services in separate command windows
- Simple command-line argument parsing
- Colored output using PowerShell

**Usage Examples:**
```batch
# Start both services
start-fiso.bat

# Start in production mode
start-fiso.bat --prod

# Custom ports
start-fiso.bat --backend-port 8080 --frontend-port 3001
```

### 3. Node.js Script (Cross-platform)
```bash
node start-fiso.js
```

**Features:**
- Cross-platform compatibility (Windows, macOS, Linux)
- Promise-based async execution
- Detailed error handling
- Concurrent service management

**Usage Examples:**
```bash
# Start both services
node start-fiso.js

# Start in production mode
node start-fiso.js --prod

# Start only frontend
node start-fiso.js --frontend

# Custom ports
node start-fiso.js --backend-port 8080 --frontend-port 3001
```

### 4. NPM Scripts
```bash
npm start              # Start both services in development mode
npm run start:dev      # Start both services in development mode
npm run start:prod     # Start both services in production mode
npm run start:frontend # Start only frontend
npm run start:backend  # Start only backend
npm run fullstack      # Start both services (alias for npm start)
npm run fullstack:prod # Start both services in production mode
```

## Default Configuration

- **Backend Port:** 5000
- **Frontend Port:** 3000
- **Mode:** Development
- **Environment:** Automatically configured based on mode

## Prerequisites

### Required Software
- **Node.js** (v14 or higher) - Download from [nodejs.org](https://nodejs.org/)
- **Python** (v3.8 or higher) - Download from [python.org](https://python.org/)
- **npm** (comes with Node.js)
- **pip** (comes with Python)

### Optional (for PowerShell script)
- **PowerShell 5.1+** (included in Windows 10/11)
- **PowerShell Core 7+** (for enhanced cross-platform support)

## Automatic Features

All scripts automatically:

1. **Check system requirements** (Node.js, Python)
2. **Install missing dependencies** (npm packages, pip packages)
3. **Set environment variables** based on mode
4. **Start both services** with proper configuration
5. **Display service URLs** and status information
6. **Handle graceful shutdown** (where supported)

## Service URLs

Once started, you can access:

- **Frontend Dashboard:** http://localhost:3000 (or custom frontend port)
- **Backend API:** http://localhost:5000 (or custom backend port)
- **API Documentation:** http://localhost:5000/docs (if available)

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Use custom ports: `--backend-port 8080 --frontend-port 3001`
   - Check what's using the port: `netstat -ano | findstr :5000`

2. **Missing Dependencies**
   - Run `npm install` in root directory
   - Run `npm install` in frontend directory
   - Install Python requirements: `pip install -r requirements-production.txt`

3. **Permission Issues**
   - Run PowerShell as Administrator if needed
   - Check execution policy: `Get-ExecutionPolicy`
   - Set policy if needed: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

4. **Python/Node.js Not Found**
   - Ensure both are installed and in your PATH
   - Restart your terminal after installation
   - Verify with: `python --version` and `node --version`

### Logs and Debugging

- Backend logs are typically in the `logs/` directory
- Frontend development server shows logs in the console
- Check browser developer tools for frontend issues
- Use `--verbose` flag if available for detailed output

## Development vs Production Mode

### Development Mode
- Hot reloading enabled
- Source maps available
- Detailed error messages
- Development-optimized builds

### Production Mode
- Optimized builds
- Minified assets
- Production error handling
- Performance optimizations

## Stopping the Services

### PowerShell Script
- Press `Ctrl+C` in the terminal (stops both services gracefully)

### Batch Script
- Close the individual command windows for frontend/backend

### Node.js Script
- Press `Ctrl+C` in the terminal (stops both services)

### Manual Stop
- Find processes: `tasklist | findstr node` and `tasklist | findstr python`
- Kill processes: `taskkill /PID <process_id> /F`

## Contributing

When modifying the startup scripts:

1. Test on multiple environments (dev/prod modes)
2. Ensure proper error handling
3. Update this README with any new features
4. Test dependency installation flows
5. Verify graceful shutdown behavior