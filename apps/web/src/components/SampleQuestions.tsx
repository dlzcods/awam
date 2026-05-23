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
    <div className="flex flex-col items-center gap-4 px-4">
      <p className="text-sm text-[#6b7280]">Atau mulai dari sini:</p>
      <div className="flex flex-wrap justify-center gap-2 max-w-2xl">
        {SAMPLE_QUESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => onSelect(question)}
            className="text-left text-sm px-3 py-2 border border-[#e5e7eb] rounded-lg text-[#1a1a1a] hover:border-[#2c5f6e] hover:text-[#2c5f6e] transition-colors cursor-pointer bg-white"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}
