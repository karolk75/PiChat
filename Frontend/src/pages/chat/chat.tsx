import { ChatInput } from "@/components/custom/chatinput";
import { PreviewMessage, ThinkingMessage } from "../../components/custom/message";
import { useScrollToBottom } from '@/components/custom/use-scroll-to-bottom';
import { useState, useRef, useEffect } from "react";
import { message } from "../../interfaces/interfaces"
import { Overview } from "@/components/custom/overview";
import { Header } from "@/components/custom/header";
import { Sidebar, Chat as ChatType } from "@/components/custom/sidebar";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { v4 as uuidv4 } from 'uuid';
import { NewChatPrompt } from "@/components/custom/new-chat-prompt";
import { CreateChatModal } from "@/components/custom/create-chat-modal";
import { ChatService, MessageService } from "@/service";

export function Chat() {
  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>();
  const [messages, setMessages] = useState<message[]>([]);
  const [question, setQuestion] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [showSuggestions, setShowSuggestions] = useState<boolean>(false);
  const [chats, setChats] = useState<ChatType[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false);
  
  const chatService = useRef(ChatService.getInstance());
  const messageService = useRef(MessageService.getInstance());

  // Setup event listeners
  useEffect(() => {
    const chatSvc = chatService.current;
    const msgSvc = messageService.current;
    
    // Register chat-related listeners
    const chatListCleanup = chatSvc.onChatList((chatList) => {
      setChats(chatList);
    });
    
    const newChatCleanup = chatSvc.onNewChat((chat, chatId) => {
      setChats(prev => [...prev, chat]);
      setCurrentChatId(chatId);
      setMessages([]);
    });
    
    const chatDeletedCleanup = chatSvc.onChatDeleted((chatId) => {
      setChats(prev => prev.filter(chat => chat.id !== chatId));
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
      }
    });
    
    // Register message-related listeners
    const chatHistoryCleanup = msgSvc.onChatHistory((messageHistory) => {
      setMessages(messageHistory);
    });
    
    const messageCleanup = msgSvc.onMessage((content, traceId, end) => {
      setIsLoading(false);
      
      if (content === "[END]" && end) {
        return;
      }
      
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        const isAppending = lastMessage?.role === "assistant" && lastMessage.id === traceId;
        
        if (isAppending) {
          const updatedMessages = [...prev];
          updatedMessages[prev.length - 1] = {
            ...lastMessage,
            content: lastMessage.content + content
          };
          return updatedMessages;
        } else {
          return [
            ...prev,
            { content, role: "assistant", id: traceId }
          ];
        }
      });
    });
    
    const textMessageCleanup = msgSvc.onTextMessage((text) => {
      if (text === "[END]") {
        setIsLoading(false);
        return;
      }
      
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        if (lastMessage?.role === "assistant") {
          const updatedMessages = [...prev];
          updatedMessages[prev.length - 1] = {
            ...lastMessage,
            content: lastMessage.content + text
          };
          return updatedMessages;
        } else {
          const traceId = uuidv4();
          return [...prev, { content: text, role: "assistant", id: traceId }];
        }
      });
    });
    
    // Request initial chat list
    chatSvc.getChats();
    
    // If a chat ID is selected, load its messages
    if (currentChatId) {
      msgSvc.getChatHistory(currentChatId);
    }
    
    // Cleanup listeners on unmount
    return () => {
      chatListCleanup();
      newChatCleanup();
      chatDeletedCleanup();
      chatHistoryCleanup();
      messageCleanup();
      textMessageCleanup();
    };
  }, [currentChatId]);

  useEffect(() => {
    if (messages.length > 0) {
      setShowSuggestions(false);
    } else {
      setShowSuggestions(true);
    }
  }, [messages]);

  async function handleSubmit(text?: string) {
    if (isLoading) return;
    
    // If no chat is selected, open create modal
    if (!currentChatId) {
      setIsCreateModalOpen(true);
      return;
    }

    const messageText = text || question;
    if (!messageText.trim()) return;
    
    setIsLoading(true);
    
    // Add user message to state immediately
    const traceId = messageService.current.sendMessage(currentChatId, messageText);
    setMessages(prev => [...prev, { content: messageText, role: "user", id: traceId }]);
    
    setQuestion("");
  }

  const handleSelectChat = (chatId: string | null) => {
    if (currentChatId === chatId) {
      setCurrentChatId(null);
      setMessages([]);
    } else if (chatId) {
      setCurrentChatId(chatId);
      messageService.current.getChatHistory(chatId);
    } else {
      setCurrentChatId(null);
      setMessages([]);
    }
  };

  const handleCreateChat = (name: string) => {
    chatService.current.createChat(name);
  };

  const handleDeleteChat = (chatId: string) => {
    chatService.current.deleteChat(chatId);
  };

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
        <Header/>
      </div>
      <Sidebar 
        isOpen={sidebarOpen} 
        onDeleteChat={handleDeleteChat}
        onSelectChat={handleSelectChat}
        onCreateChat={handleCreateChat}
        currentChatId={currentChatId}
        chats={chats}
      />
      
      {currentChatId ? (
        <>
          <div className="flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4" ref={messagesContainerRef}>
            {messages.length === 0 && <Overview />}
            {messages.map((message, index) => (
              <PreviewMessage key={index} message={message} />
            ))}
            {isLoading && <ThinkingMessage />}
            <div ref={messagesEndRef} className="shrink-0 min-w-[24px] min-h-[24px]"/>
          </div>
          <div className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
            <ChatInput  
              question={question}
              setQuestion={setQuestion}
              onSubmit={handleSubmit}
              isLoading={isLoading}
              showSuggestions={showSuggestions}
              setShowSuggestions={setShowSuggestions}
            />
          </div>
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
};