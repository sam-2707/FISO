import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.subscriptions = new Map();
    this.baseURL = 'http://localhost:5001';
  }

  connect() {
    if (this.socket) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      try {
        this.socket = io(this.baseURL, {
          transports: ['websocket', 'polling'],
          timeout: 10000,
          reconnection: true,
          reconnectionAttempts: 5,
          reconnectionDelay: 1000
        });

        this.socket.on('connect', () => {
          console.log('✅ WebSocket connected to FISO Real-Time Server');
          this.isConnected = true;
          resolve();
        });

        this.socket.on('disconnect', () => {
          console.log('❌ WebSocket disconnected');
          this.isConnected = false;
        });

        this.socket.on('connect_error', (error) => {
          console.error('❌ WebSocket connection error:', error);
          this.isConnected = false;
          reject(error);
        });

        this.socket.on('connection_established', (data) => {
          console.log('🎯 Connection established:', data);
        });

        // Handle real-time data streams
        this.socket.on('pricing_update', (data) => {
          this.notifySubscribers('pricing_update', data);
        });

        this.socket.on('cost_alert', (data) => {
          this.notifySubscribers('cost_alert', data);
        });

        this.socket.on('ai_prediction', (data) => {
          this.notifySubscribers('ai_prediction', data);
        });

        this.socket.on('anomaly_detection', (data) => {
          this.notifySubscribers('anomaly_detection', data);
        });

        this.socket.on('subscription_confirmed', (data) => {
          console.log(`✅ Subscribed to stream: ${data.stream_type}`);
        });

        this.socket.on('unsubscription_confirmed', (data) => {
          console.log(`❌ Unsubscribed from stream: ${data.stream_type}`);
        });

      } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
        reject(error);
      }
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      this.subscriptions.clear();
      console.log('🔌 WebSocket disconnected');
    }
  }

  subscribeToStream(streamType, callback) {
    if (!this.isConnected) {
      console.warn('WebSocket not connected. Attempting to connect...');
      this.connect().then(() => {
        this.subscribeToStream(streamType, callback);
      });
      return;
    }

    // Store subscription callback
    if (!this.subscriptions.has(streamType)) {
      this.subscriptions.set(streamType, new Set());
    }
    this.subscriptions.get(streamType).add(callback);

    // Send subscription request to server
    this.socket.emit('subscribe_to_stream', { stream_type: streamType });

    console.log(`📡 Subscribed to stream: ${streamType}`);
  }

  unsubscribeFromStream(streamType, callback) {
    if (!this.isConnected || !this.subscriptions.has(streamType)) {
      return;
    }

    const callbacks = this.subscriptions.get(streamType);
    if (callback) {
      callbacks.delete(callback);
      if (callbacks.size === 0) {
        this.subscriptions.delete(streamType);
        this.socket.emit('unsubscribe_from_stream', { stream_type: streamType });
      }
    } else {
      // Unsubscribe all callbacks for this stream
      this.subscriptions.delete(streamType);
      this.socket.emit('unsubscribe_from_stream', { stream_type: streamType });
    }

    console.log(`📡 Unsubscribed from stream: ${streamType}`);
  }

  notifySubscribers(streamType, data) {
    if (this.subscriptions.has(streamType)) {
      this.subscriptions.get(streamType).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in stream callback for ${streamType}:`, error);
        }
      });
    }
  }

  // Convenience methods for specific streams
  subscribeToPricingUpdates(callback) {
    this.subscribeToStream('pricing_updates', callback);
  }

  subscribeToCostAlerts(callback) {
    this.subscribeToStream('cost_alerts', callback);
  }

  subscribeToAIPredictions(callback) {
    this.subscribeToStream('ai_predictions', callback);
  }

  subscribeToAnomalyDetection(callback) {
    this.subscribeToStream('anomaly_detection', callback);
  }

  // Get connection status
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      activeSubscriptions: Array.from(this.subscriptions.keys()),
      serverURL: this.baseURL
    };
  }

  // Send custom events to server
  sendEvent(eventName, data) {
    if (this.isConnected && this.socket) {
      this.socket.emit(eventName, data);
    } else {
      console.warn('Cannot send event: WebSocket not connected');
    }
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;