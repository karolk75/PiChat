interface ConnectionStatusProps {
  status: 'connecting' | 'connected' | 'disconnected' | 'failed';
}

export function ConnectionStatus({ status }: ConnectionStatusProps) {
  if (status === 'connected') return null;

  return (
    <div className="fixed top-0 left-0 right-0 bg-yellow-500 text-black p-2 text-center">
      {status === 'connecting' ? "Connecting to server..." : "Connection lost. Attempting to reconnect..."}
    </div>
  );
} 