import type {Instruction} from "@/types/recipe"

export type DirectionSection = {title: string | null, steps: Instruction[]}

/* remove blank direction rows */
export function filterRealDirectionSteps(steps: Instruction[] | null | undefined): Instruction[] {
    if (!steps?.length) return []
    return steps.filter((step) => Boolean(step.direction?.trim()))
}

export function groupDirectionsBySection(steps: Instruction[]): DirectionSection[] {
    const realSteps = filterRealDirectionSteps(steps)
    if (!realSteps.length) return []

    const sections: DirectionSection[] = []
    for (const step of realSteps) {
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
