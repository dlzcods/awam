interface SampleQuestionsProps {
  onSelect: (question: string) => void
}

const SAMPLE_QUESTIONS = [
  'Kalau tetangga bangun rumah lewat batas tanah gue, bisa dituntut gak?',
  'Gimana cara bikin PT untuk usaha kecil?',
  'Hak karyawan kontrak kalau di-PHK sepihak apa aja sih?',
  'Kalau beli barang online terus barangnya gak sesuai, bisa minta refund gak?',
  'Syarat nikah beda agama di Indonesia gimana ya?',
]

export function SampleQuestions({ onSelect }: SampleQuestionsProps) {
  return (
    <div className="flex flex-col items-center gap-4 px-4 py-2 animate-fade-in">
      <p className="text-sm text-muted">Atau mulai dari sini:</p>
      <div className="flex flex-wrap justify-center gap-2 max-w-2xl">
        {SAMPLE_QUESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => onSelect(question)}
            className="text-left text-sm px-4 py-2.5 border border-border rounded-xl
                       text-foreground bg-card hover:border-brand hover:text-brand
                       active:scale-[0.98] transition-all cursor-pointer
                       min-h-[44px]"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}