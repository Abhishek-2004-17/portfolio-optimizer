import { useState, useRef, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, Search, Loader2 } from 'lucide-react';
import { searchTickers } from '@/api/dataApi';

interface Ticker {
  symbol: string;
  name: string;
  exchange: string | null;
}

interface Props {
  value: string;
  onChange: (value: string) => void;
  onRemove?: () => void;
  showRemove?: boolean;
  placeholder?: string;
  className?: string;
}

// Debounce hook for search queries
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export function TickerInput({ value, onChange, onRemove, showRemove, placeholder = 'e.g. AAPL', className = '' }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState(value);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const debouncedQuery = useDebounce(query, 300);

  // Fetch tickers from API
  const { data: results = [], isLoading } = useQuery({
    queryKey: ['tickers', 'search', debouncedQuery],
    queryFn: () => searchTickers(debouncedQuery),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: debouncedQuery.length >= 0,
  });

  useEffect(() => {
    setQuery(value);
  }, [value]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = useCallback((symbol: string) => {
    onChange(symbol);
    setQuery(symbol);
    setIsOpen(false);
    setSelectedIndex(-1);
  }, [onChange]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, results.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < results.length) {
          handleSelect(results[selectedIndex].symbol);
        } else if (query.trim()) {
          handleSelect(query.trim().toUpperCase());
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  return (
    <div className={`relative ${className}`}>
      <div className="relative flex items-center">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value.toUpperCase());
            setIsOpen(true);
            setSelectedIndex(-1);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          onBlur={() => {
            setTimeout(() => setIsOpen(false), 200);
          }}
          className="flex-1 bg-panel-light border border-panel-light rounded-lg px-3 py-2 pr-8 text-sm focus:outline-none focus:border-brand-500"
          placeholder={placeholder}
          autoComplete="off"
        />
        {isLoading && query && (
          <Loader2 size={14} className="absolute right-8 text-muted animate-spin" />
        )}
        {query && !isLoading && (
          <button
            type="button"
            onClick={() => {
              setQuery('');
              onChange('');
            }}
            className="absolute right-6 text-muted hover:text-foreground transition-colors"
          >
            <X size={14} />
          </button>
        )}
        <Search size={14} className="absolute right-2.5 text-muted pointer-events-none" />
      </div>

      {isOpen && results.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-panel border border-panel-light rounded-lg shadow-lg max-h-64 overflow-y-auto"
        >
          {results.map((ticker, index) => (
            <button
              type="button"
              key={ticker.symbol}
              onClick={() => handleSelect(ticker.symbol)}
              className={`w-full px-3 py-2 text-left text-sm hover:bg-panel-light transition-colors flex items-center justify-between ${
                index === selectedIndex ? 'bg-panel-light' : ''
              }`}
            >
              <div className="flex items-center gap-2 overflow-hidden">
                <span className="font-mono font-medium text-brand-400 shrink-0">{ticker.symbol}</span>
                <span className="text-muted text-xs truncate">{ticker.name}</span>
                {ticker.exchange && (
                  <span className="text-muted text-[10px] uppercase shrink-0">{ticker.exchange}</span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}

      {isOpen && query && !isLoading && results.length === 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-panel border border-panel-light rounded-lg shadow-lg p-3"
        >
          <p className="text-sm text-muted text-center">
            No matches found. Press{' '}
            <kbd className="px-1 bg-panel-light rounded text-xs">
              Enter
            </kbd>{' '}
            to use "{query.trim().toUpperCase()}"
          </p>
        </div>
      )}
    </div>
  );
}
