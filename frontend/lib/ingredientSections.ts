import type {Ingredient} from "@/types/recipe"

export type IngredientSection = {title: string | null, ingredients: Ingredient[]}

export function groupIngredientsBySection(ingredients: Ingredient[]): IngredientSection[] {
    if (!ingredients?.length) return []

    const sections: IngredientSection[] = []
    for (const ing of ingredients) {
        const title = ing.section_title ?? null
        const last = sections[sections.length - 1]
        
        if (last && last.title === title) {
            last.ingredients.push(ing)
        } else {
            sections.push({ title, ingredients: [ing] })
        }
    }

    return sections
}

export function sectionKey(section: IngredientSection, index: number): string {
    return `${section.title ?? "default"}-${index}`
}

export function distributeToColumns<T>(
    sections: T[],
    itemCount: (section: T) => number,
): [T[], T[]] {
    const left: T[] = []
    const right: T[] = []
    let leftCount = 0
    let rightCount = 0

    for (const section of sections) {
        const n = itemCount(section)
        if (leftCount <= rightCount) {
            left.push(section)
            leftCount += n
        } else {
            right.push(section)
            rightCount += n
        }
    }
    return [left, right]
}

export function distributeSectionsToColumns(
    sections: IngredientSection[],
): [IngredientSection[], IngredientSection[]] {
    return distributeToColumns(sections, (section) => section.ingredients.length)
}
