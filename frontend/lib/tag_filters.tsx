"use client"

import {useEffect, useState} from "react"
import {TAG_LABELS, CuratedTag} from "@/lib/recipeTags"
import "./tag_filters.css"

type CuratedTagFiltersProps = {
  selected: string[]
  onChange: (tags: string[]) => void
  maxTime?: number
  onMaxTimeChange?: (minutes: number | undefined) => void
  maxCalories?: number
  onMaxCaloriesChange?: (calories: number | undefined) => void
  onClearAll?: () => void
}

const DIETARY_TAGS: CuratedTag[] = ["protein", "vegetarian", "vegan", "gluten-free", "keto"]
const MEAL_TAGS: CuratedTag[] = ["main-course", "side-dish"]
const MOBILE_MQ = "(max-width: 640px)"

export default function CuratedTagFilters({selected, onChange, maxTime, onMaxTimeChange, maxCalories, onMaxCaloriesChange, onClearAll}: CuratedTagFiltersProps) {
  const [isMobile, setIsMobile] = useState(false)
  const [expanded, setExpanded] = useState(true)

  useEffect(() => {
    const mq = window.matchMedia(MOBILE_MQ)
    const sync = () => {
      const mobile = mq.matches
      setIsMobile(mobile)
      setExpanded(!mobile)
    }
    sync()
    mq.addEventListener("change", sync)
    return () => mq.removeEventListener("change", sync)
  }, [])

  const toggle = (tag: string) => {
    if (selected.includes(tag)) {
      onChange(selected.filter(t => t !== tag))
    } else {
      onChange([...selected, tag])
    }
  }

  const clearAll = () => {
    if (onClearAll) {
      onClearAll()
      return
    }
    onChange([])
    onMaxTimeChange?.(undefined)
    onMaxCaloriesChange?.(undefined)
  }

  const hasAnyFilter = selected.length > 0 || maxTime != null || maxCalories != null
  const showBody = !isMobile || expanded

  return (
    <div className={[
      "filter_panel",
      isMobile && !expanded ? "filter_panel--collapsed" : "",
      isMobile ? "filter_panel--mobile" : "",
    ].filter(Boolean).join(" ")}>
      {isMobile ? (
        <button
          type="button"
          className="filter_panel__toggle"
          aria-expanded={expanded}
          onClick={() => setExpanded((v) => !v)}
        >
          <h3 className="filter_panel__title">Filters</h3>
          <i
            className={`fa-solid fa-chevron-down filter_panel__chevron${expanded ? " filter_panel__chevron--open" : ""}`}
            aria-hidden="true"
          />
        </button>
      ) : (
        <h3 className="filter_panel__title">Filters</h3>
      )}

      {showBody && (
        <div className="filter_panel__body">
          {/* dietary */}
          <div className="filter_section filter_section--dietary">
            <p className="filter_section__label">Dietary</p>
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

          {/* meal type */}
          <div className="filter_section filter_section--meal">
            <p className="filter_section__label">Meal Type</p>
            {MEAL_TAGS.map((tag) => (
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
            <div className="filter_section filter_section--time">
              <p className="filter_section__label">Max Cook Time (min)</p>
              <div className="filter_slider_row">
                <div className="filter_slider_wrapper">
                  <input type="range" min={1} max={240} step={1} value={maxTime ?? 240}
                    onChange={(e) => {
                      const val = Number(e.target.value)
                      onMaxTimeChange(val)
                    }}
                    className="filter_slider"
                  />
                  <div className="filter_slider_labels_row">
                    <span className="slider-min">1</span>
                    <span className="slider-max">240</span>
                  </div>
                </div>
                <input
                  type="number"
                  min={1}
                  max={240}
                  step={1}
                  value={maxTime ?? ""}
                  placeholder="240"
                  onChange={(e) => {
                    const val = e.target.value ? Number(e.target.value) : undefined
                    onMaxTimeChange(val)
                  }}
                  className="filter_number_input"
                />
                <span className="filter_unit"></span>
              </div>
            </div>
          )}

          {/* calories slider */}
          {onMaxCaloriesChange && (
            <div className="filter_section filter_section--calories">
              <p className="filter_section__label">Max Calories (kcal)</p>
              <div className="filter_slider_row">
                <div className="filter_slider_wrapper">
                  <input type="range" min={5} max={2000} step={5} value={maxCalories ?? 2000}
                    onChange={(e) => {
                      const val = Number(e.target.value)
                      onMaxCaloriesChange?.(val)
                    }}
                    className="filter_slider"
                  />
                  <div className="filter_slider_labels_row">
                    <span className="slider-min">5</span>
                    <span className="slider-max">2000</span>
                  </div>
                </div>
                <input
                  type="number"
                  min={5}
                  max={2000}
                  step={10}
                  value={maxCalories ?? ""}
                  placeholder="2000"
                  onChange={(e) => {
                    const val = e.target.value ? Number(e.target.value) : undefined
                    onMaxCaloriesChange(val)
                  }}
                  className="filter_number_input"
                />
                <span className="filter_unit"></span>
              </div>
            </div>
          )}

          {hasAnyFilter && (
            <button type="button" onClick={clearAll} className="filter_clear_btn">
              Clear Filters
            </button>
          )}
        </div>
      )}
    </div>
  )
}
