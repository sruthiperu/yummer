"use client"

import {TAG_LABELS, CuratedTag} from "@/lib/recipeTags"
import "./tag_filters.css"

type CuratedTagFiltersProps = {
  selected: string[]
  onChange: (tags: string[]) => void
  maxTime?: number
  onMaxTimeChange?: (minutes: number | undefined) => void
  maxCalories?: number
  onMaxCaloriesChange?: (calories: number | undefined) => void
}

const DIETARY_TAGS: CuratedTag[] = ["protein", "vegetarian", "vegan", "gluten-free", "keto", "main-course", "side-dish"]

export default function CuratedTagFilters({selected, onChange, maxTime, onMaxTimeChange, maxCalories, onMaxCaloriesChange}: CuratedTagFiltersProps) {
  
  const toggle = (tag: string) => {
    if (selected.includes(tag)) {
      onChange(selected.filter(t => t !== tag))
    } else {
      onChange([...selected, tag])
    }
  }

  const clearAll = () => {
    onChange([])
    onMaxTimeChange?.(undefined)
    onMaxCaloriesChange?.(undefined)
  }

  const hasAnyFilter = selected.length > 0 || maxTime != null || maxCalories != null

  return (
    <div className="filter_panel">
      <h3 className="filter_panel__title">Filters</h3>

      {/* dietary, meal type checkboxes */}
      <div className="filter_section">
        <p className="filter_section__label">Dietary & Meal Type</p>
        {DIETARY_TAGS.map((tag) => (
          <label key={tag} className="filter_checkbox">
            <input
              type="checkbox"
              checked={selected.includes(tag)}
              onChange={() => toggle(tag)}
              className="filter_checkbox__input"
            />
            <span className="filter_checkbox__checkmark" />
            <span className="filter_checkbox__text">{TAG_LABELS[tag]}</span>
          </label>
        ))}
      </div>

      {/* time slider */}
      {onMaxTimeChange && (
        <div className="filter_section">
          <p className="filter_section__label">
            Max Cook Time (min): {maxTime ? `${maxTime} min` : "Any"}
          </p>
          <input type="range" min={5} max={120} step={5} value={maxTime || 120}
            onChange={(e) => {
              const val = Number(e.target.value)
              onMaxTimeChange(val >= 120 ? undefined : val)
            }}
            className="filter_slider"
          />
          <div className="filter_slider_labels">
            <span>5</span>
            <span>60</span>
            <span>120</span>
          </div>
        </div>
      )}

      {/* calories slider */}
      {onMaxCaloriesChange && (
        <div className="filter_section">
          <p className="filter_section__label">
            Max Calories (kcal): {maxCalories ? `${maxCalories}` : "Any"}
          </p>
          <input type="range" min={100} max={1500} step={50} value={maxCalories || 1500}
            onChange={(e) => {
              const val = Number(e.target.value)
              onMaxCaloriesChange(val >= 1500 ? undefined : val)
            }}
            className="filter_slider"
          />
          <div className="filter_slider_labels">
            <span>100</span>
            <span>750</span>
            <span>1500</span>
          </div>
        </div>
      )}

      {/* clear filters button */}
      {hasAnyFilter && (
        <button onClick={clearAll} className="filter_clear_btn">
          Clear Filters
        </button>
      )}
    </div>
  )
}