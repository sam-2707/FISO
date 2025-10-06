#!/bin/bash
set -e

echo "🚀 Starting FISO Enterprise Intelligence Platform..."

# Function to handle shutdown
shutdown() {
    echo "🛑 Shutting down services..."
    if [ ! -z "$REALTIME_PID" ] && kill -0 $REALTIME_PID 2>/dev/null; then
        kill $REALTIME_PID
    fi
    if [ ! -z "$PRODUCTION_PID" ] && kill -0 $PRODUCTION_PID 2>/dev/null; then
        kill $PRODUCTION_PID
    fi
    exit 0
}

# Trap signals for graceful shutdown
trap shutdown SIGTERM SIGINT

# Database migrations (if needed)
if [ -f "migrations/migrate.py" ]; then
    echo "📊 Running database migrations..."
    python migrations/migrate.py || echo "⚠️  Migration failed or not needed"
fi

# Initialize database if needed
if [ -f "setup_db.py" ]; then
    echo "🗄️  Setting up database..."
    python setup_db.py || echo "⚠️  Database setup failed or already exists"
fi

# Initialize AI models
echo "🤖 Initializing AI models..."
python -c "
try:
    import sys
    import os
    sys.path.append('/app')
    
    # Try to import and initialize AI components
    try:
        from predictor.production_ai_engine import ProductionAIEngine
        engine = ProductionAIEngine()
        print('✅ Production AI engine initialized successfully')
    except ImportError:
        print('⚠️  Production AI engine not found, trying alternatives...')
        try:
            from predictor.lightweight_ai_engine import LightweightAIEngine
            engine = LightweightAIEngine()
            print('✅ Lightweight AI engine initialized successfully')
        except ImportError:
            print('⚠️  No AI engines found, continuing without AI features')
    except Exception as e:
        print(f'⚠️  AI engine initialization failed: {e}')
        
except Exception as e:
    print(f'⚠️  AI initialization error: {e}')
    print('📝 Continuing without AI features...')
" || echo "⚠️  AI initialization skipped"

# Create required directories
mkdir -p logs reports data

# Start services
echo "🚀 Starting services..."

# Check if real_time_server.py exists
if [ -f "real_time_server.py" ]; then
    echo "🔄 Starting real-time server..."
    python real_time_server.py &
    REALTIME_PID=$!
    echo "✅ Real-time server started (PID: $REALTIME_PID)"
else
    echo "⚠️  real_time_server.py not found, skipping real-time server"
    REALTIME_PID=""
fi

# Start main production server
if [ -f "production_server.py" ]; then
    echo "🏭 Starting production server..."
    python production_server.py &
    PRODUCTION_PID=$!
    echo "✅ Production server started (PID: $PRODUCTION_PID)"
else
    echo "❌ production_server.py not found!"
    exit 1
fi

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Health check function
health_check() {
    local url=$1
    local service_name=$2
    
    if curl -f -s "$url" >/dev/null 2>&1; then
        echo "✅ $service_name is healthy"
        return 0
    else
        echo "❌ $service_name health check failed"
        return 1
    fi
}

# Perform health checks
echo "🩺 Performing health checks..."

# Check production server
if ! health_check "http://localhost:5000/health" "Production server"; then
    # Try alternative endpoints
    if curl -f -s "http://localhost:5000/" >/dev/null 2>&1; then
        echo "✅ Production server is responding (no health endpoint)"
    else
        echo "❌ Production server is not responding"
    fi
fi

# Check real-time server if it was started
if [ ! -z "$REALTIME_PID" ]; then
    if ! health_check "http://localhost:5001/health" "Real-time server"; then
        # Try alternative endpoints
        if curl -f -s "http://localhost:5001/" >/dev/null 2>&1; then
            echo "✅ Real-time server is responding (no health endpoint)"
        else
            echo "⚠️  Real-time server health check failed"
        fi
    fi
fi

echo ""
echo "🎉 FISO Platform startup completed!"
echo "📊 Frontend: Static files served by production server"
echo "🔧 Production server: http://localhost:5000"
if [ ! -z "$REALTIME_PID" ]; then
    echo "🔄 Real-time server: http://localhost:5001"
fi
echo ""

# Keep container running and monitor processes
echo "👀 Monitoring services..."
while true; do
    # Check if production server is still running
    if [ ! -z "$PRODUCTION_PID" ] && ! kill -0 $PRODUCTION_PID 2>/dev/null; then
        echo "❌ Production server stopped unexpectedly"
        shutdown
    fi
    
    # Check if real-time server is still running (if it was started)
    if [ ! -z "$REALTIME_PID" ] && ! kill -0 $REALTIME_PID 2>/dev/null; then
        echo "⚠️  Real-time server stopped"
        # Don't exit for real-time server failure, just log it
        REALTIME_PID=""
    fi
    
    sleep 30
done