import { ChatInput } from "@/components/custom/chatinput";

interface ChatInputContainerProps {
  question: string;
  setQuestion: (value: string) => void;
  onSubmit: (text?: string) => void;
  isLoading: boolean;
  showSuggestions: boolean;
  setShowSuggestions: (value: boolean) => void;
}

export function ChatInputContainer({
  question,
  setQuestion,
  onSubmit,
  isLoading,
  showSuggestions,
  setShowSuggestions
}: ChatInputContainerProps) {
  return (
    <div className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
      <ChatInput  
        question={question}
        setQuestion={setQuestion}
        onSubmit={onSubmit}
        isLoading={isLoading}
        showSuggestions={showSuggestions}
        setShowSuggestions={setShowSuggestions}
      />
    </div>
  );
} 