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
        className="flex items-center gap-1.5 text-xs text-[#6b7280] hover:text-[#1a1a1a] transition-colors cursor-pointer"
      >
        <ChevronDown
          className={`size-3.5 transition-transform ${open ? 'rotate-180' : ''}`}
        />
        <span>Lihat reformulasi query</span>
      </button>
      {open && (
        <div className="text-sm space-y-1.5 pt-2 pl-5">
          <div>
            <span className="font-medium text-[#1a1a1a]">Query Asli: </span>
            <span className="text-[#6b7280]">{originalQuery}</span>
          </div>
          <div>
            <span className="font-medium text-[#1a1a1a]">Query Hukum: </span>
            <span className="text-[#6b7280]">
              {reformulatedQuery || 'N/A'}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
