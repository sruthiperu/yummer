export type DietaryIcon = {
  id: "vegan" | "vegetarian" | "fish" | "non_veg" | "egg" | "gluten_free"
  label: string
  iconClass: string
}

type IngredientDietaryInput = {
  name?: string | null
  food_type?: string | null
  is_vegan?: boolean | null
  is_vegetarian?: boolean | null
  is_gluten_free?: boolean | null
  allergens?: string[] | null
}

function hasSeafoodAllergen(tagSet: Set<string>): boolean {
  return tagSet.has("fish") || tagSet.has("shellfish")
}
function hasEgg(name: string, tagSet: Set<string>): boolean {
  return tagSet.has("eggs") || /\begg\b/.test(name)
}

export function displayDietaryIcons(ing: IngredientDietaryInput): DietaryIcon[] {
  const icons: DietaryIcon[] = []
  const tagSet = new Set((ing.allergens ?? []).map((t) => t.toLowerCase()))
  const name = (ing.name ?? "").toLowerCase()
  const isVegan = ing.is_vegan === true
  const isVegetarian = ing.is_vegetarian === true
  const isGlutenFree = ing.is_gluten_free === true

  if (isVegan) {
    icons.push({id: "vegan", label: "Vegan", iconClass: "fa-seedling"})
  } else if (isVegetarian) {
    icons.push({id: "vegetarian", label: "Vegetarian", iconClass: "fa-leaf"})
  }
  if (ing.is_vegetarian === false && ing.food_type === "protein") {
    if (hasSeafoodAllergen(tagSet)) {
      icons.push({id: "fish", label: "Fish / seafood", iconClass: "fa-fish"})
    } else {
      icons.push({id: "non_veg", label: "Non-vegetarian", iconClass: "fa-drumstick-bite"})
    }
  }
  if (hasEgg(name, tagSet)) {
    icons.push({id: "egg", label: "Contains egg", iconClass: "fa-egg"})
  }
  if (isGlutenFree) {
    icons.push({id: "gluten_free", label: "Gluten-free", iconClass: "fa-wheat-awn"})
  }

  return icons
}
