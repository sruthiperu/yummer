"use client"

export default function SearchIngredientsCTA() {
  function goToSearch() {
    const el = document.getElementById("home-search")
    el?.scrollIntoView({ behavior: "smooth", block: "center" })
    el?.querySelector<HTMLInputElement>("input")?.focus()
  }

  return (
    <section className="search_cta">
      <div className="search_cta_row">
        <p className="search_cta_text">
          Search by ingredients to view more recipes
        </p>
        <button type="button" onClick={goToSearch} className="search_cta_arrow" aria-label="Scroll to search bar">
          <i className="fa-solid fa-arrow-up" />
        </button>
      </div>
    </section>
  )
}