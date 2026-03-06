interface ErrorMessageProps {
  message: string | any;
}

export default function ErrorMessage({ message }: ErrorMessageProps) {
  if (!message) return null;

  const baseClasses = "bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4";

  if (typeof message === 'string') {
    return (
      <div className={baseClasses}>
        <p className="text-sm">{message}</p>
      </div>
    );
  }

  if (Array.isArray(message)) {
    return (
      <div className={baseClasses}>
        {message.map((err, idx) => (
          <p key={idx} className="text-sm mb-1">
            {err.msg || JSON.stringify(err)}
          </p>
        ))}
      </div>
    );
  }

  if (typeof message === 'object') {
    return (
      <div className={baseClasses}>
        <p className="text-sm">{message.msg || message.detail || JSON.stringify(message)}</p>
      </div>
    );
  }

  return null;
}
