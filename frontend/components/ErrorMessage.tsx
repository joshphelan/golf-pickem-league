interface ErrorMessageProps {
  message: string | any;
}

export default function ErrorMessage({ message }: ErrorMessageProps) {
  if (!message) return null;

  // Handle string errors
  if (typeof message === 'string') {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
        <p className="text-sm">{message}</p>
      </div>
    );
  }

  // Handle structured errors (Pydantic validation errors)
  if (Array.isArray(message)) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
        {message.map((err, idx) => (
          <p key={idx} className="text-sm mb-1">
            {err.msg || JSON.stringify(err)}
          </p>
        ))}
      </div>
    );
  }

  // Handle object errors
  if (typeof message === 'object') {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
        <p className="text-sm">{message.msg || message.detail || JSON.stringify(message)}</p>
      </div>
    );
  }

  return null;
}

