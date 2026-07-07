import type {Instruction} from "@/types/recipe"

export type DirectionSection = {title: string | null, steps: Instruction[]}

export function groupDirectionsBySection(steps: Instruction[]): DirectionSection[] {
    if (!steps?.length) return []

    const sections: DirectionSection[] = []
    for (const step of steps) {
        const title = step.section_title ?? null
        const last = sections[sections.length - 1]
        
        if (last && last.title === title) {
            last.steps.push(step)
        } else {
            sections.push({ title, steps: [step] })
        }
    }

    return sections
}

export function directionSectionKey(section: DirectionSection, index: number): string {
    return `${section.title ?? "default"}-${index}`
}
