"use client";

import { useCopilotAction, useHumanInTheLoop } from "@copilotkit/react-core";
import { WeatherCard, WeatherToolResult, getThemeColor } from "./WeatherComponents";
import { StepsFeedback } from "./TaskComponents";
import { RecipeCard } from "./RecipeComponents";

export function useBackgroundAction(setBackground: (bg: string) => void) {
  useCopilotAction({
    name: "change_background",
    description:
      "Change the background color of the entire page. Can be anything that the CSS background attribute accepts: regular colors, linear or radial gradients, etc. Use creative and beautiful gradients when asked.",
    parameters: [
      {
        name: "background",
        type: "string",
        description: "The CSS background value. Prefer beautiful gradients. Examples: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', '#ff6b6b', 'radial-gradient(circle, #ff6b6b, #4ecdc4)'",
        required: true,
      },
    ],
    handler: async ({ background }) => {
      setBackground(background);
      return `Background successfully changed to: ${background}`;
    },
  });
}

export function useWeatherAction() {
  useCopilotAction({
    name: "get_weather",
    available: "disabled",
    parameters: [{ name: "location", type: "string", required: true }],
    render: ({ args, result, status }) => {
      if (status !== "complete") {
        return (
          <div className="bg-[#667eea] text-white p-4 rounded-lg max-w-md">
            <span className="animate-spin">⚙️</span> Retrieving weather...
          </div>
        );
      }

      const weatherResult: WeatherToolResult = {
        temperature: result?.temperature || 0,
        conditions: result?.conditions || "clear",
        humidity: result?.humidity || 0,
        windSpeed: result?.wind_speed || result?.windSpeed || 0,
        feelsLike: result?.feels_like || result?.feelsLike || result?.temperature || 0,
      };

      const themeColor = getThemeColor(weatherResult.conditions);

      return (
        <WeatherCard
          location={args.location}
          themeColor={themeColor}
          result={weatherResult}
        />
      );
    },
  });
}

export function useTaskAction() {
  useHumanInTheLoop({
    name: "generate_task_plan",
    description: "Generate a step-by-step task plan",
    parameters: [
      {
        name: "task_description",
        type: "string",
      },
      {
        name: "steps",
        type: "object[]",
        attributes: [
          {
            name: "description",
            type: "string",
          },
          {
            name: "status",
            type: "string",
            enum: ["enabled", "disabled", "executing"],
          },
        ],
      },
    ],
    render: ({ args, respond, status }) => {
      return <StepsFeedback args={args} respond={respond} status={status} />;
    },
  });
}

export function useRecipeAgent() {
  // Recipe agent uses shared state management through useCoAgent
  // The RecipeCard component handles all the state synchronization
  return null;
}
