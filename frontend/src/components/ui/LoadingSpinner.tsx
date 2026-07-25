// src/components/ui/LoadingSpinner.tsx

function LoadingSpinner({ message = "Processing your request..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 gap-4">
      <div className="w-10 h-10 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin" />
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  )
}

export default LoadingSpinner