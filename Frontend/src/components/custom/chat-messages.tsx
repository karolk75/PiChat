import { message } from "@/interfaces/interfaces";
import { useScrollToBottom } from '@/components/custom/use-scroll-to-bottom';
import { PreviewMessage, ThinkingMessage } from '@/components/custom/message';
import { Overview } from '@/components/custom/overview';

interface ChatMessagesProps {
  messages: message[];
  isLoading: boolean;
}

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>();

  return (
    <div className="flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4" ref={messagesContainerRef}>
      {messages.length === 0 && <Overview />}
      {messages.map((message, index) => (
        <PreviewMessage key={index} message={message} />
      ))}
      {isLoading && <ThinkingMessage />}
      <div ref={messagesEndRef} className="shrink-0 min-w-[24px] min-h-[24px]"/>
    </div>
  );
} 