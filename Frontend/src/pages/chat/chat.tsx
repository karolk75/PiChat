import { useState, useEffect } from "react";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Header } from "@/components/custom/header";
import { Sidebar } from "@/components/custom/sidebar";
import { NewChatPrompt } from "@/components/custom/new-chat-prompt";
import { CreateChatModal } from "@/components/custom/create-chat-modal";
import { ConnectionStatus } from "@/components/custom/connection-status";
import { ChatMessages } from "@/components/custom/chat-messages";
import { ChatInputContainer } from "@/components/custom/chat-input-container";
import { useWebSocket } from "@/context/WebsocketContext";
import { useChats } from "@/hooks/useChats";
import { useMessages } from "@/hooks/useMessages";

export function Chat() {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false);
  
  const { connectionStatus } = useWebSocket();
  const {
    chats,
    currentChatId,
    handleSelectChat,
    handleCreateChat,
    handleDeleteChat
  } = useChats();
  
  const {
    messages,
    question,
    setQuestion,
    isLoading,
    showSuggestions,
    setShowSuggestions,
    handleSubmit,
    clearMessages
  } = useMessages(currentChatId);

  // Clear messages when chat changes
  useEffect(() => {
    if (!currentChatId) {
      clearMessages();
    }
  }, [currentChatId, clearMessages]);

  return (
    <div className={`flex flex-col min-w-0 h-dvh bg-background transition-all duration-200 ${sidebarOpen ? 'pl-64' : ''}`}>
      <div className="flex items-center">
        <Button 
          variant="ghost" 
          className="ml-2" 
          size="icon" 
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          <Menu className="h-5 w-5" />
        </Button>
        <Header />
      </div>
      
      <Sidebar 
        isOpen={sidebarOpen}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        onCreateChat={handleCreateChat}
        currentChatId={currentChatId}
        chats={chats}
      />
      
      <ConnectionStatus status={connectionStatus} />
      
      {currentChatId ? (
        <>
          <ChatMessages 
            messages={messages}
            isLoading={isLoading}
          />
          <ChatInputContainer
            question={question}
            setQuestion={setQuestion}
            onSubmit={handleSubmit}
            isLoading={isLoading}
            showSuggestions={showSuggestions}
            setShowSuggestions={setShowSuggestions}
          />
        </>
      ) : (
        <div className="flex-1">
          <NewChatPrompt onCreateChat={() => setIsCreateModalOpen(true)} />
        </div>
      )}
      
      <CreateChatModal 
        isOpen={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)} 
        onCreateChat={handleCreateChat}
      />
    </div>
  );
}