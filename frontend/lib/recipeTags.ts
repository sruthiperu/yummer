export const TAG_ORDER = ["main-course", "side-dish", "protein", "vegetarian", "vegan", "gluten-free", "keto", "low-calorie", "under-15-min", "under-30-min", "under-45-min", "under-60-min"] as const

export type CuratedTag = (typeof TAG_ORDER)[number]

export const TAG_LABELS: Record<CuratedTag, string> = {"main-course": "main-course", "side-dish": "side-dish", 
  protein: "protein", vegetarian: "vegetarian", vegan: "vegan", "gluten-free": "gluten-free", keto: "keto", "low-calorie": "low-calorie", 
  "under-15-min": "under-15-min", "under-30-min": "under-30-min", "under-45-min": "under-45-min", "under-60-min": "under-60-min"}

const TAG_SET = new Set<string>(TAG_ORDER)

export function formatRecipeTags(tags: string[] | null | undefined, limit?: number): { id: CuratedTag; label: string }[] {
  if (!tags?.length) return []

  const tagSet = new Set(tags)
  const ordered = TAG_ORDER.filter((t) => tagSet.has(t))
  const sliced = limit != null ? ordered.slice(0, limit) : ordered

  return sliced.map((id) => ({ id, label: TAG_LABELS[id] }))
}

export function isCuratedTag(tag: string): tag is CuratedTag {
  return TAG_SET.has(tag)
}
