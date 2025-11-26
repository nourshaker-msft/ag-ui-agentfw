import React, { useState, useEffect, useRef } from "react";
import { useCoAgent, useCopilotChat } from "@copilotkit/react-core";
import { Role, TextMessage } from "@copilotkit/runtime-client-gql";

enum SkillLevel {
  BEGINNER = "Beginner",
  INTERMEDIATE = "Intermediate",
  ADVANCED = "Advanced",
}

enum CookingTime {
  FiveMin = "5 min",
  FifteenMin = "15 min",
  ThirtyMin = "30 min",
  FortyFiveMin = "45 min",
  SixtyPlusMin = "60+ min",
}

const cookingTimeValues = [
  { label: CookingTime.FiveMin, value: 0 },
  { label: CookingTime.FifteenMin, value: 1 },
  { label: CookingTime.ThirtyMin, value: 2 },
  { label: CookingTime.FortyFiveMin, value: 3 },
  { label: CookingTime.SixtyPlusMin, value: 4 },
];

enum SpecialPreferences {
  HighProtein = "High Protein",
  LowCarb = "Low Carb",
  Spicy = "Spicy",
  BudgetFriendly = "Budget-Friendly",
  OnePotMeal = "One-Pot Meal",
  Vegetarian = "Vegetarian",
  Vegan = "Vegan",
}

interface Ingredient {
  icon: string;
  name: string;
  amount: string;
}

interface Recipe {
  title: string;
  skill_level: SkillLevel;
  cooking_time: CookingTime;
  special_preferences: string[];
  ingredients: Ingredient[];
  instructions: string[];
}

interface RecipeAgentState {
  recipe: Recipe;
}

const INITIAL_STATE: RecipeAgentState = {
  recipe: {
    title: "My Delicious Recipe",
    skill_level: SkillLevel.INTERMEDIATE,
    cooking_time: CookingTime.FortyFiveMin,
    special_preferences: [],
    ingredients: [
      { icon: "🥕", name: "Carrots", amount: "3 large, grated" },
      { icon: "🌾", name: "All-Purpose Flour", amount: "2 cups" },
    ],
    instructions: ["Preheat oven to 350°F (175°C)"],
  },
};

