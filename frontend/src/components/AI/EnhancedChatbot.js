import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Chip,
  Fab,
  Fade,
  CircularProgress,
  alpha,
  useTheme
} from '@mui/material';
import {
  SendOutlined,
  SmartToyOutlined,
  PersonOutlined,
  MicOutlined,
  AttachFileOutlined,
  MoreVertOutlined,
  AutoAwesomeOutlined
} from '@mui/icons-material';
import { keyframes, styled } from '@mui/material/styles';

const typing = keyframes`
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
`;

const ChatContainer = styled(Paper)(({ theme }) => ({
  background: theme.palette.mode === 'dark'
    ? `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.95)} 0%, ${alpha(theme.palette.background.default, 0.95)} 100%)`
    : `linear-gradient(135deg, ${alpha('#ffffff', 0.95)} 0%, ${alpha('#f8fafc', 0.95)} 100%)`,
  backdropFilter: 'blur(20px)',
  borderRadius: 20,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  height: '600px',
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
}));

const MessageBubble = styled(Box)(({ theme, isUser }) => ({
  maxWidth: '70%',
  padding: '12px 16px',
  borderRadius: isUser ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
  background: isUser 
    ? `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`
    : alpha(theme.palette.background.paper, 0.8),
  color: isUser ? theme.palette.primary.contrastText : theme.palette.text.primary,
  marginBottom: '8px',
  alignSelf: isUser ? 'flex-end' : 'flex-start',
  boxShadow: theme.palette.mode === 'dark'
    ? `0 4px 20px ${alpha('#000', 0.3)}`
    : `0 4px 20px ${alpha('#000', 0.1)}`,
  position: 'relative',
  '&::before': !isUser ? {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '2px',
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
    borderRadius: '20px 20px 0 0',
  } : {},
}));

const TypingIndicator = styled(Box)({
  display: 'flex',
  gap: '4px',
  '& > div': {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: 'currentColor',
    animation: `${typing} 1.4s ease-in-out infinite`,
    '&:nth-of-type(2)': {
      animationDelay: '0.2s',
    },
    '&:nth-of-type(3)': {
      animationDelay: '0.4s',
    },
  },
});

