"use client";

import React, { useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { useTheme } from "next-themes";
import Link from "next/link";
import { useBackgroundAction, useWeatherAction, useTaskAction, useRecipeAgent } from "../components/AgentActions";
import { RecipeCard } from "../components/RecipeComponents";
import "../style.css";

interface ChatPageProps {
  params: Promise<{
    agent: string;
  }>;
}

const agentConfig = {
  simple: {
    title: "Simple Chat",
    icon: "💬",
    description: "General purpose AI assistant",
    suggestions: [
      { title: "Tell me a joke", message: "Tell me a funny joke" },
      { title: "Explain AI", message: "Explain artificial intelligence in simple terms" },
      { title: "Write a poem", message: "Write a short poem about technology" },
    ],
    initial: "Hi! I'm your AI assistant. How can I help you today?",
  },
  weather: {
    title: "Weather Agent",
    icon: "🌤️",
    description: "Get weather information",
    suggestions: [
      { title: "New York Weather", message: "What's the weather in New York?" },
      { title: "London Weather", message: "How's the weather in London?" },
      { title: "Tokyo Weather", message: "Tell me about the weather in Tokyo" },
    ],
    initial: "Hi! I can help you check the weather for any location. Just ask!",
  },
  tasks: {
    title: "Task Planner",
    icon: "✅",
    description: "Plan and execute tasks",
    suggestions: [
      { title: "Plan a trip", message: "Help me plan a trip to Paris in 8 steps" },
      { title: "Learn programming", message: "Create a plan to learn Python in 10 steps" },
      { title: "Start a business", message: "Plan steps to start an online business" },
    ],
    initial: "Hi! I'm your task planning assistant. Tell me what you'd like to accomplish!",
  },
  shared_state: {
    title: "Recipe Assistant",
    icon: "👨‍🍳",
    description: "Create and improve recipes with AI",
    suggestions: [
      { title: "Create pasta recipe", message: "Create a delicious pasta recipe" },
      { title: "Healthy breakfast", message: "Make a healthy breakfast recipe" },
      { title: "Improve recipe", message: "Improve the recipe with better ingredients" },
    ],
    initial: "Hi! I'm your recipe assistant. I can help you create and improve recipes!",
  },
};

export default function ChatPage({ params }: ChatPageProps) {
  const { agent } = React.use(params);
  const { theme } = useTheme();
  const [background, setBackground] = useState<string>(
    "bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900"
  );
  
  const config = agentConfig[agent as keyof typeof agentConfig] || agentConfig.simple;

  return (
    <div 
      className={`min-h-screen transition-all duration-500 ${background.startsWith('bg-') ? background : ''}`}
      style={!background.startsWith('bg-') ? { background } : undefined}
    >
      <div className="container mx-auto px-4 py-6 h-screen flex flex-col">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
              >
                ← Back
              </Link>
              <div className="flex items-center gap-3">
                <div className="text-4xl">{config.icon}</div>
                <div>
                  <h1 className="text-2xl font-bold">{config.title}</h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {config.description}
                  </p>
                </div>
              </div>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Powered by Agent Framework
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 min-h-0">
          <CopilotKit
            runtimeUrl={`/api/copilotkit/${agent}`}
            showDevConsole={false}
            agent={agent}
          >
            <ChatInterface config={config} theme={theme} setBackground={setBackground} agent={agent} />
          </CopilotKit>
        </div>
      </div>
    </div>
  );
}

function ChatInterface({
  config,
  theme,
  setBackground,
  agent,
}: {
  config: typeof agentConfig[keyof typeof agentConfig];
  theme: string | undefined;
  setBackground: (bg: string) => void;
  agent: string;
}) {
  // Agent-specific actions
  useBackgroundAction(setBackground);
  useWeatherAction();
  useTaskAction();
  useRecipeAgent();

  // For recipe agent, show the recipe card instead of regular chat
  if (agent === "shared_state") {
    return (
      <div className="h-full overflow-y-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          <div className="overflow-y-auto p-4">
            <RecipeCard />
          </div>
          <div className="h-full rounded-2xl overflow-hidden shadow-2xl bg-white dark:bg-gray-800">
            <CopilotChat
              className="h-full"
              labels={{
                initial: config.initial,
              }}
              suggestions={config.suggestions}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full rounded-2xl overflow-hidden shadow-2xl bg-white dark:bg-gray-800">
      <CopilotChat
        className="h-full"
        labels={{
          initial: config.initial,
        }}
        suggestions={[
          ...config.suggestions,
          {
            title: "Change background",
            message: "Change the background to a beautiful gradient",
          },
        ]}
      />
    </div>
  );
}
