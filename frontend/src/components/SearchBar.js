/**
 * SearchBar Component - Search input with clear button
 */
import React from 'react';
import './SearchBar.css';

function SearchBar({
  value,
  onChange,
  placeholder = 'Search...',
  onClear,
  disabled = false
}) {
  const handleClear = () => {
    onChange('');
    if (onClear) onClear();
  };

  return (
    <div className="search-bar">
      <span className="search-icon">🔍</span>
      <input
        type="text"
        className="search-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
      />
      {value && (
        <button
          className="search-clear"
          onClick={handleClear}
          aria-label="Clear search"
        >
          ×
        </button>
      )}
    </div>
  );
}

export default SearchBar;