function EnhancedChatbot() {
  const theme = useTheme();
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm FISO AI, your intelligent cloud optimization assistant. How can I help you optimize your cloud infrastructure today?",
      isUser: false,
      timestamp: new Date(),
      type: 'greeting'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputValue);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: aiResponse.text,
        isUser: false,
        timestamp: new Date(),
        type: aiResponse.type,
        data: aiResponse.data
      }]);
      setIsTyping(false);
    }, 1500 + Math.random() * 1000);
  };

  const generateAIResponse = (input) => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('cost') || lowerInput.includes('save') || lowerInput.includes('optimize')) {
      return {
        text: "Based on your current usage patterns, I've identified 3 key optimization opportunities:\n\n💰 **Compute Optimization**: You can save $2,400/month by rightsizing over-provisioned instances\n📊 **Storage Tiering**: Move 40% of your data to cheaper storage tiers for $800/month savings\n⚡ **Auto-scaling**: Implement intelligent scaling to reduce costs by $1,600/month\n\nWould you like me to create a detailed optimization plan?",
        type: 'optimization',
        data: { totalSavings: 4800, opportunities: 3 }
      };
    }
    
    if (lowerInput.includes('performance') || lowerInput.includes('speed') || lowerInput.includes('latency')) {
      return {
        text: "I've analyzed your system performance metrics:\n\n🚀 **Current Performance Score**: 92.4%\n📈 **Latency**: Average 45ms (Excellent)\n🔄 **Throughput**: 15,000 requests/second\n⚡ **CPU Utilization**: 67% (Optimal)\n\nYour system is performing well! I recommend monitoring these key metrics for continued optimization.",
        type: 'performance',
        data: { score: 92.4, latency: 45 }
      };
    }
    
    if (lowerInput.includes('security') || lowerInput.includes('vulnerable') || lowerInput.includes('threat')) {
      return {
        text: "🛡️ **Security Analysis Complete**\n\n✅ **Security Score**: 95/100\n🔒 **Encryption**: All data encrypted at rest and in transit\n🚨 **Threats Detected**: 0 critical, 2 medium (resolved)\n📊 **Compliance**: SOC2, GDPR, HIPAA compliant\n\nYour security posture is strong. All recent vulnerabilities have been patched automatically.",
        type: 'security',
        data: { securityScore: 95, threats: 0 }
      };
    }
    
    if (lowerInput.includes('predict') || lowerInput.includes('forecast') || lowerInput.includes('future')) {
      return {
        text: "🔮 **AI Predictions for Next 30 Days**:\n\n📊 **Usage Trend**: Expected 15% increase\n💰 **Cost Forecast**: $12,400 (within budget)\n⚡ **Performance**: Maintaining 90%+ efficiency\n🎯 **Recommendations**: Scale storage by 20%, optimize 3 underutilized instances\n\nConfidence: 94% based on historical patterns and current trends.",
        type: 'prediction',
        data: { confidence: 94, costForecast: 12400 }
      };
    }
    
    // Default responses
    const defaultResponses = [
      {
        text: "I'm analyzing your cloud infrastructure in real-time. Here's what I can help you with:\n\n💰 Cost optimization strategies\n📊 Performance monitoring\n🛡️ Security assessments\n🔮 Predictive analytics\n⚙️ Resource management\n\nWhat specific area would you like to focus on?",
        type: 'menu',
        data: null
      },
      {
        text: "Great question! I'm processing data from your cloud providers right now. Based on current metrics, everything looks optimized. Is there a specific concern or area you'd like me to investigate further?",
        type: 'general',
        data: null
      }
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleVoiceInput = () => {
    setIsListening(!isListening);
    // Voice input simulation
    if (!isListening) {
      setTimeout(() => {
        setIsListening(false);
        setInputValue("How can I optimize my cloud costs?");
      }, 3000);
    }
  };

  return (
    <Box sx={{ height: '100%', p: 3 }}>
      <ChatContainer elevation={0}>
        {/* Chat Header */}
        <Box sx={{ 
          p: 3, 
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.1)} 100%)`,
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ 
                bgcolor: 'primary.main',
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                width: 48,
                height: 48
              }}>
                <SmartToyOutlined />
              </Avatar>
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  FISO AI Assistant
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: 'success.main',
                    animation: `${typing} 2s ease-in-out infinite`
                  }} />
                  <Typography variant="caption" color="success.main">
                    Online • AI-Powered
                  </Typography>
                </Box>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip 
                icon={<AutoAwesomeOutlined />} 
                label="Smart Mode" 
                size="small" 
                color="primary" 
                variant="outlined"
              />
              <IconButton size="small">
                <MoreVertOutlined />
              </IconButton>
            </Box>
          </Box>
        </Box>

        {/* Messages Container */}
        <Box 
          ref={chatContainerRef}
          sx={{ 
            flex: 1, 
            p: 2, 
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 1,
            '&::-webkit-scrollbar': {
              width: '6px',
            },
            '&::-webkit-scrollbar-track': {
              background: alpha(theme.palette.divider, 0.1),
              borderRadius: '10px',
            },
            '&::-webkit-scrollbar-thumb': {
              background: alpha(theme.palette.primary.main, 0.3),
              borderRadius: '10px',
            },
          }}
        >
          {messages.map((message, index) => (
            <Fade
              key={message.id}
              in={true}
              timeout={300 + index * 100}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                {!message.isUser && (
                  <Avatar sx={{ 
                    width: 32, 
                    height: 32, 
                    bgcolor: 'primary.main',
                    mt: 0.5
                  }}>
                    <SmartToyOutlined fontSize="small" />
                  </Avatar>
                )}
                <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <MessageBubble isUser={message.isUser}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.5
                      }}
                    >
                      {message.text}
                    </Typography>
                    {message.data && (
                      <Box sx={{ mt: 1, pt: 1, borderTop: `1px solid ${alpha('#fff', 0.2)}` }}>
                        {message.type === 'optimization' && (
                          <Chip 
                            label={`Potential savings: $${message.data.totalSavings}/month`}
                            size="small"
                            sx={{ bgcolor: alpha('#fff', 0.2) }}
                          />
                        )}
                        {message.type === 'prediction' && (
                          <Chip 
                            label={`${message.data.confidence}% confidence`}
                            size="small"
                            sx={{ bgcolor: alpha('#fff', 0.2) }}
                          />
                        )}
                      </Box>
                    )}
                  </MessageBubble>
                  <Typography 
                    variant="caption" 
                    color="text.secondary" 
                    sx={{ 
                      mt: 0.5,
                      ml: message.isUser ? 'auto' : 0,
                      mr: message.isUser ? 1 : 0
                    }}
                  >
                    {message.timestamp.toLocaleTimeString('en-US', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </Typography>
                </Box>
                {message.isUser && (
                  <Avatar sx={{ 
                    width: 32, 
                    height: 32, 
                    bgcolor: 'secondary.main',
                    mt: 0.5
                  }}>
                    <PersonOutlined fontSize="small" />
                  </Avatar>
                )}
              </Box>
            </Fade>
          ))}
          
          {isTyping && (
            <Fade in={isTyping}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                  <SmartToyOutlined fontSize="small" />
                </Avatar>
                <MessageBubble isUser={false}>
                  <TypingIndicator>
                    <div />
                    <div />
                    <div />
                  </TypingIndicator>
                </MessageBubble>
              </Box>
            </Fade>
          )}
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box sx={{ 
          p: 2, 
          borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          background: alpha(theme.palette.background.paper, 0.8)
        }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
            <IconButton 
              size="small" 
              onClick={toggleVoiceInput}
              sx={{ 
                color: isListening ? 'error.main' : 'text.secondary',
                '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.1) }
              }}
            >
              <MicOutlined />
            </IconButton>
            <IconButton 
              size="small"
              sx={{ '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.1) } }}
            >
              <AttachFileOutlined />
            </IconButton>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder="Ask FISO AI about cost optimization, performance, security..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              variant="outlined"
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  bgcolor: alpha(theme.palette.background.paper, 0.8),
                  '&:hover fieldset': {
                    borderColor: theme.palette.primary.main,
                  },
                },
              }}
            />
            <Fab
              size="small"
              color="primary"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              sx={{ 
                minWidth: 40,
                width: 40,
                height: 40,
                boxShadow: theme.palette.mode === 'dark'
                  ? `0 4px 20px ${alpha(theme.palette.primary.main, 0.3)}`
                  : `0 4px 20px ${alpha(theme.palette.primary.main, 0.2)}`,
              }}
            >
              {isTyping ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <SendOutlined fontSize="small" />
              )}
            </Fab>
          </Box>
        </Box>
      </ChatContainer>
    </Box>
  );
}

export default EnhancedChatbot;