import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  IconButton,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Send as SendIcon,
  Mic as MicIcon,
  Psychology as AIIcon,
  TrendingUp,
  Warning,
  Lightbulb,
  Assessment
} from '@mui/icons-material';
import { apiService } from '../../services/apiService';

const NaturalLanguageInterface = ({ onQueryResult, contextData }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [suggestions] = useState([
    "Show me AWS costs for this month",
    "Compare Azure and GCP pricing",
    "How can I optimize my cloud spending?",
    "Predict next month's costs",
    "Find cost anomalies in my data",
    "What are my most expensive services?"
  ]);

  const handleSubmitQuery = useCallback(async () => {
    if (!query.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString()
    };

    setConversation(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      // Call the natural language processing API
      const response = await fetch('http://localhost:5000/api/ai/natural-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          context: contextData || {}
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: data.result.response.response,
          data: data.result.response.data,
          intent: data.result.parsed_query.intent,
          confidence: data.result.parsed_query.confidence,
          timestamp: new Date().toLocaleTimeString()
        };

        setConversation(prev => [...prev, aiMessage]);
        
        // Notify parent component about the query result
        if (onQueryResult) {
          onQueryResult(data.result);
        }
      } else {
        throw new Error(data.message || 'Failed to process query');
      }
    } catch (error) {
      console.error('Error processing query:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I'm sorry, I couldn't process your request right now. Please try again later.",
        error: true,
        timestamp: new Date().toLocaleTimeString()
      };

      setConversation(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setQuery('');
    }
  }, [query, loading, contextData, onQueryResult]);

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
  };

  const getIntentIcon = (intent) => {
    switch (intent) {
      case 'cost_query':
        return <Assessment color="primary" />;
      case 'comparison_query':
        return <TrendingUp color="info" />;
      case 'optimization_query':
        return <Lightbulb color="warning" />;
      case 'prediction_query':
        return <AIIcon color="secondary" />;
      default:
        return <AIIcon color="action" />;
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.5) return 'warning';
    return 'error';
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <AIIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">
            AI Assistant
          </Typography>
          <Chip 
            label="BETA" 
            size="small" 
            color="secondary" 
            sx={{ ml: 1 }}
          />
        </Box>

        {/* Conversation Area */}
        <Box 
          sx={{ 
            flexGrow: 1, 
            overflowY: 'auto', 
            mb: 2, 
            maxHeight: '400px',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
            p: 1
          }}
        >
          {conversation.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <AIIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Ask me anything about your cloud costs!
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Try: "Show me my AWS costs" or "How can I save money?"
              </Typography>
            </Box>
          ) : (
            conversation.map((message) => (
              <Box key={message.id} sx={{ mb: 2 }}>
                <Paper
                  sx={{
                    p: 2,
                    bgcolor: message.type === 'user' ? 'primary.main' : 'grey.100',
                    color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
                    ml: message.type === 'user' ? 4 : 0,
                    mr: message.type === 'user' ? 0 : 4
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                    <Typography variant="body2">
                      {message.content}
                    </Typography>
                    <Typography variant="caption" sx={{ ml: 2, opacity: 0.7 }}>
                      {message.timestamp}
                    </Typography>
                  </Box>
                  
                  {message.type === 'ai' && message.intent && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, gap: 1 }}>
                      {getIntentIcon(message.intent)}
                      <Chip 
                        label={message.intent.replace('_', ' ')}
                        size="small"
                        variant="outlined"
                      />
                      <Chip 
                        label={`${Math.round(message.confidence * 100)}% confident`}
                        size="small"
                        color={getConfidenceColor(message.confidence)}
                        variant="outlined"
                      />
                    </Box>
                  )}
                  
                  {message.error && (
                    <Alert severity="error" sx={{ mt: 1 }}>
                      An error occurred while processing your request.
                    </Alert>
                  )}
                </Paper>
              </Box>
            ))
          )}
          
          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                AI is thinking...
              </Typography>
            </Box>
          )}
        </Box>

        {/* Suggestions */}
        {conversation.length === 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom color="text.secondary">
              Try these questions:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <Chip
                  key={index}
                  label={suggestion}
                  variant="outlined"
                  size="small"
                  onClick={() => handleSuggestionClick(suggestion)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Input Area */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            placeholder="Ask me about your cloud costs..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmitQuery();
              }
            }}
            disabled={loading}
            size="small"
            multiline
            maxRows={3}
          />
          <IconButton
            color="primary"
            onClick={handleSubmitQuery}
            disabled={!query.trim() || loading}
            sx={{ alignSelf: 'flex-end' }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );
};

export default NaturalLanguageInterface;