#!/usr/bin/env node
/**
 * FISO Full Stack Startup Script (Node.js Version)
 * Cross-platform launcher for both frontend and backend components
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const config = {
    backendPort: 5000,
    frontendPort: 3000,
    mode: 'dev'
};

// Colors for console output
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    cyan: '\x1b[36m'
};

// Helper functions
function colorLog(color, message) {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function info(message) {
    colorLog('cyan', `ℹ️  ${message}`);
}

function success(message) {
    colorLog('green', `✅ ${message}`);
}

function error(message) {
    colorLog('red', `❌ ${message}`);
}

function warning(message) {
    colorLog('yellow', `⚠️  ${message}`);
}

// Parse command line arguments
function parseArgs() {
    const args = process.argv.slice(2);
    const options = {
        mode: 'dev',
        backendPort: 5000,
        frontendPort: 3000,
        help: false,
        frontend: false,
        backend: false
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--dev':
                options.mode = 'dev';
                break;
            case '--prod':
                options.mode = 'prod';
                break;
            case '--backend-port':
                options.backendPort = parseInt(args[++i]);
                break;
            case '--frontend-port':
                options.frontendPort = parseInt(args[++i]);
                break;
            case '--frontend':
                options.frontend = true;
                break;
            case '--backend':
                options.backend = true;
                break;
            case '--help':
            case '-h':
                options.help = true;
                break;
        }
    }

    return options;
}

// Show help message
function showHelp() {
    console.log(`
FISO Full Stack Startup Script
===============================

Usage: node start-fiso.js [options]

Options:
  --dev              Start in development mode (default)
  --prod             Start in production mode
  --backend-port N   Set backend port (default: 5000)
  --frontend-port N  Set frontend port (default: 3000)
  --frontend         Start only frontend
  --backend          Start only backend
  --help, -h         Show this help message

Examples:
  node start-fiso.js
  node start-fiso.js --prod
  node start-fiso.js --backend-port 8080 --frontend-port 3001
  node start-fiso.js --frontend
`);
}

// Check if command exists
function commandExists(command) {
    return new Promise((resolve) => {
        exec(`${command} --version`, (error) => {
            resolve(!error);
        });
    });
}

// Install dependencies
async function installDependencies() {
    info('Checking and installing dependencies...');

    // Check Python dependencies
    if (fs.existsSync('requirements-production.txt')) {
        info('Installing Python dependencies...');
        const pipProcess = spawn('pip', ['install', '-r', 'requirements-production.txt'], {
            stdio: 'inherit'
        });

        await new Promise((resolve, reject) => {
            pipProcess.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error('Failed to install Python dependencies'));
                }
            });
        });
    }

    // Install root Node.js dependencies
    if (fs.existsSync('package.json')) {
        info('Installing root Node.js dependencies...');
        const npmProcess = spawn('npm', ['install'], {
            stdio: 'inherit'
        });

        await new Promise((resolve, reject) => {
            npmProcess.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error('Failed to install root Node.js dependencies'));
                }
            });
        });
    }

    // Install frontend dependencies
    if (fs.existsSync('frontend/package.json')) {
        info('Installing frontend dependencies...');
        const frontendNpmProcess = spawn('npm', ['install'], {
            cwd: 'frontend',
            stdio: 'inherit'
        });

        await new Promise((resolve, reject) => {
            frontendNpmProcess.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error('Failed to install frontend dependencies'));
                }
            });
        });
    }

    success('All dependencies installed successfully!');
}

// Start backend server
function startBackend(port, mode) {
    return new Promise((resolve, reject) => {
        info(`Starting FISO Backend Server on port ${port}...`);

        const env = {
            ...process.env,
            PORT: port.toString(),
            FLASK_ENV: mode === 'dev' ? 'development' : 'production'
        };

        const backendProcess = spawn('python', ['production_server.py'], {
            env,
            stdio: 'inherit'
        });

        backendProcess.on('error', (err) => {
            error(`Backend server error: ${err.message}`);
            reject(err);
        });

        backendProcess.on('close', (code) => {
            if (code !== 0) {
                error(`Backend server exited with code ${code}`);
                reject(new Error(`Backend process exited with code ${code}`));
            } else {
                resolve();
            }
        });

        // Give the backend a moment to start
        setTimeout(() => {
            success(`Backend server started on port ${port}`);
        }, 2000);
    });
}

// Start frontend server
function startFrontend(port, mode) {
    return new Promise((resolve, reject) => {
        info(`Starting FISO Frontend Server on port ${port}...`);

        const env = {
            ...process.env,
            PORT: port.toString()
        };

        let command, args;
        if (mode === 'dev') {
            command = 'npm';
            args = ['start'];
        } else {
            // For production, build first then serve
            info('Building frontend for production...');
            const buildProcess = spawn('npm', ['run', 'build'], {
                cwd: 'frontend',
                stdio: 'inherit'
            });

            buildProcess.on('close', (buildCode) => {
                if (buildCode === 0) {
                    info('Serving built frontend...');
                    const serveProcess = spawn('npx', ['serve', '-s', 'build', '-l', port.toString()], {
                        cwd: 'frontend',
                        env,
                        stdio: 'inherit'
                    });

                    serveProcess.on('error', reject);
                    serveProcess.on('close', (code) => {
                        if (code !== 0) {
                            reject(new Error(`Serve process exited with code ${code}`));
                        } else {
                            resolve();
                        }
                    });
                } else {
                    reject(new Error('Frontend build failed'));
                }
            });
            return;
        }

        const frontendProcess = spawn(command, args, {
            cwd: 'frontend',
            env,
            stdio: 'inherit'
        });

        frontendProcess.on('error', (err) => {
            error(`Frontend server error: ${err.message}`);
            reject(err);
        });

        frontendProcess.on('close', (code) => {
            if (code !== 0) {
                error(`Frontend server exited with code ${code}`);
                reject(new Error(`Frontend process exited with code ${code}`));
            } else {
                resolve();
            }
        });

        // Give the frontend a moment to start
        setTimeout(() => {
            success(`Frontend server started on port ${port}`);
        }, 3000);
    });
}

// Main function
async function main() {
    const options = parseArgs();

    if (options.help) {
        showHelp();
        return;
    }

    console.clear();
    info('FISO Full Stack Startup Script');
    info('===============================');
    console.log();

    // Check if we're in the right directory
    if (!fs.existsSync('package.json') || !fs.existsSync('production_server.py')) {
        error('Please run this script from the FISO root directory');
        process.exit(1);
    }

    // Check dependencies
    info('Checking system requirements...');
    
    const nodeExists = await commandExists('node');
    const pythonExists = await commandExists('python');

    if (!nodeExists) {
        error('Node.js not found. Please install Node.js from https://nodejs.org/');
        process.exit(1);
    } else {
        success('Node.js found');
    }

    if (!pythonExists) {
        error('Python not found. Please install Python from https://python.org/');
        process.exit(1);
    } else {
        success('Python found');
    }

    try {
        // Install dependencies
        await installDependencies();

        console.log();
        info('Starting FISO Platform...');
        info(`Mode: ${options.mode}`);
        info(`Backend Port: ${options.backendPort}`);
        info(`Frontend Port: ${options.frontendPort}`);
        console.log();

        // Start servers based on options
        if (options.frontend && !options.backend) {
            await startFrontend(options.frontendPort, options.mode);
        } else if (options.backend && !options.frontend) {
            await startBackend(options.backendPort, options.mode);
        } else {
            // Start both servers concurrently
            success('🚀 FISO Platform is starting up...');
            success(`📊 Frontend: http://localhost:${options.frontendPort}`);
            success(`🔧 Backend API: http://localhost:${options.backendPort}`);
            console.log();
            info('Press Ctrl+C to stop all services');
            console.log();

            await Promise.all([
                startBackend(options.backendPort, options.mode),
                startFrontend(options.frontendPort, options.mode)
            ]);
        }

    } catch (err) {
        error(`An error occurred: ${err.message}`);
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log();
    info('Shutting down FISO Platform...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log();
    info('Shutting down FISO Platform...');
    process.exit(0);
});

// Run the main function
if (require.main === module) {
    main().catch((err) => {
        error(`Fatal error: ${err.message}`);
        process.exit(1);
    });
}

module.exports = { main, parseArgs, showHelp };