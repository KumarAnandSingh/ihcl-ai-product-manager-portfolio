"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  Mic, 
  MicOff, 
  Send, 
  Activity, 
  Brain, 
  Zap, 
  BarChart3, 
  Globe, 
  Shield 
} from "lucide-react";

interface Message {
  text: string;
  type: "user" | "agent";
  timestamp: Date;
  visual?: {
    image: string;
    type: string;
  };
}

interface Metrics {
  totalQueries: number;
  avgResponseTime: number;
  avgConfidence: number;
  containmentRate: number;
  totalCost: number;
}

export function TelecomAIAgent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      text: "Welcome! I'm your AI assistant for telecom services. I can help you with account recharges, bill payments, plan information, balance checks, and technical support. How can I assist you today?",
      type: "agent",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [language, setLanguage] = useState("en");
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [metrics, setMetrics] = useState<Metrics>({
    totalQueries: 0,
    avgResponseTime: 0,
    avgConfidence: 0,
    containmentRate: 0,
    totalCost: 0,
  });
  const [backendStatus, setBackendStatus] = useState<"checking" | "connected" | "disconnected">("checking");
  const [voiceStatus, setVoiceStatus] = useState<"idle" | "elevenlabs" | "browser" | "playing">("idle");
  const [availableVoices, setAvailableVoices] = useState<any>({});
  const [selectedVoice, setSelectedVoice] = useState<string>("aria");
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== "undefined" && ("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      const recognition = recognitionRef.current;
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsRecording(true);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        // Auto-send after voice input
        setTimeout(() => {
          handleSendMessage(transcript);
        }, 500);
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setIsRecording(false);
        addMessage("Sorry, I couldn't understand your voice. Please try again.", "agent");
      };
    }
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Check backend connectivity and load voices
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/health", {
          method: "GET",
        });
        if (response.ok) {
          setBackendStatus("connected");
        } else {
          setBackendStatus("disconnected");
        }
      } catch (error) {
        setBackendStatus("disconnected");
      }
    };

    const loadAvailableVoices = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/voices");
        if (response.ok) {
          const data = await response.json();
          setAvailableVoices(data.voices);
        }
      } catch (error) {
        console.error("Failed to load voices:", error);
      }
    };

    checkBackendStatus();
    loadAvailableVoices();
    // Check every 30 seconds
    const interval = setInterval(checkBackendStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const addMessage = (text: string, type: "user" | "agent") => {
    setMessages(prev => [...prev, { text, type, timestamp: new Date() }]);
  };

  const toggleVoiceRecording = () => {
    if (!recognitionRef.current) {
      alert("Voice recognition is not supported in your browser. Please use Chrome or Edge.");
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
    } else {
      // Set language for recognition
      const langCodes: Record<string, string> = {
        en: "en-US",
        hi: "hi-IN",
        ta: "ta-IN",
        te: "te-IN",
      };
      recognitionRef.current.lang = langCodes[language] || "en-US";
      recognitionRef.current.start();
    }
  };

  const speakResponse = async (text: string, language: string) => {
    setVoiceStatus("playing");
    
    try {
      // Try Edge-TTS first for natural voice
      setVoiceStatus("elevenlabs");
      const response = await fetch("http://localhost:8000/api/tts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text,
          language: language,
          voice_id: selectedVoice,
        }),
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          setVoiceStatus("idle");
        };
        
        audio.onerror = () => {
          URL.revokeObjectURL(audioUrl);
          setVoiceStatus("idle");
        };
        
        await audio.play();
        console.log("🎤 Playing Edge-TTS natural voice");
        return;
      }
    } catch (error) {
      console.log("Edge-TTS failed, falling back to browser TTS:", error);
    }

    // Fallback to browser TTS if ElevenLabs fails
    setVoiceStatus("browser");
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      const voices = window.speechSynthesis.getVoices();
      
      let voice = null;
      if (language === "hi") {
        // Prefer higher quality Hindi voices
        voice = voices.find(v => v.name.includes("Google") && v.lang.startsWith("hi")) ||
               voices.find(v => v.name.includes("Microsoft") && v.lang.startsWith("hi")) ||
               voices.find(v => v.lang === "hi-IN") ||
               voices.find(v => v.lang.startsWith("hi"));
      } else {
        // Prefer natural English voices
        voice = voices.find(v => v.name.includes("Google") && v.lang.startsWith("en")) ||
               voices.find(v => v.name.includes("Microsoft") && v.lang.startsWith("en")) ||
               voices.find(v => v.name.includes("Samantha") || v.name.includes("Alex")) ||
               voices.find(v => v.name.includes("Karen") || v.name.includes("Daniel")) ||
               voices.find(v => v.lang === "en-US" || v.lang === "en-GB");
      }
      
      if (voice) {
        utterance.voice = voice;
      }
      
      // Enhanced voice parameters for more natural sound
      utterance.rate = language === "hi" ? 0.8 : 0.9;  // Slightly faster
      utterance.pitch = 1.0;  // Natural pitch
      utterance.volume = 1.0;  // Full volume
      
      utterance.onend = () => setVoiceStatus("idle");
      utterance.onerror = () => setVoiceStatus("idle");
      
      window.speechSynthesis.speak(utterance);
      console.log("🔊 Playing browser TTS voice");
    }
  };

  const generateVisualResponse = async (intent: string, data: any) => {
    try {
      const visualType = getVisualType(intent);
      if (!visualType) return null;

      const response = await fetch("http://localhost:8000/api/generate-visual", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          visual_type: visualType,
          data: data,
          language: language,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        return result;
      }
    } catch (error) {
      console.error("Visual generation error:", error);
    }
    return null;
  };

  const getVisualType = (intent: string) => {
    if (intent.includes("plan") || intent.includes("compare")) {
      return "plan_comparison";
    } else if (intent.includes("balance") || intent.includes("account")) {
      return "account_summary";
    } else if (intent.includes("recharge") || intent.includes("payment")) {
      return "recharge_receipt";
    }
    return null;
  };

  const handleSendMessage = async (message: string = inputValue) => {
    if (!message.trim()) return;

    setIsLoading(true);
    addMessage(message, "user");
    setInputValue("");

    try {
      // Call Python FastAPI backend
      const response = await fetch("http://localhost:8000/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: message,
          language: language,
          customer_id: "DEMO_USER",
          phone_number: "9876543210",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.status === "success") {
        // Generate visual response if applicable
        const visual = await generateVisualResponse(result.response.intent || message, {
          plans: [
            { name: "Basic Plan", price: "₹199", features: ["2GB Daily", "Unlimited Calls"] },
            { name: "Premium Plan", price: "₹399", features: ["4GB Daily", "Unlimited Calls", "Free Roaming"] }
          ],
          balance: "₹156.50",
          data_left: "2.5 GB",
          validity: "15 days",
          amount: "₹199",
          phone: "9876543210",
          transaction_id: "TXN" + Date.now(),
          timestamp: new Date().toLocaleString()
        });

        // Add message with visual if available
        const messageWithVisual = {
          text: result.response.text,
          type: "agent" as const,
          timestamp: new Date(),
          visual: visual
        };
        
        setMessages(prev => [...prev, messageWithVisual]);
        
        // Speak response if voice was used for input
        if (isRecording || recognitionRef.current) {
          speakResponse(result.response.text, language);
        }
        
        // Update metrics
        updateMetrics(result.metrics);
      } else {
        addMessage("Sorry, I encountered an error processing your request.", "agent");
      }
    } catch (error) {
      console.error("Connection Error:", error);
      addMessage(`Connection Error: Please ensure the Python backend is running on http://localhost:8000. Error: ${error.message}`, "agent");
    } finally {
      setIsLoading(false);
    }
  };

  const updateMetrics = (newMetrics: any) => {
    setMetrics(prev => ({
      totalQueries: prev.totalQueries + 1,
      avgResponseTime: (prev.avgResponseTime * prev.totalQueries + newMetrics.processing_time_seconds) / (prev.totalQueries + 1),
      avgConfidence: (prev.avgConfidence * prev.totalQueries + newMetrics.intent_confidence) / (prev.totalQueries + 1),
      containmentRate: newMetrics.containment ? ((prev.containmentRate * prev.totalQueries + 1) / (prev.totalQueries + 1)) : (prev.containmentRate * prev.totalQueries / (prev.totalQueries + 1)),
      totalCost: prev.totalCost + newMetrics.cost_usd,
    }));
  };

  const sampleQueries = [
    { text: "I want to recharge my phone for 200 rupees", icon: "💳" },
    { text: "What is my account balance?", icon: "📊" },
    { text: "Show me available plans", icon: "📋" },
    { text: "Compare different plans for me", icon: "🔄" },
    { text: "My internet is not working", icon: "🔧" },
    { text: "Generate my account summary", icon: "📈" },
  ];

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="max-w-7xl mx-auto bg-white shadow-2xl flex flex-col" style={{ minHeight: '100vh' }}>
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white p-6 text-center relative overflow-hidden flex-shrink-0">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10">
            <h1 className="text-3xl font-bold mb-1">My Telecom AI Agent</h1>
            <p className="text-lg opacity-90 mb-1">Production-Scale Customer Service AI</p>
            <p className="text-sm opacity-80">Enterprise-grade multilingual voice assistant with tool integration</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="p-6 bg-slate-50 flex-1 overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            {/* Chat Panel */}
            <div className="lg:col-span-2 flex flex-col">
              <div className="border rounded-lg bg-white shadow-lg flex flex-col" style={{ height: 'calc(100vh - 280px)' }}>
              {/* Header */}
              <div className="bg-slate-100 border-b p-4 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      backendStatus === "connected" ? "bg-green-500 animate-pulse" :
                      backendStatus === "disconnected" ? "bg-red-500" :
                      "bg-yellow-500 animate-spin"
                    }`}></div>
                    <span className="font-semibold">AI Assistant</span>
                    {backendStatus === "disconnected" && (
                      <span className="text-xs text-red-600 ml-2">(Backend Disconnected)</span>
                    )}
                    {voiceStatus === "elevenlabs" && (
                      <Badge variant="secondary" className="ml-2 text-xs">
                        🎤 Edge-TTS Voice
                      </Badge>
                    )}
                    {voiceStatus === "browser" && (
                      <Badge variant="outline" className="ml-2 text-xs">
                        🔊 Browser Voice
                      </Badge>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Select value={language} onValueChange={(newLang) => {
                      setLanguage(newLang);
                      if (availableVoices[newLang] && availableVoices[newLang].length > 0) {
                        setSelectedVoice(availableVoices[newLang][0].id);
                      }
                    }}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">🇺🇸 English</SelectItem>
                        <SelectItem value="hi">🇮🇳 हिंदी</SelectItem>
                        <SelectItem value="ta">🇮🇳 தமிழ்</SelectItem>
                        <SelectItem value="te">🇮🇳 తెలుగు</SelectItem>
                      </SelectContent>
                    </Select>
                    
                    <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Select Voice" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableVoices[language]?.map((voice: any) => (
                          <SelectItem key={voice.id} value={voice.id}>
                            <div className="flex flex-col">
                              <span className="font-medium">{voice.name}</span>
                              <span className="text-xs text-gray-500">{voice.description}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
              
              {/* Messages Area - Simple Scrollable Div */}
              <div 
                className="flex-1 overflow-y-auto p-4"
                style={{ minHeight: 0 }}
              >
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`mb-4 flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[70%] p-3 rounded-lg ${
                        message.type === "user"
                          ? "bg-indigo-600 text-white"
                          : "bg-gray-100 text-gray-900"
                      }`}
                    >
                      <div className="whitespace-pre-wrap break-words">
                        {message.text}
                      </div>
                      {/* Visual content */}
                      {message.visual && (
                        <div className="mt-2 border rounded overflow-hidden bg-white">
                          <img 
                            src={message.visual.image} 
                            alt={`Visual: ${message.visual.type}`}
                            className="w-full h-auto max-h-48 object-contain"
                            onLoad={() => {
                              setTimeout(() => {
                                messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
                              }, 100);
                            }}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start mb-4">
                    <div className="bg-gray-100 text-gray-900 p-3 rounded-lg">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                        <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                        <span className="text-sm text-gray-600 ml-2">Processing...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Section */}
              <div className="border-t bg-white p-4 flex-shrink-0">
                <div className="flex gap-3 items-end">
                  <Textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your question here or click the mic to speak..."
                    className="flex-1 min-h-[56px] max-h-[120px] resize-none"
                    rows={1}
                  />
                  <Button
                    onClick={toggleVoiceRecording}
                    variant={isRecording ? "destructive" : "secondary"}
                    size="lg"
                    className={`p-3 ${isRecording ? "animate-pulse" : ""}`}
                  >
                    {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                  </Button>
                  <Button
                    onClick={() => handleSendMessage()}
                    disabled={!inputValue.trim() || isLoading}
                    size="lg"
                    className="px-6"
                  >
                    <Send className="h-5 w-5 mr-2" />
                    Send
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {sampleQueries.map((query, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="w-full justify-start text-left h-auto p-3"
                    onClick={() => {
                      setInputValue(query.text);
                      handleSendMessage(query.text);
                    }}
                  >
                    <span className="mr-2">{query.icon}</span>
                    {query.text}
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* Live Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Live Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-slate-50 rounded-lg">
                    <div className="text-2xl font-bold text-indigo-600">{metrics.totalQueries}</div>
                    <div className="text-sm text-slate-600">Queries</div>
                  </div>
                  <div className="text-center p-3 bg-slate-50 rounded-lg">
                    <div className="text-2xl font-bold text-indigo-600">{metrics.avgResponseTime.toFixed(1)}s</div>
                    <div className="text-sm text-slate-600">Avg Time</div>
                  </div>
                  <div className="text-center p-3 bg-slate-50 rounded-lg">
                    <div className="text-2xl font-bold text-indigo-600">{Math.round(metrics.avgConfidence * 100)}%</div>
                    <div className="text-sm text-slate-600">Confidence</div>
                  </div>
                  <div className="text-center p-3 bg-slate-50 rounded-lg">
                    <div className="text-2xl font-bold text-indigo-600">{Math.round(metrics.containmentRate * 100)}%</div>
                    <div className="text-sm text-slate-600">Contained</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

          {/* Feature Highlights */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Production Features Demonstrated</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { icon: Brain, text: "Multi-step conversation workflows with confidence-based decision making" },
                  { icon: Zap, text: "Real-time tool integration for recharges, bill payments, and technical support" },
                  { icon: BarChart3, text: "Production-grade performance monitoring and metrics collection" },
                  { icon: Globe, text: "Multilingual support with intelligent intent detection and cultural adaptation" },
                  { icon: Mic, text: "High-quality voice recognition and natural text-to-speech in multiple languages" },
                  { icon: Shield, text: "Enterprise security with PII protection and comprehensive audit trails" },
                ].map((feature, index) => {
                  const IconComponent = feature.icon;
                  return (
                    <div key={index} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                      <IconComponent className="h-5 w-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                      <span className="text-xs text-slate-700">{feature.text}</span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}