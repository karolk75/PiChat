import { Button } from "@/components/ui/button";
import { PlusCircle } from "lucide-react";

interface NewChatPromptProps {
  onCreateChat: () => void;
}

export function NewChatPrompt({ onCreateChat }: NewChatPromptProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4 p-8 text-center">
      <div className="rounded-full bg-muted p-3">
        <PlusCircle className="h-8 w-8" />
      </div>
      <h3 className="font-semibold text-xl">No chat selected</h3>
      <p className="text-muted-foreground mb-2">
        Create a new chat or select an existing one from the sidebar to get started.
      </p>
      <Button onClick={onCreateChat} className="gap-2">
        <PlusCircle className="h-4 w-4" />
        New Chat
      </Button>
    </div>
  );
} 