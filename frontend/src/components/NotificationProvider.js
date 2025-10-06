import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Slide,
  Fade,
  IconButton,
  Box
} from '@mui/material';
import { Close } from '@mui/icons-material';

const NotificationContext = createContext();

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

const TransitionUp = (props) => {
  return <Slide {...props} direction="up" />;
};

const TransitionLeft = (props) => {
  return <Slide {...props} direction="left" />;
};

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  // Helper function to hide notifications (defined first to avoid dependency issues)
  const hideNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const showNotification = useCallback((message, options = {}) => {
    const notification = {
      id: Date.now() + Math.random(),
      message,
      severity: options.severity || 'info',
      title: options.title,
      autoHideDuration: options.autoHideDuration !== undefined ? options.autoHideDuration : 6000,
      position: options.position || 'bottom-right',
      action: options.action,
      ...options
    };

    setNotifications(prev => [...prev, notification]);

    // Auto-hide notification
    if (notification.autoHideDuration !== null) {
      setTimeout(() => {
        hideNotification(notification.id);
      }, notification.autoHideDuration);
    }

    return notification.id;
  }, [hideNotification]);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Convenience methods
  const showSuccess = useCallback((message, options = {}) => {
    return showNotification(message, { ...options, severity: 'success' });
  }, [showNotification]);

  const showError = useCallback((message, options = {}) => {
    return showNotification(message, { 
      ...options, 
      severity: 'error',
      autoHideDuration: options.autoHideDuration !== undefined ? options.autoHideDuration : 8000
    });
  }, [showNotification]);

  const showWarning = useCallback((message, options = {}) => {
    return showNotification(message, { ...options, severity: 'warning' });
  }, [showNotification]);

  const showInfo = useCallback((message, options = {}) => {
    return showNotification(message, { ...options, severity: 'info' });
  }, [showNotification]);

  const contextValue = {
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hideNotification,
    clearAllNotifications,
    notifications
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      <NotificationContainer notifications={notifications} onClose={hideNotification} />
    </NotificationContext.Provider>
  );
};

const NotificationContainer = ({ notifications, onClose }) => {
  const groupedNotifications = notifications.reduce((groups, notification) => {
    const position = notification.position || 'bottom-right';
    if (!groups[position]) {
      groups[position] = [];
    }
    groups[position].push(notification);
    return groups;
  }, {});

  const getPositionStyles = (position) => {
    const styles = {
      position: 'fixed',
      zIndex: 1400,
      maxWidth: '90vw',
      width: 'auto',
      minWidth: '300px'
    };

    switch (position) {
      case 'top-left':
        return { ...styles, top: 24, left: 24 };
      case 'top-center':
        return { ...styles, top: 24, left: '50%', transform: 'translateX(-50%)' };
      case 'top-right':
        return { ...styles, top: 24, right: 24 };
      case 'bottom-left':
        return { ...styles, bottom: 24, left: 24 };
      case 'bottom-center':
        return { ...styles, bottom: 24, left: '50%', transform: 'translateX(-50%)' };
      case 'bottom-right':
      default:
        return { ...styles, bottom: 24, right: 24 };
    }
  };

  return (
    <>
      {Object.entries(groupedNotifications).map(([position, positionNotifications]) => (
        <Box key={position} sx={getPositionStyles(position)}>
          {positionNotifications.map((notification, index) => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onClose={onClose}
              index={index}
            />
          ))}
        </Box>
      ))}
    </>
  );
};

const NotificationItem = ({ notification, onClose, index }) => {
  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    onClose(notification.id);
  };

  return (
    <Fade in timeout={300}>
      <Box sx={{ mb: 1 }}>
        <Snackbar
          open={true}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          TransitionComponent={notification.position?.includes('bottom') ? TransitionUp : TransitionLeft}
          style={{ position: 'relative', transform: 'none' }}
        >
          <Alert
            severity={notification.severity}
            variant="filled"
            action={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {notification.action}
                <IconButton
                  size="small"
                  aria-label="close"
                  color="inherit"
                  onClick={handleClose}
                >
                  <Close fontSize="small" />
                </IconButton>
              </Box>
            }
            sx={{
              width: '100%',
              '& .MuiAlert-message': {
                width: '100%'
              }
            }}
          >
            {notification.title && (
              <AlertTitle>{notification.title}</AlertTitle>
            )}
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </Fade>
  );
};

export default NotificationProvider;