export function RecipeCard() {
  const { state: agentState, setState: setAgentState } = useCoAgent<RecipeAgentState>({
    name: "shared_state",
    initialState: INITIAL_STATE,
  });

  const [recipe, setRecipe] = useState(INITIAL_STATE.recipe);
  const { appendMessage, isLoading } = useCopilotChat();
  const [editingInstructionIndex, setEditingInstructionIndex] = useState<number | null>(null);
  const changedKeysRef = useRef<string[]>([]);

  const updateRecipe = (partialRecipe: Partial<Recipe>) => {
    setAgentState({
      ...agentState,
      recipe: {
        ...recipe,
        ...partialRecipe,
      },
    });
    setRecipe({
      ...recipe,
      ...partialRecipe,
    });
  };

  const newRecipeState = { ...recipe };
  const newChangedKeys = [];

  for (const key in recipe) {
    if (
      agentState &&
      agentState.recipe &&
      (agentState.recipe as any)[key] !== undefined &&
      (agentState.recipe as any)[key] !== null
    ) {
      let agentValue = (agentState.recipe as any)[key];
      const recipeValue = (recipe as any)[key];

      if (typeof agentValue === "string") {
        agentValue = agentValue.replace(/\\n/g, "\n");
      }

      if (JSON.stringify(agentValue) !== JSON.stringify(recipeValue)) {
        (newRecipeState as any)[key] = agentValue;
        newChangedKeys.push(key);
      }
    }
  }

  if (newChangedKeys.length > 0) {
    changedKeysRef.current = newChangedKeys;
  } else if (!isLoading) {
    changedKeysRef.current = [];
  }

  useEffect(() => {
    setRecipe(newRecipeState);
  }, [JSON.stringify(newRecipeState)]);

  const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    updateRecipe({ title: event.target.value });
  };

  const handleSkillLevelChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    updateRecipe({ skill_level: event.target.value as SkillLevel });
  };

  const handleDietaryChange = (preference: string, checked: boolean) => {
    if (checked) {
      updateRecipe({ special_preferences: [...recipe.special_preferences, preference] });
    } else {
      updateRecipe({
        special_preferences: recipe.special_preferences.filter((p) => p !== preference),
      });
    }
  };

  const handleCookingTimeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    updateRecipe({ cooking_time: cookingTimeValues[Number(event.target.value)].label });
  };

  const addIngredient = () => {
    updateRecipe({
      ingredients: [...recipe.ingredients, { icon: "🍴", name: "", amount: "" }],
    });
  };

  const updateIngredient = (index: number, field: keyof Ingredient, value: string) => {
    const updatedIngredients = [...recipe.ingredients];
    updatedIngredients[index] = { ...updatedIngredients[index], [field]: value };
    updateRecipe({ ingredients: updatedIngredients });
  };

  const removeIngredient = (index: number) => {
    const updatedIngredients = [...recipe.ingredients];
    updatedIngredients.splice(index, 1);
    updateRecipe({ ingredients: updatedIngredients });
  };

  const addInstruction = () => {
    const newIndex = recipe.instructions.length;
    updateRecipe({ instructions: [...recipe.instructions, ""] });
    setEditingInstructionIndex(newIndex);

    setTimeout(() => {
      const textareas = document.querySelectorAll(".instructions-container textarea");
      const newTextarea = textareas[textareas.length - 1] as HTMLTextAreaElement;
      if (newTextarea) newTextarea.focus();
    }, 50);
  };

  const updateInstruction = (index: number, value: string) => {
    const updatedInstructions = [...recipe.instructions];
    updatedInstructions[index] = value;
    updateRecipe({ instructions: updatedInstructions });
  };

  const removeInstruction = (index: number) => {
    const updatedInstructions = [...recipe.instructions];
    updatedInstructions.splice(index, 1);
    updateRecipe({ instructions: updatedInstructions });
  };

  const getProperIcon = (icon: string | undefined): string => {
    return icon || "🍴";
  };

  return (
    <div className="recipe-card max-w-4xl mx-auto p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl">
      {/* Recipe Title */}
      <div className="mb-8">
        <input
          type="text"
          value={recipe.title || ""}
          onChange={handleTitleChange}
          className="w-full text-4xl font-bold border-none border-b-2 border-transparent focus:border-blue-500 dark:bg-gray-800 dark:text-white pb-2 mb-6 transition-colors outline-none"
          placeholder="Recipe Title"
        />

        <div className="flex gap-6 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🕒</span>
            <select
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm cursor-pointer dark:bg-gray-700 dark:text-white hover:border-blue-500 focus:border-blue-500 focus:outline-none transition-colors"
              value={cookingTimeValues.find((t) => t.label === recipe.cooking_time)?.value || 3}
              onChange={handleCookingTimeChange}
            >
              {cookingTimeValues.map((time) => (
                <option key={time.value} value={time.value}>
                  {time.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-2xl">🏆</span>
            <select
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm cursor-pointer dark:bg-gray-700 dark:text-white hover:border-blue-500 focus:border-blue-500 focus:outline-none transition-colors"
              value={recipe.skill_level}
              onChange={handleSkillLevelChange}
            >
              {Object.values(SkillLevel).map((level) => (
                <option key={level} value={level}>
                  {level}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Dietary Preferences */}
      <div className="mb-8 relative">
        {changedKeysRef.current.includes("special_preferences") && <Ping />}
        <h2 className="text-2xl font-semibold mb-4 dark:text-white">Dietary Preferences</h2>
        <div className="flex flex-wrap gap-3">
          {Object.values(SpecialPreferences).map((option) => (
            <label
              key={option}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-full cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors select-none"
            >
              <input
                type="checkbox"
                checked={recipe.special_preferences.includes(option)}
                onChange={(e) => handleDietaryChange(option, e.target.checked)}
                className="cursor-pointer"
              />
              <span className="text-sm dark:text-white">{option}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Ingredients */}
      <div className="mb-8 relative">
        {changedKeysRef.current.includes("ingredients") && <Ping />}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-semibold dark:text-white">Ingredients</h2>
          <button
            type="button"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors"
            onClick={addIngredient}
          >
            + Add Ingredient
          </button>
        </div>
        <div className="space-y-3">
          {recipe.ingredients.map((ingredient, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl hover:border-blue-500 transition-colors"
            >
              <div className="text-3xl min-w-[32px] text-center">{getProperIcon(ingredient.icon)}</div>
              <div className="flex-1 space-y-2">
                <input
                  type="text"
                  value={ingredient.name || ""}
                  onChange={(e) => updateIngredient(index, "name", e.target.value)}
                  placeholder="Ingredient name"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium dark:bg-gray-800 dark:text-white focus:border-blue-500 outline-none transition-colors"
                />
                <input
                  type="text"
                  value={ingredient.amount || ""}
                  onChange={(e) => updateIngredient(index, "amount", e.target.value)}
                  placeholder="Amount"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-800 dark:text-white focus:border-blue-500 outline-none transition-colors"
                />
              </div>
              <button
                type="button"
                className="min-w-[32px] h-8 bg-red-500 text-white rounded-full text-xl hover:bg-red-600 hover:scale-110 transition-all flex items-center justify-center"
                onClick={() => removeIngredient(index)}
                aria-label="Remove ingredient"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Instructions */}
      <div className="mb-8 relative">
        {changedKeysRef.current.includes("instructions") && <Ping />}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-semibold dark:text-white">Instructions</h2>
          <button
            type="button"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors"
            onClick={addInstruction}
          >
            + Add Step
          </button>
        </div>
        <div className="instructions-container space-y-6">
          {recipe.instructions.map((instruction, index) => (
            <div key={index} className="flex gap-4 relative">
              <div className="min-w-[32px] h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0 z-10">
                {index + 1}
              </div>
              {index < recipe.instructions.length - 1 && (
                <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-gray-300 dark:bg-gray-600 -mb-6" />
              )}
              <div
                className={`flex-1 relative p-4 rounded-lg cursor-pointer transition-all ${
                  editingInstructionIndex === index
                    ? "bg-white dark:bg-gray-800 border-2 border-blue-500 shadow-lg"
                    : "bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 hover:border-blue-500"
                }`}
                onClick={() => setEditingInstructionIndex(index)}
              >
                <textarea
                  value={instruction || ""}
                  onChange={(e) => updateInstruction(index, e.target.value)}
                  placeholder="Enter cooking instruction..."
                  onFocus={() => setEditingInstructionIndex(index)}
                  onBlur={(e) => {
                    if (!e.relatedTarget || !e.currentTarget.contains(e.relatedTarget as Node)) {
                      setEditingInstructionIndex(null);
                    }
                  }}
                  className="w-full min-h-[60px] border-none bg-transparent text-sm leading-relaxed resize-vertical outline-none dark:text-white"
                />
                <button
                  type="button"
                  className={`absolute top-2 right-2 min-w-[32px] h-8 bg-red-500 text-white rounded-full text-xl hover:bg-red-600 transition-all flex items-center justify-center ${
                    editingInstructionIndex === index ? "opacity-100" : "opacity-0 group-hover:opacity-100"
                  }`}
                  onClick={(e) => {
                    e.stopPropagation();
                    removeInstruction(index);
                  }}
                  aria-label="Remove instruction"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Improve Button */}
      <div className="text-center">
        <button
          type="button"
          className={`px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-60 disabled:cursor-not-allowed ${
            isLoading ? "animate-pulse" : ""
          }`}
          onClick={() => {
            if (!isLoading) {
              appendMessage(
                new TextMessage({
                  content: "Improve the recipe with better ingredients and techniques",
                  role: Role.User,
                })
              );
            }
          }}
          disabled={isLoading}
        >
          {isLoading ? "Improving..." : "✨ Improve with AI"}
        </button>
      </div>
    </div>
  );
}

function Ping() {
  return (
    <span className="absolute -top-2 -right-2 flex items-center justify-center">
      <span className="absolute w-4 h-4 bg-blue-500 rounded-full opacity-75 animate-ping" />
      <span className="relative w-2 h-2 bg-blue-500 rounded-full" />
    </span>
  );
}
