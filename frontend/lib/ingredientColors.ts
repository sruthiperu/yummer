export type IngredientCategory = "protein" | "dairy" | "vegetables" | "fruits" | "grains" | "other"     /* five main food types */

const DB_TYPE_MAP: Record<string, IngredientCategory> = {protein: "protein", dairy: "dairy", vegetable: "vegetables", vegetables: "vegetables",
  fruit: "fruits", fruits: "fruits", grain: "grains", grains: "grains",}

export function ingredientTypeClass(foodType?: string | null): IngredientCategory {
  if (!foodType) return "other"
  const mapped = DB_TYPE_MAP[foodType.toLowerCase()]
  
  return mapped ?? "other"
}

export const INGREDIENT_LEGEND: { type: IngredientCategory; label: string }[] = [
  {type: "protein", label: "Protein"}, {type: "dairy", label: "Dairy"}, {type: "vegetables", label: "Vegetables"}, 
  {type: "fruits", label: "Fruits"}, {type: "grains", label: "Grains"}, {type: "other", label: "Other"}]
