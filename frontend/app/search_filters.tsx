"use client"

type filters = {
    // true, false checkbox
    vegetarian: boolean, vegan: boolean, gluten_free: boolean, 

    // sliders
    max_time: number | null,    // only increments of 15 min
    min_calories: number | null, max_calories: number | null, sort: string}

type search_filters_props = {
    filters: filters
    onChange: (filters: filters) => void
    res_count: number
}

function filter_section({

})

function ({
    
})

export default function search_filters({filters, onChange, res_count}: search_filters_props) {
    // change 1 filter while keeping others constant
    function update(key: keyof filters, value: any) {
        onChange({ ...filters, [key]: value })
    }
    
    // make all filters default again
    function clearAll() {
        onChange({vegetarian: false, vegan: false, gluten_free: false, max_time: null, min_calories: null,
                  max_calories: null, sort: "relevance"})
    }

    const has_active_filters = filters.vegetarian || filters.vegan || filters.gluten_free || filters.max_time !== null ||
                               filters.min_calories !== null || filters.max_calories !== null

    
    return (
        <aside className="filter_sidebar">

            {/* header */}
            <div className="header">
                <span className="filters_title">Filters</span>
                
                {has_active_filters && (
                    <button onClick={clearAll} className="filter_btn">Clear all</button>
                )}
            </div>

            {/* result count */}
            <p className="res_count">
                {res_count} recipe{res_count !== 1 ? "s" : ""}      {/* plural if 0 or > 1 recipes */}
            </p>
                    
            {/* sort */}
            <filter_section title="Sort by">
                <select
                value={filters.sort}
                onChange={e => update("sort", e.target.value)}
                style={{width: "100%", fontSize: "13px", padding: "7px 10px", borderRadius: "8px", border: "1px solid #ddd",
                        background: "white", cursor: "pointer"}}
                >
                <option value="relevance">Best match</option>
                <option value="quickest">Quickest first</option>
                <option value="newest">Newest first</option>
                <option value="calories_asc">Lowest calories</option>
                <option value="calories_desc">Highest calories</option>
                </select>
            </FilterSection>
            

        </aside>
    )
}