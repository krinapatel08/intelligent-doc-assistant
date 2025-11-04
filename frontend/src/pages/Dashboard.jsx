import { useState, useEffect } from "react";
import { toast } from "sonner";
import { FileUpload } from "./FileUpload";
import { ChatWindow } from "./ChatWindow";

import { authService, documentService, chatService } from "@/services/api";


export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load documents
  const loadDocs = async () => {
    const token = authService.getToken();
    if (!token) return;
    const res = await documentService.list(token);
    if (res.data) setDocuments(res.data.documents);
    else toast.error(res.error || "Error loading documents");
  };

  useEffect(() => {
    loadDocs();
  }, []);

  // Load chat history when doc selected
  const loadHistory = async (id) => {
    const token = authService.getToken();
    const res = await chatService.getHistory(id, token);
    if (res.data) setMessages(res.data.messages);
  };

  // Upload new document
  const handleUpload = async (file) => {
    const token = authService.getToken();
    const res = await documentService.upload(file, token);
    if (res.data) {
      toast.success("Document uploaded!");
      await loadDocs();
      setSelectedDoc(res.data.document_id);
    } else toast.error(res.error || "Upload failed");
  };

  // Send message to backend
  const handleSend = async (text) => {
    if (!selectedDoc) return toast.error("Select a document first");
    const token = authService.getToken();
    const userMsg = { role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);
    const res = await chatService.ask(selectedDoc, text, token);
    setLoading(false);
    if (res.data?.answer) {
      setMessages((m) => [...m, { role: "assistant", content: res.data.answer }]);
    } else toast.error(res.error || "Error fetching answer");
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 p-4 space-y-4 border-r border-gray-700">
        <h2 className="text-lg font-bold mb-3">📚 Documents</h2>
        <button
          onClick={() => setSelectedDoc(null)}
          className="w-full bg-blue-600 hover:bg-blue-700 rounded py-2 mb-2"
        >
          + New Chat
        </button>

        <div className="space-y-2 max-h-[70vh] overflow-y-auto">
          {documents.map((d) => (
            <div
              key={d.id}
              onClick={() => {
                setSelectedDoc(d.id);
                loadHistory(d.id);
              }}
              className={`cursor-pointer p-2 rounded ${
                selectedDoc === d.id
                  ? "bg-blue-700 text-white"
                  : "bg-gray-700 hover:bg-gray-600"
              }`}
            >
              {d.name}
            </div>
          ))}
        </div>

        <FileUpload onUpload={handleUpload} />
      </div>

      {/* Chat Window */}
      <div className="flex-1 flex flex-col">
        <header className="p-4 border-b border-gray-700 text-lg font-semibold">
          Document Assistant
        </header>
        <ChatWindow
          messages={messages}
          onSendMessage={handleSend}
          isLoading={loading}
        />
      </div>
    </div>
  );
}
