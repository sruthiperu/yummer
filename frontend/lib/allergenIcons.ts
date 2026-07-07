export type AllergenDisplay = {
  id: string
  label: string
}

const ALLERGEN_MAP: {tags: string[]; id: string; label: string}[] = [
  {tags: ["peanuts"], id: "peanut", label: "Peanut"},
  {tags: ["tree nuts"], id: "tree_nut", label: "Tree nut"},
  {tags: ["soy"], id: "soy", label: "Soy"},
  {tags: ["wheat", "gluten"], id: "wheat", label: "Wheat"},
  {tags: ["dairy"], id: "milk", label: "Milk"},
  {tags: ["eggs"], id: "egg", label: "Egg"},
  {tags: ["fish"], id: "fish", label: "Fish"},
  {tags: ["shellfish"], id: "shellfish", label: "Shellfish"},
  {tags: ["sesame"], id: "sesame", label: "Sesame"},
]

export function displayAllergens(tags: string[] | null | undefined): AllergenDisplay[] {
  if (!tags?.length) return []

  const tagSet = new Set(tags.map((t) => t.toLowerCase()))
  const result: AllergenDisplay[] = []
  for (const entry of ALLERGEN_MAP) {
    if (entry.tags.some((t) => tagSet.has(t))) {
      result.push({ id: entry.id, label: entry.label })
    }
  }

  return result
}

export function allergenContainsText(allergens: AllergenDisplay[]): string {
  if (!allergens.length) return ""
  const names = allergens.map((a) => a.label.toLowerCase())
  return `Contains ${names.join(", ")}`     /* handles multiple allergens */
}

export const ALLERGEN_LEGEND: { label: string }[] = [{label: "Allergen"}]
