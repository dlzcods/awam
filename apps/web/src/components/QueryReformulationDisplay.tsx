import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

interface QueryReformulationDisplayProps {
  originalQuery: string
  reformulatedQuery: string
}

export function QueryReformulationDisplay({
  originalQuery,
  reformulatedQuery,
}: QueryReformulationDisplayProps) {
  const [open, setOpen] = useState(false)

  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-xs text-muted hover:text-foreground
                   transition-colors cursor-pointer py-1"
      >
        <ChevronDown
          className={`size-3.5 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
        <span>Lihat reformulasi query</span>
      </button>
      {open && (
        <div className="text-sm space-y-1.5 pt-2 pl-5 animate-slide-up">
          <div>
            <span className="font-medium text-foreground">Query Asli: </span>
            <span className="text-muted">{originalQuery}</span>
          </div>
          <div>
            <span className="font-medium text-foreground">Query Hukum: </span>
            <span className="text-muted">{reformulatedQuery || 'N/A'}</span>
          </div>
        </div>
      )}
    </div>
  )
}