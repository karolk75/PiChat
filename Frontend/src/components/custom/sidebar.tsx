import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { MessageCircle, PlusCircle, Trash2 } from "lucide-react";
import { useState } from "react";
import { CreateChatModal } from "./create-chat-modal";

// Interface for chat object
export interface Chat {
  id: string;
  name: string;
  active: boolean;
}

interface SidebarProps {
  isOpen: boolean;
  onDeleteChat?: (chatId: string) => void;
  onSelectChat: (chatId: string | null) => void;
  onCreateChat: (name: string) => void;
  currentChatId: string | null;
  chats: Chat[];
}

export function Sidebar({
  isOpen,
  onDeleteChat,
  onSelectChat,
  onCreateChat,
  currentChatId,
  chats,
}: SidebarProps) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const selectChat = (chatId: string) => {
    onSelectChat(chatId);
  };

  const handleDeleteChat = (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation();
    if (onDeleteChat) {
      onDeleteChat(chatId);
    }
  };

  const handleCreateChat = (name: string) => {
    onCreateChat(name);
  };

  return (
    <>
      <div
        className={cn(
          "fixed inset-y-0 left-0 w-64 bg-background border-r transform transition-transform duration-200 ease-in-out z-50",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Chats</h2>
          </div>

          <Button
            onClick={() => setIsCreateModalOpen(true)}
            className="mb-4 flex items-center gap-2"
            variant="outline"
          >
            <PlusCircle className="h-4 w-4" />
            New Chat
          </Button>

          <ScrollArea className="flex-1">
            <div className="space-y-2">
              {chats.map((chat) => (
                <div key={chat.id} className="group relative">
                  <Button
                    variant={chat.id === currentChatId ? "secondary" : "ghost"}
                    className="w-full justify-start gap-2 pr-8"
                    onClick={() => selectChat(chat.id)}
                  >
                    <MessageCircle className="h-4 w-4" />
                    {chat.name}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => handleDeleteChat(e, chat.id)}
                  >
                    <Trash2 className="h-4 w-4 text-primary" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      <CreateChatModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreateChat={handleCreateChat}
      />
    </>
  );
}
