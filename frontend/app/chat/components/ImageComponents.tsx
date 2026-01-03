"use client";

import React from "react";
import { useCoAgent } from "@copilotkit/react-core";

interface ImageState {
  url: string;
  prompt: string;
}

interface ImageAgentState {
  image?: ImageState;
}

export function ImagePlaceholder() {
  const { state } = useCoAgent<ImageAgentState>({
    name: "image",
    initialState: {},
  });

  const imageUrl = state.image?.url;
  const imagePrompt = state.image?.prompt;

  if (imageUrl) {
    return (
      <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center h-full min-h-[300px]">
        <img 
          src={imageUrl} 
          alt={imagePrompt || "Generated Image"} 
          className="max-w-full max-h-full rounded shadow-lg object-contain"
        />
        {imagePrompt && (
          <p className="mt-4 text-sm text-gray-600 dark:text-gray-400 text-center">
            {imagePrompt}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 h-full min-h-[300px] flex items-center justify-center">
      <p className="text-center text-gray-500 dark:text-gray-400">
        Image generation components will appear here. Over multiple turns; Images will appear as soon as they're created by the agent.
        <br />
        Ask the agent to generate an image!
      </p>
    </div>
  );
}
